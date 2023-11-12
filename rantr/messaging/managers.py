from django.db import models


class ConversationManager(models.Manager):
    def get_or_create_participants(self, *participant_ids):
        participant_ids = list(participant_ids)
        participant_ids.sort()

        # Check if a conversation with the specified participants already exists
        conversations = self.filter(participants__in=participant_ids).distinct()

        if conversations.exists():
            return conversations.first()

        # Create a new conversation if none exists
        new_conversation = self.create()
        new_conversation.participants.set(participant_ids)
        return new_conversation