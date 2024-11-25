from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from notifications.signals import notify

from rantr.comments.models import Comment
from rantr.rants.models import Rant
from rantr.comments.serializers import CommentSerializer


@api_view(['POST'])
def add_comment(request, rant_uuid):
    rant = get_object_or_404(Rant, uuid=rant_uuid)

    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        comment = serializer.save(rant=rant, user=request.user)
        if request.user != rant.user:
            notify.send(request.user, recipient=rant.user, verb='commented on your rant', action_object=rant, target=rant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
