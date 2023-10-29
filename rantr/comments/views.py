from django.shortcuts import redirect, get_object_or_404
from rantr.comments.models import Comment
from rantr.rants.models import Rant


def add_comment(request, rant_uuid):
    rant = get_object_or_404(Rant, uuid=rant_uuid)

    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        parent = None

        if parent_id:
            parent = get_object_or_404(Comment, pk=parent_id)

        comment = Comment.objects.create(
            rant=rant,
            user=request.user,
            content=content,
            parent=parent,
        )

    return redirect('rants:detail', rant.uuid)
