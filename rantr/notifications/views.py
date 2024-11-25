from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from notifications.models import Notification

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    paginator = Paginator(notifications, 20)  # Show 20 notifications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    unread_count = notifications.filter(unread=True).count()
    
    context = {
        'notifications': page_obj,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notification_list.html', context)

@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(
        Notification, 
        recipient=request.user,
        id=notification_id
    )
    notification.mark_as_read()
    messages.success(request, 'Notification marked as read.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('rantr_notifications:list')))

@login_required
def mark_all_as_read(request):
    Notification.objects.filter(recipient=request.user, unread=True).update(unread=False)
    messages.success(request, 'All notifications marked as read.')
    return redirect('rantr_notifications:list')

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(
        Notification, 
        recipient=request.user,
        id=notification_id
    )
    notification.delete()
    messages.success(request, 'Notification deleted.')
    return redirect('rantr_notifications:list')

@login_required
def delete_all_notifications(request):
    Notification.objects.filter(recipient=request.user).delete()
    messages.success(request, 'All notifications deleted.')
    return redirect('rantr_notifications:list')
