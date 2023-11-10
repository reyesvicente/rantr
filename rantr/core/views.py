from django.shortcuts import render
from django.views.generic import ListView

from notifications.models import Notification


class UnreadNotificationsList(ListView):  
    model = Notification 
    queryset = Notification.objects.filter(unread=True)
    template_name = 'notifications/unread_list.html'