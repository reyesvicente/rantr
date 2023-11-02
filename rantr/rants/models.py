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
    popularity_score = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'rant'
        verbose_name_plural = 'rants'

    def __str__(self):
        return self.content[:50]

    def save(self, *args, **kwargs):
        # Calculate popularity_score here
        like_weight = 4.0
        comment_weight = 5.0
        self.popularity_score = (self.likes * like_weight) + (self.comment_set.count() * comment_weight)
        super(Rant, self).save(*args, **kwargs)

    def update_popularity_score(self):
        self.save()

    def get_absolute_url(self):
        return reverse("rants:detail", kwargs={"slug": self.slug})