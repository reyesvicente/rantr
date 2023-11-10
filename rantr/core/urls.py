from django.urls import path

from rantr.core.views import UnreadNotificationsList

app_name = 'core'
urlpatterns = [
    path('inbox/unread/', UnreadNotificationsList.as_view(), name='unread'),
]