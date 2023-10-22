from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, ManyToManyField, BooleanField
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

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
