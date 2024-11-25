from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.core.paginator import Paginator
from notifications.signals import notify

from rantr.likes.models import Like
from rantr.rants.models import Rant


@login_required
@transaction.atomic
def like_rant(request, slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    rant = get_object_or_404(Rant, slug=slug)
    like, created = Like.objects.get_or_create(user=request.user, rant=rant)
    
    if created:
        rant.likes = rant.likes + 1
        rant.save(update_fields=['likes'])
        rant.update_popularity_score()
        
        if request.user != rant.user:
            notify.send(
                request.user,
                recipient=rant.user,
                verb='liked your rant',
                action_object=rant,
                target=rant
            )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'liked',
                'likes_count': rant.likes
            })
    
    return redirect('rants:detail', slug=slug)


@login_required
@transaction.atomic
def unlike_rant(request, slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    rant = get_object_or_404(Rant, slug=slug)
    deleted = Like.objects.filter(user=request.user, rant=rant).delete()[0] > 0
    
    if deleted:
        rant.likes = rant.likes - 1
        rant.save(update_fields=['likes'])
        rant.update_popularity_score()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'unliked',
                'likes_count': rant.likes
            })
    
    return redirect('rants:detail', slug=slug)


@login_required
def rant_likes_list(request, slug):
    rant = get_object_or_404(Rant, slug=slug)
    likes_list = Like.objects.select_related('user').filter(rant=rant).order_by('-id')
    
    paginator = Paginator(likes_list, 50)  # Show 50 likes per page
    page = request.GET.get('page')
    likes = paginator.get_page(page)
    
    context = {
        'rant': rant,
        'likes': likes,
        'is_paginated': paginator.num_pages > 1,
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'likes/includes/likes_list.html', context)
    
    return render(request, 'likes/rants_likes_list.html', context)
