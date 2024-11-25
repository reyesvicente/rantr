from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rantr.notifications'
    label = 'rantr_notifications'  # This must be unique
    verbose_name = 'Notifications'

    def ready(self):
        try:
            import rantr.notifications.signals  # noqa F401
        except ImportError:
            pass
