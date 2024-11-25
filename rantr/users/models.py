from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, ManyToManyField, BooleanField, ImageField, TextField, Count, Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils.functional import cached_property
from django.db import models


class User(AbstractUser):
    """
    Custom user model for Rantr with additional fields and functionality.
    """
    username_validator = RegexValidator(
        regex=r'^[\w.@+-]+$',
        message=_('Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.')
    )

    username = CharField(
        _('username'),
        max_length=30,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
        db_index=True
    )

    following = ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        db_index=True
    )

    is_onboarded = BooleanField(default=False)
    
    location = CharField(
        max_length=50,
        default="",
        blank=True,
        help_text=_('City, Country or any location identifier')
    )
    
    profile_picture = ImageField(
        upload_to='users/profile_picture/%Y/%m/',
        default=None,
        blank=True,
        null=True
    )
    
    bio = TextField(
        max_length=250,
        default="",
        blank=True,
        help_text=_('Tell us about yourself in 250 characters or less')
    )

    class Meta:
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['is_onboarded']),
        ]
        ordering = ['-date_joined']

    def get_absolute_url(self) -> str:
        return reverse("users:detail", kwargs={"username": self.username})

    @cached_property
    def followers_count(self) -> int:
        return self.followers.count()

    @cached_property
    def following_count(self) -> int:
        return self.following.count()

    @cached_property
    def rants_count(self) -> int:
        return self.rants.count()

    def get_timeline_rants(self):
        """Get rants from users that this user follows, including their own rants."""
        from rantr.rants.models import Rant
        return Rant.objects.filter(
            Q(user__in=self.following.all()) | Q(user=self)
        ).select_related('user').prefetch_related('comments').order_by('-created')

    def get_suggested_users(self, limit=5):
        """Get suggested users to follow based on common followers/following."""
        return User.objects.filter(
            ~Q(pk=self.pk) & ~Q(pk__in=self.following.all())
        ).annotate(
            common_followers=Count('followers', filter=Q(followers__in=self.followers.all())),
            common_following=Count('following', filter=Q(following__in=self.following.all()))
        ).order_by('-common_followers', '-common_following')[:limit]

    def toggle_follow(self, user_to_follow):
        """Toggle follow/unfollow for a user."""
        if user_to_follow == self:
            return False
        if self.following.filter(pk=user_to_follow.pk).exists():
            self.following.remove(user_to_follow)
            return False
        self.following.add(user_to_follow)
        return True
