from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, ManyToManyField, BooleanField, ImageField, TextField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for Rantr.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """
    following = ManyToManyField('self', symmetrical=False, related_name='followers')
    is_onboarded = BooleanField(default=False)
    location = CharField(max_length=50, default="", blank=True)
    profile_picture = ImageField(upload_to='users/profile_picture/', default=None, blank=True, null=True)
    bio = TextField(max_length=250, default="")

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
