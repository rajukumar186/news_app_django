import json
import traceback
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from .rag_service import query_rag_assistant

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Gracefully leave the room group on disconnect
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception:
            pass

    async def receive_json(self, content):
        user_message = content.get("message", "")
        sender_email = content.get("sender_email", "guest@thepeoplesera.com")

        if not user_message.strip():
            return

        # 1. Echo user message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "sender_email": sender_email,
                "message": user_message
            }
        )

        # 2. Run RAG safely in thread pool
        try:
            ai_response = await sync_to_async(query_rag_assistant)(user_message)
        except Exception as e:
            traceback.print_exc()
            ai_response = f"⚠️ Sorry, an error occurred: {str(e)}"

        # 3. Send AI response back
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "sender_email": "assistant@thepeoplesera.com",
                "message": ai_response
            }
        )

    async def chat_message(self, event):
        await self.send_json({
            "sender_email": event["sender_email"],
            "message": event["message"]
        })