# chat/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from .models import ChatRoom, Message

User = get_user_model()


def get_or_create_user_room(user_email):
    room_id = user_email.replace('@', '_').replace('.', '_')
    room, created = ChatRoom.objects.get_or_create(
        room_id=room_id,
        defaults={'user_email': user_email}
    )

    if not room.admin_email:
        admin = User.objects.filter(is_staff=True, is_active=True).order_by('id').first()
        if admin and admin.email:
            room.admin_email = admin.email
            room.save(update_fields=['admin_email'])

    return room


@login_required
def user_chat_view(request):
    room = get_or_create_user_room(request.user.email)
    initial_messages = room.messages.all().order_by('timestamp')

    return render(request, 'support_chat.html', {
        'initial_messages': initial_messages,
        'admin_email': room.admin_email,
        'room_name': room.room_id,
    })


@login_required
def ping_admin(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST is allowed.'}, status=405)

    room = get_or_create_user_room(request.user.email)
    room.is_pending = True
    room.last_ping_at = timezone.now()
    room.unread_by_admin = (room.unread_by_admin or 0) + 1
    room.save(update_fields=['is_pending', 'last_ping_at', 'unread_by_admin'])

    return JsonResponse({
        'status': 'success',
        'message': 'Admin has been notified.',
        'admin_email': room.admin_email,
        'redirect': reverse('support_chat'),
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_chat_dashboard(request):
    chat_rooms = ChatRoom.objects.all().order_by('-last_ping_at', '-created_at')
    pending_requests = chat_rooms.filter(is_pending=True)
    active_user = request.GET.get('user')
    initial_messages = []

    if active_user:
        room_id = active_user.replace('@', '_').replace('.', '_')
        try:
            room = ChatRoom.objects.get(room_id=room_id)
            room.is_pending = False
            room.unread_by_admin = 0
            room.save(update_fields=['is_pending', 'unread_by_admin'])
            initial_messages = room.messages.all().order_by('timestamp')
        except ChatRoom.DoesNotExist:
            pass

    return render(request, 'admin_chat.html', {
        'chat_rooms': chat_rooms,
        'pending_requests': pending_requests,
        'active_user': active_user,
        'initial_messages': initial_messages,
    })


@login_required
def room_messages_api(request, room_name):
    room = ChatRoom.objects.filter(room_id=room_name).first()
    if not room:
        return JsonResponse({'messages': []})

    messages = room.messages.all().order_by('timestamp')
    data = [
        {
            'id': msg.id,
            'sender_email': msg.sender_email,
            'message': msg.content,
            'timestamp': msg.timestamp.isoformat(),
        }
        for msg in messages
    ]
    return JsonResponse({'messages': data})