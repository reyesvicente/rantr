from django.urls import path

from rantr.core.views import UnreadNotificationsList, MarkNotificationAsReadView, search

app_name = 'core'
urlpatterns = [
    path('inbox/unread/', UnreadNotificationsList.as_view(), name='unread'),
    path('notifications/mark-as-read/<int:notification_id>/', MarkNotificationAsReadView.as_view(), name='mark_as_read'),
    path('search/', search, name='search'),
]