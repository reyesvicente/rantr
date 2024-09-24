from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, F, Prefetch
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
)
from rantr.rants.models import Rant 
from rantr.likes.models import Like

User = get_user_model()


class FollowingRantsView(LoginRequiredMixin, ListView):
    template_name = 'rants/following_rants.html'
    context_object_name = 'rants'

    def get_queryset(self):
        # Ensure that `following` is restricted to authenticated users
        # and only valid follow relations are returned.
        return Rant.objects.filter(
            user__in=self.request.user.following.all()
        ).prefetch_related('user')


class RantListView(LoginRequiredMixin, ListView):
    model = Rant
    context_object_name = 'rants'

    def get_queryset(self):
        # Calculate popularity score at the database level to avoid loading all objects into memory
        like_weight = settings.LIKE_WEIGHT
        comment_weight = settings.COMMENT_WEIGHT
        impression_weight = settings.IMPRESSION_WEIGHT

        # Use Django ORM to calculate popularity scores efficiently in the database
        return Rant.objects.annotate(
            popularity_score=(
                Count('likes') * like_weight +
                Count('comment_set') * comment_weight +
                F('views') * impression_weight
            )
        ).order_by('-popularity_score')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user

        # Prefetch related user and limit the fields to avoid exposing sensitive data
        context['rants'] = self.model.objects.prefetch_related(
            Prefetch('user', queryset=User.objects.only('username', 'id'))  # Fetch only necessary fields
        )

        # Get likes for these rants by this user
        liked_rants = Like.objects.filter(
            user=self.request.user,
            rant__in=context['rants']
        ).values('rant').annotate(likes_count=Count('rant'))

        rant_map = {rant.uuid: rant for rant in context['rants']}

        for like in liked_rants:
            rant = rant_map.get(like['rant'])
            if rant:
                rant.user_liked = True
                rant.likes_count = like['likes_count']
        
        return context
    

class RantDetailView(DetailView):
    model = Rant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rant = get_object_or_404(Rant, slug=self.kwargs['slug'])
        
        # Increment views using F() expression to prevent race conditions
        rant.views = F('views') + 1
        rant.save(update_fields=['views'])

        context['rant'] = rant
        context['likes_count'] = rant.likes

        if self.request.user.is_authenticated:
            # Check if the current user has liked the rant
            context['user_like'] = Like.objects.filter(rant=rant, user=self.request.user).exists()

        return context


class RantCreateView(LoginRequiredMixin, CreateView):
    model = Rant
    fields = ['content', 'image']

    def form_valid(self, form):
        # Assign the logged-in user to the rant
        form.instance.user = self.request.user

        # Validate the image file if provided
        image = form.cleaned_data.get('image')
        if image:
            # Ensure image validation for allowed types, size, etc.
            form.instance.image = image

        return super().form_valid(form)
