from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Notification

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    paginate_by = 20
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return self.model.objects.filter(
            recipient=self.request.user,
            deleted=False
        ).order_by('-timestamp')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = self.model.objects.filter(
            recipient=self.request.user,
            unread=True,
            deleted=False
        ).count()
        return context

@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(
        Notification, 
        recipient=request.user,
        id=notification_id
    )
    notification.mark_as_read()
    messages.success(request, 'Notification marked as read.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('notifications:list')))

@login_required
def mark_all_as_read(request):
    Notification.objects.filter(recipient=request.user, unread=True).update(unread=False)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:list')

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(
        Notification, 
        recipient=request.user,
        id=notification_id
    )
    notification.delete()
    messages.success(request, 'Notification deleted.')
    return redirect('notifications:list')

@login_required
def delete_all_notifications(request):
    Notification.objects.filter(recipient=request.user).delete()
    messages.success(request, 'All notifications deleted.')
    return redirect('notifications:list')
