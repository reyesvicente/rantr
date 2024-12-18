from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from model_utils.models import TimeStampedModel
from model_utils.fields import UUIDField
from autoslug import AutoSlugField
from rantr.utils.image_resizer import validate_rectangular_image

User = get_user_model()


class Rant(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rants')
    uuid = UUIDField(primary_key=True, version=4, editable=False, db_index=True)
    content = models.TextField(max_length=230)
    slug = AutoSlugField(populate_from='uuid', unique=True, db_index=True)
    likes = models.PositiveIntegerField(default=0, db_index=True)
    image = models.ImageField(upload_to='rants/images/%Y/%m/', default=None, blank=True, null=True, validators=[validate_rectangular_image])
    popularity_score = models.DecimalField(default=0.0, max_digits=10, decimal_places=5, db_index=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'rant'
        verbose_name_plural = 'rants'
        ordering = ['-popularity_score', '-created']
        indexes = [
            models.Index(fields=['-popularity_score', '-created']),
            models.Index(fields=['-created']),
            models.Index(fields=['user', '-created']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"

    def update_popularity_score(self):
        like_weight = settings.LIKE_WEIGHT
        comment_weight = settings.COMMENT_WEIGHT
        impression_weight = settings.IMPRESSION_WEIGHT
        
        comment_count = self.comments.count()
        self.popularity_score = (self.likes * like_weight) + (comment_count * comment_weight) + (self.views * impression_weight)
        self.save(update_fields=['popularity_score'])

    def save(self, *args, **kwargs):
        # Only calculate popularity score if not just updating specific fields
        if not kwargs.get('update_fields'):
            like_weight = settings.LIKE_WEIGHT
            comment_weight = settings.COMMENT_WEIGHT
            impression_weight = settings.IMPRESSION_WEIGHT
            
            comment_count = self.comments.count() if self.pk else 0
            self.popularity_score = (self.likes * like_weight) + (comment_count * comment_weight) + (self.views * impression_weight)
        
        # Organize uploaded images by year/month
        if self.image and not self.pk:  # Only for new instances
            from datetime import datetime
            date = datetime.now()
            self.image.name = f"rants/images/{date.year}/{date.month}/{self.image.name}"
            
        super().save(*args, **kwargs)

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

# Signal handlers to update popularity score when related models change
@receiver([post_save, post_delete], sender='likes.Like')
def update_rant_popularity_on_like_change(sender, instance, **kwargs):
    if hasattr(instance, 'rant'):
        instance.rant.update_popularity_score()

@receiver([post_save, post_delete], sender='comments.Comment')
def update_rant_popularity_on_comment_change(sender, instance, **kwargs):
    if hasattr(instance, 'rant'):
        instance.rant.update_popularity_score()