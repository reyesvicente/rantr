from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

from model_utils.models import TimeStampedModel
from model_utils.fields import UUIDField

from rantr.rants.models import Rant

User = get_user_model()


class Comment(TimeStampedModel):
    uuid = UUIDField(version=4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None) 
    rant = models.ForeignKey(Rant, on_delete=models.CASCADE, default=None)
    text = models.TextField(default=None)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, default=None)
    
    class Meta:
        verbose_name = "Coment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.text[:50]
    
    def get_absolute_url(self):
        return reverse("comments:detail", kwargs={"uuid": self.uuid})
