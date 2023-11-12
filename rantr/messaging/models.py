from django.urls import reverse
from django.db import models
from django.contrib.auth import get_user_model

from model_utils.models import TimeStampedModel
from model_utils.fields import UUIDField

from rantr.messaging.managers import ConversationManager

User = get_user_model()


class Conversation(TimeStampedModel):
    participants = models.ManyToManyField(User, related_name='conversations')

    objects = ConversationManager()

    def get_absolute_url(self):
        return reverse("messaging:conversation_detail", kwargs={"pk": self.id})

    def __str__(self):
        return " and ".join(participant.username for participant in self.participants.all())


class Message(TimeStampedModel):
    uuid = UUIDField(primary_key=True, version=4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    
    def get_absolute_url(self):
        return reverse("messaging:conversation_detail", kwargs={"pk": self.conversation.id})