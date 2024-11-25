from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from notifications.signals import notify

from rantr.comments.models import Comment
from rantr.rants.models import Rant


@login_required
def add_comment(request, rant_uuid):
    if request.method == 'POST':
        rant = get_object_or_404(Rant, uuid=rant_uuid)
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if content:
            # Create the comment
            comment = Comment.objects.create(
                rant=rant,
                user=request.user,
                content=content,
                parent_id=parent_id if parent_id else None
            )
            
            # Send notification
            if request.user != rant.user:
                if parent_id:
                    parent_comment = Comment.objects.get(id=parent_id)
                    if parent_comment.user != request.user:
                        notify.send(
                            request.user,
                            recipient=parent_comment.user,
                            verb='replied to your comment',
                            action_object=comment,
                            target=rant
                        )
                else:
                    notify.send(
                        request.user,
                        recipient=rant.user,
                        verb='commented on your rant',
                        action_object=comment,
                        target=rant
                    )
            
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Comment cannot be empty!')
            
    return redirect('rants:detail', slug=rant.slug)
