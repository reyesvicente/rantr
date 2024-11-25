from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from django.views import View
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import transaction
from django.http import JsonResponse

from notifications.models import Notification

from rantr.rants.models import Rant
from rantr.users.models import User


@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)
    cache_key = f'search_results_{query}_{page}_{request.user.id}'
    
    # Try to get cached results
    cached_results = cache.get(cache_key)
    if cached_results and not request.GET.get('nocache'):
        return render(request, 'core/search_results.html', cached_results)

    rant_results = []
    user_results = []

    if query:
        # Create search vector with weights
        search_vector = (
            SearchVector('content', weight='A') +
            SearchVector('user__username', weight='B')
        )
        search_query = SearchQuery(query)

        # Search for rants using PostgreSQL full-text search with ranking
        rant_results = Rant.objects.annotate(
            rank=SearchRank(search_vector, search_query),
            search=search_vector,
        ).filter(
            Q(search=search_query) |
            Q(content__icontains=query)
        ).order_by('-rank', '-created')

        # Search for users with ranking
        user_results = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(bio__icontains=query)
        ).annotate(
            rank=SearchRank(
                SearchVector('username', weight='A') +
                SearchVector('first_name', 'last_name', weight='B') +
                SearchVector('bio', weight='C'),
                search_query
            )
        ).order_by('-rank')

    # Paginate results
    rants_paginator = Paginator(rant_results, 20)
    users_paginator = Paginator(user_results, 20)

    context = {
        'query': query,
        'rant_results': rants_paginator.get_page(page),
        'user_results': users_paginator.get_page(page),
        'is_paginated': rants_paginator.num_pages > 1 or users_paginator.num_pages > 1,
    }

    # Cache results for 10 minutes
    cache.set(cache_key, context, 60 * 10)

    return render(request, 'core/search_results.html', context)


class UnreadNotificationsList(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/unread_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return (
            Notification.objects.filter(recipient=self.request.user, unread=True)
            .select_related('actor', 'target')
            .order_by('-timestamp')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = (
            Notification.objects.filter(recipient=self.request.user, unread=True)
            .count()
        )
        return context


class MarkNotificationAsReadView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, notification_id=None):
        if notification_id:
            # Mark single notification as read
            notification = get_object_or_404(
                Notification,
                id=notification_id,
                recipient=request.user
            )
            notification.mark_as_read()
        else:
            # Mark all as read
            Notification.objects.filter(
                recipient=request.user,
                unread=True
            ).update(unread=False)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        
        return redirect('core:unread')