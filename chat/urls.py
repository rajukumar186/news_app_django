# chat/urls.py
from django.shortcuts import redirect
from django.urls import path
from .views import user_chat_view, admin_chat_dashboard, ping_admin, room_messages_api


def admin_chat_redirect(request):
    return redirect('custom_admin_dashboard')


urlpatterns = [
    path('', user_chat_view, name='support_chat'),
    path('ping-admin/', ping_admin, name='ping_admin'),
    path('admin-dashboard/', admin_chat_redirect, name='admin_chat_dashboard'),
    path('api/messages/<str:room_name>/', room_messages_api, name='room_messages_api'),
]