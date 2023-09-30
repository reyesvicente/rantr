from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class FriendsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rantr.friends"
    verbose_name = _("Friends")
