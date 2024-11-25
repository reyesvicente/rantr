from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from rantr.rants.models import Rant
from rantr.comments.models import Comment
from rantr.likes.models import Like

# Define our own notification signal
notify = Signal()

@receiver(post_save, sender=Like)
def notify_like(sender, instance, created, **kwargs):
    if created and instance.content_type.model_class() == Rant:
        rant = instance.content_object
        if instance.user != rant.user:  # Don't notify if user likes their own rant
            notify.send(
                sender=instance.user,
                recipient=rant.user,
                verb='liked',
                action_object=instance,
                target=rant,
                description=f"{instance.user.username} liked your rant"
            )

@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    if created:
        if instance.parent:  # This is a reply to a comment
            if instance.user != instance.parent.user:  # Don't notify if user replies to their own comment
                notify.send(
                    sender=instance.user,
                    recipient=instance.parent.user,
                    verb='replied to',
                    action_object=instance,
                    target=instance.parent,
                    description=f"{instance.user.username} replied to your comment"
                )
        else:  # This is a comment on a rant
            if instance.user != instance.rant.user:  # Don't notify if user comments on their own rant
                notify.send(
                    sender=instance.user,
                    recipient=instance.rant.user,
                    verb='commented on',
                    action_object=instance,
                    target=instance.rant,
                    description=f"{instance.user.username} commented on your rant"
                )
