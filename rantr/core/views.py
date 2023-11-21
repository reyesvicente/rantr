from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from django.views import View

from notifications.models import Notification


class UnreadNotificationsList(ListView):  
    model = Notification 
    queryset = Notification.objects.filter(unread=True)
    template_name = 'notifications/unread_list.html'

    def get_queryset(self):
        # Filter unread notifications for the logged-in user
        return Notification.objects.filter(recipient=self.request.user, unread=True)


class MarkNotificationAsReadView(View):
    def get(self, request, notification_id):
        notification = get_object_or_404(Notification, id=notification_id)
        notification.mark_as_read()
        return redirect('core:unread')