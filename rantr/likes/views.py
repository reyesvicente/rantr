from django.shortcuts import get_object_or_404, redirect, render

from notifications.signals import notify

from rantr.likes.models import Like
from rantr.rants.models import Rant


def like_rant(request, slug):
    rant = get_object_or_404(Rant, slug=slug)


    if not Like.objects.filter(user=request.user, rant=rant).exists():
        Like.objects.create(user=request.user, rant=rant)
        rant.likes += 1
        rant.save()
        if request.user != rant.user:
            notify.send(request.user, recipient=rant.user, verb='liked your rant', action_object=rant, target=rant) 
    return redirect('rants:detail', slug=slug)


def unlike_rant(request, slug):
    rant = get_object_or_404(Rant, slug=slug)
    rant.likes -= 1
    rant.save()

    Like.objects.filter(user=request.user, rant=rant).delete()

    return redirect('rants:detail', slug=slug)


def rant_likes_list(request, slug):
    rant = get_object_or_404(Rant, slug=slug)
    likes = Like.objects.filter(rant=rant)
    
    context = {
        'rant': rant,
        'likes': likes,
    }
    
    return render(request, 'likes/rants_likes_list.html', context)

