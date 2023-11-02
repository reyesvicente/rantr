from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch
from django.contrib.auth import get_user_model
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
        # Get rants for users that the logged in user follows
        return Rant.objects.filter(
            user__in=self.request.user.following.all()
        )


class RantListView(LoginRequiredMixin, ListView):

    model = Rant
    context_object_name = 'rants'

    def get_queryset(self):
        # Calculate popularity score for each rant and order by it
        like_weight = 4.0
        comment_weight = 5.0  # Adjust the weights based on your preference

        rants = Rant.objects.all()
        for rant in rants:
            number_of_likes = rant.likes
            number_of_comments = rant.comment_set.count()
            popularity_score = (number_of_likes * like_weight) + (number_of_comments * comment_weight)
            rant.popularity_score = popularity_score

        # Order rants by popularity score in descending order
        return rants.order_by('-popularity_score')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        # Prefetch related user
        context['rants'] = self.model.objects.prefetch_related('user')
        
        # Get likes for these rants by this user
        liked_rants = Like.objects.filter(
            user=self.request.user,
            rant__in=context['rants']
        ).values('rant').annotate(likes_count=Count('rant'))
        
        rant_map = {rant.uuid: rant for rant in context['rants']}

        for like in liked_rants:
            rant = rant_map[like['rant']]
            rant.user_liked = True
            rant.likes_count = like['likes_count']
        return context
    

class RantDetailView(DetailView):
    model = Rant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rant = context['rant']
        context['rant'] = get_object_or_404(Rant, slug=self.kwargs['slug'])
        context['likes_count'] = rant.likes

        if self.request.user.is_authenticated:
            context['user_like'] = Like.objects.filter(rant=rant, user=self.request.user).exists()
        
        return context


class RantCreateView(LoginRequiredMixin, CreateView):
    model = Rant
    fields = [
        'content',
        'image'
    ]

    def form_valid(self, form):
        form.instance.user = self.request.user
        if form.cleaned_data['image']:
            image = form.cleaned_data['image']
            form.instance.image = image
        return super().form_valid(form)
