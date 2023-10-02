from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from model_utils.models import TimeStampedModel
from model_utils.fields import UUIDField
from autoslug import AutoSlugField

User = get_user_model()


class Profile(TimeStampedModel):
    uuid = UUIDField(version=4, editable=False)
    slug = AutoSlugField(populate_from='uuid')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField(
        "self",
        related_name='followed_by',
        symmetrical=False,
        blank=True
    )

    def __str__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return reverse("profiles:detail", kwargs={"uuid": self.uuid})
    

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        user_profile.follows.add(instance.profile)
        user_profile.save()
