from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from model_utils.models import TimeStampedModel
from model_utils.fields import UUIDField

User = get_user_model()


class Conversation(TimeStampedModel):
    uuid = UUIDField(primary_key=True, version=4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')

    def get_absolute_url(self):
        return reverse('conversations:conversation_detail', args=[str(self.uuid)])


class Message(TimeStampedModel):
    uuid = UUIDField(primary_key=True, version=4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()