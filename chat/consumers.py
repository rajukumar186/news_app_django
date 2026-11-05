# chat/consumers.py
import json
from collections import defaultdict

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message

ONLINE_USERS = defaultdict(set)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope.get('user') or not self.scope['user'].is_authenticated:
            await self.close()
            return

        self.user_email = self.scope['user'].email or self.scope['user'].username
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.update_presence()

    async def disconnect(self, close_code):
        await self.update_presence(remove=True)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        if not text_data:
            return

        data = json.loads(text_data)
        message = data.get('message')
        sender_email = data.get('sender_email')

        if not sender_email or not message or not message.strip():
            return

        saved_message = await self.save_message(self.room_name, sender_email, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_email': sender_email,
                'message_id': saved_message.id,
                'timestamp': saved_message.timestamp.isoformat(),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_email': event['sender_email'],
            'message_id': event.get('message_id'),
            'timestamp': event.get('timestamp'),
        }))

    async def presence_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'online_users': event['online_users']
        }))

    async def update_presence(self, remove=False):
        room_users = ONLINE_USERS[self.room_group_name]
        if remove:
            room_users.discard(self.user_email)
            if not room_users:
                ONLINE_USERS.pop(self.room_group_name, None)
        else:
            room_users.add(self.user_email)

        online_users = sorted(ONLINE_USERS.get(self.room_group_name, set()))
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'presence_status',
                'online_users': online_users,
            }
        )

    @database_sync_to_async
    def save_message(self, room_id, sender_email, content):
        room, created = ChatRoom.objects.get_or_create(room_id=room_id, defaults={'user_email': sender_email})
        return Message.objects.create(room=room, sender_email=sender_email, content=content)