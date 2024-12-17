# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'modified',
        'rant',
        'user',
        'content',
        'parent',
        'likes',
    )
    list_filter = ('created', 'modified', 'rant', 'user', 'parent')