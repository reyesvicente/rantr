from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from rantr.rants.models import Rant
from rantr.comments.models import Comment
from rantr.likes.models import Like
from rantr.notifications.models import Notification

@receiver(post_save, sender=Like)
def notify_like(sender, instance, created, **kwargs):
    if created:
        rant = instance.rant
        if instance.user != rant.user:  # Don't notify if user likes their own rant
            Notification.objects.create(
                recipient=rant.user,
                actor=instance.user,
                verb='liked',
                target_content_type=ContentType.objects.get_for_model(rant),
                target_object_id=rant.id,
                description=f"{instance.user.username} liked your rant"
            )

@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    if created:
        if instance.parent:  # This is a reply to a comment
            if instance.user != instance.parent.user:  # Don't notify if user replies to their own comment
                Notification.objects.create(
                    recipient=instance.parent.user,
                    actor=instance.user,
                    verb='replied to',
                    target_content_type=ContentType.objects.get_for_model(instance.parent),
                    target_object_id=instance.parent.id,
                    description=f"{instance.user.username} replied to your comment"
                )
        else:  # This is a comment on a rant
            if instance.user != instance.rant.user:  # Don't notify if user comments on their own rant
                Notification.objects.create(
                    recipient=instance.rant.user,
                    actor=instance.user,
                    verb='commented on',
                    target_content_type=ContentType.objects.get_for_model(instance.rant),
                    target_object_id=instance.rant.id,
                    description=f"{instance.user.username} commented on your rant"
                )
