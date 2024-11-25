from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

from rantr.rants.models import Rant
from rantr.comments.models import Comment
from rantr.notifications.models import Notification


@login_required
def add_comment(request, slug):
    if request.method == 'POST':
        rant = get_object_or_404(Rant, slug=slug)
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
                    target_object_id=rant.id,
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
    
    return redirect('rants:detail', slug=slug)
