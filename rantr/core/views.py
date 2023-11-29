from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from django.views import View
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from notifications.models import Notification

from rantr.rants.models import Rant
from rantr.users.models import User


@login_required
def search(request):
    query = request.GET.get('q')

    rant_results = []
    user_results = []

    if query:
        # Search for rants and users using PostgreSQL full-text search and icontains
        rant_results = Rant.objects.annotate(
            search=SearchVector('content'),
        ).filter(Q(search=SearchQuery(query)) | Q(content__icontains=query))

        user_results = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

    context = {
        'query': query,
        'rant_results': rant_results,
        'user_results': user_results,
    }

    return render(request, 'core/search_results.html', context)


class UnreadNotificationsList(ListView):  
    model = Notification 
    queryset = Notification.objects.filter(unread=True)
    template_name = 'notifications/unread_list.html'

    def get_queryset(self):
        # Filter unread notifications for the logged-in user
        return Notification.objects.filter(recipient=self.request.user, unread=True)


class MarkNotificationAsReadView(View):
    def get(self, request, notification_id):
        notification = get_object_or_404(Notification, id=notification_id)
        notification.mark_as_read()
        return redirect('core:unread')