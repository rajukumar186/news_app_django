 
from django.contrib import admin
from .models import ChatRoom, Message

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'user_email', 'admin_email', 'created_at')
    search_fields = ('room_id', 'user_email', 'admin_email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender_email', 'timestamp', 'content_preview')
    search_fields = ('sender_email', 'content')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)

    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Message Preview'