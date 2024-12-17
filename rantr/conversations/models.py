from django.db import models
from django.conf import settings
from django.utils import timezone


User = settings.AUTH_USER_MODEL


class Conversation(models.Model):
    initiator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='initiated_conversations',
        null=True,
        blank=True
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_conversations',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def get_other_user(self, user=None):
        """Get the other participant in the conversation."""
        if user == self.initiator:
            return self.receiver
        return self.initiator

    def __str__(self):
        initiator_name = self.initiator.username if self.initiator else 'Unknown'
        receiver_name = self.receiver.username if self.receiver else 'Unknown'
        return f'Conversation between {initiator_name} and {receiver_name}'


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        null=True,
        blank=True
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        null=True,
        blank=True
    )
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        sender_name = self.sender.username if self.sender else 'Unknown'
        return f'Message from {sender_name} at {self.created_at}'