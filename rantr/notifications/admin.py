# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'recipient',
        'actor',
        'verb',
        'target_content_type',
        'target_object_id',
        'unread',
        'timestamp',
    )
    list_filter = ('unread', 'timestamp', 'recipient', 'actor', 'verb')
    search_fields = ('description', 'recipient__username', 'actor__username')
    raw_id_fields = ('recipient', 'actor')
    date_hierarchy = 'timestamp'
