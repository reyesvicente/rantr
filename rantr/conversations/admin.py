# -*- coding: utf-8 -*-
from django.contrib import admin
from rantr.conversations.models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['initiator', 'receiver', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['initiator__username', 'receiver__username']
    date_hierarchy = 'created_at'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'content', 'created_at']
    list_filter = ['created_at', 'sender']
    search_fields = ['content', 'sender__username']
    date_hierarchy = 'created_at'
    raw_id_fields = ['conversation', 'sender']