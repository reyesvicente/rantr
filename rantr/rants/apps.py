from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class RantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rantr.rants"
    verbose_name = _("Rants")
