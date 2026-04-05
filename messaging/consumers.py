import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from auth_module.models import CustomUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            # Reject connection if not authenticated
            await self.close()
        else:
            self.user_group_name = f"user_personal_{self.user.id}"

            # Join personal group
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group_name'):
            # Leave personal group
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    # Receive message from WebSocket (Client sending a message directly via WS)
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            receiver_id = data.get('receiver_id')
            content = data.get('content')
            conversation_id = data.get('conversation_id', f"conv_{self.user.id}_{receiver_id}")

            if receiver_id and content:
                # Save message to database
                message = await self.save_message(receiver_id, content, conversation_id)
                if not message:
                    return

                # Broadcast to receiver's personal group
                receiver_group_name = f"user_personal_{receiver_id}"
                await self.channel_layer.group_send(
                    receiver_group_name,
                    {
                        "type": "chat.message",
                        "event_type": "receive_message",
                        "message_id": message.id,
                        "sender_id": str(self.user.id),
                        "content": content,
                        "timestamp": message.timestamp.isoformat(),
                    }
                )

                # Send delivery update back to sender
                await self.send(text_data=json.dumps({
                    'event_type': 'delivery_update',
                    'message_id': message.id,
                    'status': 'sent'
                }))

        except json.JSONDecodeError:
            pass

    # Receive message from channel layer (from group_send)
    async def chat_message(self, event):
        # We catch the raw event dictionary
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, receiver_id, content, conversation_id):
        try:
            receiver = CustomUser.objects.get(id=receiver_id)
            return Message.objects.create(
                sender=self.user,
                receiver=receiver,
                content=content,
                conversation_id=conversation_id,
                status='sent'
            )
        except CustomUser.DoesNotExist:
            return None
