from django.db import models
from django.contrib.auth import get_user_model
from model_utils.models import TimeStampedModel
from rantr.rants.models import Rant

User = get_user_model()


class Comment(TimeStampedModel):
    rant = models.ForeignKey(Rant, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['rant', '-created']),
            models.Index(fields=['user', '-created']),
            models.Index(fields=['parent', '-created']),
        ]

    def __str__(self):
        return f"{self.user.username}'s comment on {self.rant}"

    def save(self, *args, **kwargs):
        # Update rant's popularity score when comment is created/deleted
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.rant.update_popularity_score()

    def delete(self, *args, **kwargs):
        rant = self.rant
        super().delete(*args, **kwargs)
        rant.update_popularity_score()

    @property
    def is_reply(self):
        return self.parent is not None

    @property
    def reply_count(self):
        return self.replies.count()
