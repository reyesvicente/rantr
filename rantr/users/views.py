from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.db.models import Count
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

from rantr.notifications.models import Notification
from rantr.rants.models import Rant

User = get_user_model()


@login_required
def follow_user(request, username):
    user = User.objects.get(username=username)
    request.user.following.add(user)
    
    # Create notification for follow
    Notification.objects.create(
        recipient=user,
        actor=request.user,
        verb='started following you',
        target_content_type=ContentType.objects.get_for_model(user),
        target_object_id=user.id,
        description=f"{request.user.username} started following you"
    )
    
    return redirect('users:detail', username)


@login_required  
def unfollow_user(request, username):
    user = User.objects.get(username=username)
    request.user.following.remove(user)
    return redirect('users:detail', username)


def user_followers(request, username):
    user = User.objects.get(username=username)
    followers = user.followers.all()
    
    context = {
        'user': user,
        'followers': followers,
    }
    
    return render(request, 'users/user_followers.html', context)


def user_following(request, username):
    user = User.objects.get(username=username)
    following = user.following.all()
    
    context = {
        'user': user,
        'following': following,
    }
    
    return render(request, 'users/user_following.html', context)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        viewed_user = self.get_object()

        followings = viewed_user.following.all()
        followers = viewed_user.followers.all()

        followings_count = followings.count()
        followers_count = followers.count()

        likes_count = viewed_user.rants.aggregate(total_likes=Count('like'))['total_likes']

        context['viewed_user'] = viewed_user
        context['followings'] = followings
        context['followers'] = followers
        context['followings_count'] = followings_count
        context['followers_count'] = followers_count
        
        # Filter rants by the viewed user and order them in descending order
        context['rants'] = viewed_user.rants.all().order_by('-created')  # Replace 'created_at' with the appropriate field for ordering
        context['likes_count'] = likes_count

        return context

user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["first_name", "last_name", 'location', "email", "profile_picture", "bio"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert self.request.user.is_authenticated  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        if 'profile_picture' in self.request.FILES:
            form.instance.profile_picture = self.request.FILES['profile_picture']
        return super().form_valid(form)

user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("rants:list", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
