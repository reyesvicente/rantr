from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView
from django.urls import reverse
from django.db.models import Count
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from django.contrib.auth.decorators import login_required

from rantr.rants.models import Rant

User = get_user_model()


@login_required
def follow_user(request, username):
    user = User.objects.get(username=username)
    request.user.following.add(user)
    return redirect('users:detail', username)


@login_required  
def unfollow_user(request, username):
    user = User.objects.get(username=username)
    request.user.following.remove(user)
    return redirect('users:detail', username)


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

        likes_count = viewed_user.rant_set.aggregate(total_likes=Count('like'))['total_likes']


        context['viewed_user'] = viewed_user
        context['followings'] = followings
        context['followers'] = followers
        context['followings_count'] = followings_count
        context['followers_count'] = followers_count
        context['rants'] = viewed_user.rant_set.all()
        context['likes_count'] = likes_count

        return context

user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["first_name", "last_name", 'location', "email", "profile_picture",]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert self.request.user.is_authenticated  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("rants:list", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
