from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, F
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
)
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from rantr.rants.models import Rant
from rantr.likes.models import Like
from .forms import RantForm  # Assuming RantForm is defined in forms.py

User = get_user_model()


class FollowingRantsView(LoginRequiredMixin, ListView):
    template_name = 'rants/following_rants.html'
    context_object_name = 'rants'

    def get_queryset(self):
        # Fetch rants only from users that the logged-in user follows
        if not self.request.user.is_authenticated:
            return Rant.objects.none()

        # Apply additional access control if needed for following relationships
        return Rant.objects.filter(user__in=self.request.user.following.all())


class RantListView(LoginRequiredMixin, ListView):
    model = Rant
    context_object_name = 'rants'
    paginate_by = 10

    def get_queryset(self):
        # The model's Meta.ordering already handles the popularity sorting
        return Rant.objects.select_related('user').prefetch_related('comments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user_likes = Like.objects.filter(user=self.request.user, rant__in=context['rants']).values_list('rant', flat=True)
            context['user_likes'] = user_likes
        return context


class RantDetailView(DetailView):
    model = Rant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get user's like status for this rant
        if self.request.user.is_authenticated:
            context['user_like'] = Like.objects.filter(
                user=self.request.user,
                rant=self.object
            ).exists()
        
        # Get comments in threaded order
        comments = []
        # First get all top-level comments
        top_level_comments = self.object.comments.filter(parent=None).select_related('user').order_by('-created')
        
        for comment in top_level_comments:
            comments.append(comment)
            # Get replies for this comment
            replies = self.object.comments.filter(parent=comment).select_related('user').order_by('created')
            comments.extend(replies)
        
        context['comments'] = comments
        
        # Increment view count
        self.object.views += 1
        self.object.save()
        
        return context


class RantCreateView(LoginRequiredMixin, CreateView):
    model = Rant
    form_class = RantForm
    template_name = 'rants/rant_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            response = super().form_valid(form)
            return response
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('rants:detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create a New Rant'
        return context
