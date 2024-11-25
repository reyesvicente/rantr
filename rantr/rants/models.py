from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import models

from model_utils.models import TimeStampedModel
from model_utils.fields import UUIDField
from autoslug import AutoSlugField
from django.utils.text import slugify
from uuid import uuid4

User = get_user_model()


class Rant(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rants')
    uuid = UUIDField(primary_key=True, version=4, editable=False, db_index=True)
    content = models.TextField(max_length=230)
    slug = AutoSlugField(populate_from='uuid', unique=True, db_index=True)
    likes = models.PositiveIntegerField(default=0, db_index=True)
    image = models.ImageField(upload_to='rants/images/%Y/%m/', default=None, blank=True, null=True)
    popularity_score = models.DecimalField(default=0.0, max_digits=10, decimal_places=5, db_index=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'rant'
        verbose_name_plural = 'rants'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-popularity_score', '-created']),
            models.Index(fields=['-created']),
            models.Index(fields=['user', '-created']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"

    def save(self, *args, **kwargs):
        # Calculate popularity_score here
        like_weight = settings.LIKE_WEIGHT
        comment_weight = settings.COMMENT_WEIGHT
        impression_weight = settings.IMPRESSION_WEIGHT
        
        # Use select_related to avoid additional queries
        comment_count = self.comments.count() if self.pk else 0
        self.popularity_score = (self.likes * like_weight) + (comment_count * comment_weight) + (self.views * impression_weight)
        
        # Organize uploaded images by year/month
        if self.image and not self.pk:  # Only for new instances
            from datetime import datetime
            date = datetime.now()
            self.image.name = f"rants/images/{date.year}/{date.month}/{self.image.name}"
        
        super(Rant, self).save(*args, **kwargs)

    def update_popularity_score(self):
        from django.db.models import Count
        from django.db import transaction
        
        with transaction.atomic():
            comment_count = self.comments.count()
            like_weight = settings.LIKE_WEIGHT
            comment_weight = settings.COMMENT_WEIGHT
            impression_weight = settings.IMPRESSION_WEIGHT
            
            self.popularity_score = (self.likes * like_weight) + (comment_count * comment_weight) + (self.views * impression_weight)
            self.save(update_fields=['popularity_score'])

    def increment_views(self):
        from django.db.models import F
        with transaction.atomic():
            self.views = F('views') + 1
            self.save(update_fields=['views'])
            self.refresh_from_db()
            self.update_popularity_score()

    def get_absolute_url(self):
        return reverse("rants:detail", kwargs={"slug": self.slug})

    @property
    def comment_count(self):
        return self.comments.count()

    @property
    def like_count(self):
        return self.likes