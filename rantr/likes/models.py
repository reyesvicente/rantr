from django.contrib.auth import get_user_model
from django.db import models

from rantr.rants.models import Rant

User = get_user_model()

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rant = models.ForeignKey(Rant, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'rant'))