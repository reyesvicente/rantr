from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.urls import reverse

from rantr.rants.models import Rant
from rantr.comments.models import Comment
from rantr.notifications.models import Notification


@login_required
def add_comment(request, rant_uuid):
    if request.method == 'POST':
        rant = get_object_or_404(Rant, uuid=rant_uuid)
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if content:
            comment = Comment.objects.create(
                user=request.user,
                rant=rant,
                content=content,
                parent_id=parent_id if parent_id else None
            )
            
            # Create notification for rant owner if commenter is not the owner
            if request.user != rant.user:
                Notification.objects.create(
                    recipient=rant.user,
                    actor=request.user,
                    verb='commented',
                    target_content_type=ContentType.objects.get_for_model(rant),
                    target_object_id=rant.uuid,
                    description=f"{request.user.username} commented on your rant"
                )
            
            # If this is a reply, also notify the parent comment's author
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                if request.user != parent_comment.user:
                    Notification.objects.create(
                        recipient=parent_comment.user,
                        actor=request.user,
                        verb='replied',
                        target_content_type=ContentType.objects.get_for_model(comment),
                        target_object_id=comment.id,
                        description=f"{request.user.username} replied to your comment"
                    )
            
            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'username': request.user.username,
                    'content': content,
                    'comment_id': comment.id,
                    'redirect_url': None  # Don't redirect for AJAX requests
                })
            
            # For non-AJAX requests, redirect to the referring page if available
            referer = request.META.get('HTTP_REFERER')
            if referer:
                return redirect(referer)
            
            # Default fallback to rant detail page
            return redirect('rants:detail', slug=rant.slug)
    
    # If not a POST request, redirect to rant detail
    return redirect('rants:detail', slug=rant.slug)
