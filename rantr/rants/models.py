from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import TimeStampedModel
from model_utils.fields import UUIDField
from autoslug import AutoSlugField

User = get_user_model()


class Rant(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = UUIDField(primary_key=True, version=4, editable=False)
    content = models.TextField(max_length=230)
    slug = AutoSlugField(populate_from='uuid')
    likes = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='rants/images/', default=None, blank=True, null=True)

    class Meta:
        verbose_name = 'rant'
        verbose_name_plural = 'rants'

    def __str__(self):
        return self.content[:50]
    
    def get_absolute_url(self):
        return reverse("rants:detail", kwargs={"slug": self.slug})


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rant = models.ForeignKey(Rant, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'rant'))