from django.contrib import admin
from .models import UserProfile, Messages


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_name', 'chat_id', 'created_at', 'active', 'is_admin']
    list_editable = ['is_admin']
    list_filter = ['is_admin', 'active', 'created_at']


@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'text', 'created_at']
