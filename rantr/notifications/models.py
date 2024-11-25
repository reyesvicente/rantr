from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='actions')
    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Generic foreign key to the target object (e.g., a rant, comment, etc.)
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='notifications_target', null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')
    
    unread = models.BooleanField(default=True, db_index=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'notifications'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['recipient', 'unread']),
            models.Index(fields=['recipient', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.actor} {self.verb} -> {self.recipient}"
    
    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()
