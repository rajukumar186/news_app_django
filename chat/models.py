# chat/models.py
from django.db import models
from django.contrib.auth.models import User


class ChatRoom(models.Model):
    room_id = models.CharField(max_length=255, unique=True, help_text="Unique identifier, e.g., user email")
    user_email = models.EmailField()
    admin_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_pending = models.BooleanField(default=False)
    unread_by_admin = models.IntegerField(default=0)
    last_ping_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Chat: {self.user_email}"


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender_email = models.EmailField()
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.sender_email}: {self.content[:30]}"


class ChatSession(models.Model):
    STATUS_CHOICES = [
        ('ai', 'AI Active'),
        ('pending', 'Waiting for Support Executive'),
        ('human', 'Connected to Human Agent'),
        ('closed', 'Closed'),
    ]
    
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ai')
    assigned_agent = models.ForeignKey(User, null=True, blank=True, related_name='assigned_chats', on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)