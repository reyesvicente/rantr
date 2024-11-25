# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('created', 'modified', 'uuid')
    list_filter = ('created', 'modified')
    raw_id_fields = ('participants',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'created',
        'modified',
        'uuid',
        'conversation',
        'sender',
        'content',
    )
    list_filter = ('created', 'modified', 'conversation', 'sender')