from django.db import models
from django.contrib.auth import get_user_model

from model_utils.models import TimeStampedModel

from rantr.rants.models import Rant

User = get_user_model()


class Comment(TimeStampedModel):
    rant = models.ForeignKey(Rant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
