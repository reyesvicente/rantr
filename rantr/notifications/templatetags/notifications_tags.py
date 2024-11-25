from django import template
from django.template.loader import render_to_string

from rantr.notifications.models import Notification

register = template.Library()

@register.simple_tag(takes_context=True)
def notifications_unread(context):
    """Return the number of unread notifications for the current user."""
    if not context.get('request') or not context['request'].user.is_authenticated:
        return 0
    return Notification.objects.filter(recipient=context['request'].user, unread=True).count()

@register.inclusion_tag('notifications/notifications_menu.html', takes_context=True)
def show_notifications(context):
    """Render the notifications dropdown menu."""
    if not context.get('request') or not context['request'].user.is_authenticated:
        return {'notifications': []}
    
    notifications = Notification.objects.filter(
        recipient=context['request'].user,
        unread=True
    ).order_by('-timestamp')[:5]
    
    return {
        'notifications': notifications,
        'notifications_count': notifications.count(),
    }
