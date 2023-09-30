from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from rantr.friends.models import UserFollow

User = get_user_model()


def follow_user(request, username):
    followed_user = User.objects.get(username=username)
    UserFollow.objects.create(
        user=request.user,
        followed_user=followed_user
    )
    return redirect('users:detail', username=followed_user.username) 


def unfollow_user(request, username):
    followed_user = User.objects.get(username=username)
    UserFollow.objects.filter(
        user=request.user, 
        followed_user=followed_user
    ).delete()
    return redirect('users:detail', username=followed_user.username)