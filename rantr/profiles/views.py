from django.shortcuts import render, redirect

from rantr.profiles.models import Profile
from rantr.rants.models import Rant


def dashboard(request):
    followed_rants = Rant.objects.filter(
        user__profile__in=request.user.profile.follows.all()
    ).order_by("-created")
    context = {
        'followed_rants': followed_rants,
    }
    return render(request, 'profiles/dashboard.html', context)


def profile_list(request):
    profiles = Profile.objects.exclude(user=request.user)
    context = {
        "profiles": profiles,
    }
    return render(request, 'profiles:profile_list.html', context)


def profile(request, uuid):
    profile = Profile.objects.get(uuid=uuid)
    if request.method == "POST":
        current_user_profile = request.user.profile
        data = request.POST
        action = data.get("follow")
        if action == "follow":
            current_user_profile.follows.add(profile)
        elif action == "unfollow":
            current_user_profile.follows.remove(profile)
        current_user_profile.save()
    context = {
        "profile": profile,
    }
    return render(request, 'profiles/profile.html', context)
