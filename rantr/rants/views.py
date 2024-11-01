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
from rantr.rants.models import Rant
from rantr.likes.models import Like

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

    def get_queryset(self):
        # Use Django's ORM to calculate popularity score in the database
        like_weight = settings.LIKE_WEIGHT
        comment_weight = settings.COMMENT_WEIGHT
        impression_weight = settings.IMPRESSION_WEIGHT

        # Calculate popularity score in the database using annotate()
        return Rant.objects.annotate(
            calculated_popularity=(
                Count('likes') * like_weight +
                Count('comments') * comment_weight +  # Use 'comments' if related_name is set
                F('views') * impression_weight
            )
        ).order_by('-calculated_popularity')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user

        # Prefetch the user and filter likes from the logged-in user efficiently
        context['rants'] = self.model.objects.prefetch_related('user')
        
        # Get likes for these rants by the current user
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
        rant = context['rant']

        # Use atomic F() expression to avoid race conditions on view count increment
        rant.views = F('views') + 1
        rant.save(update_fields=['views'])

        # Fetch updated rant object after view increment
        context['rant'] = get_object_or_404(Rant, slug=self.kwargs['slug'])
        context['likes_count'] = rant.likes

        if self.request.user.is_authenticated:
            context['user_like'] = Like.objects.filter(rant=rant, user=self.request.user).exists()

        return context


class RantCreateView(LoginRequiredMixin, CreateView):
    model = Rant
    fields = ['content', 'image']

    def form_valid(self, form):
        # Assign the logged-in user to the rant
        form.instance.user = self.request.user

        # Validate and handle image uploads securely
        image = form.cleaned_data.get('image', None)
        if image:
            # Validate image file extensions
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            validator = FileExtensionValidator(allowed_extensions=valid_extensions)
            try:
                validator(image)
            except ValidationError:
                form.add_error('image', 'Invalid image format. Only jpg, jpeg, png, gif are allowed.')

            form.instance.image = image

        return super().form_valid(form)
