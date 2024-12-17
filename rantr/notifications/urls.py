from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('mark-as-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-as-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete'),
    path('delete-all/', views.delete_all_notifications, name='delete_all'),
]
