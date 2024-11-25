from django.db import models
from notifications.base.models import AbstractNotification

class Notification(AbstractNotification):
    class Meta(AbstractNotification.Meta):
        abstract = False
        indexes = [
            models.Index(fields=['recipient', 'unread']),
            models.Index(fields=['recipient', 'timestamp']),
        ]
        # Remove index_together as it's deprecated
        app_label = 'rantr_notifications'  # Match the app label from apps.py
