from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message
from .serializers import MessageSerializer

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(sender=user) | Message.objects.filter(receiver=user)

    @action(detail=False, methods=['post'], url_path='send')
    def send_message(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            receiver = serializer.validated_data.get('receiver')
            receiver_id = str(receiver.id) if receiver else None
            
            # Since receiver_id is validated in the serializer to exist, we can create the message here.
            # We enforce sender to be the authenticated user.
            message = serializer.save(sender=request.user, status='sent')

            # Async Hook to channel layer
            channel_layer = get_channel_layer()
            if channel_layer and receiver_id:
                group_name = f"user_personal_{receiver_id}"
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "chat.message",
                        "event_type": "receive_message",
                        "message_id": message.id,
                        "sender_id": str(request.user.id),
                        "content": message.content,
                        "timestamp": message.timestamp.isoformat(),
                    }
                )

            return Response(
                {"message": "Message sent successfully.", "message_id": message.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='history/(?P<conversation_id>[^/.]+)')
    def conversation_history(self, request, conversation_id=None):
        if not conversation_id:
            return Response({"error": "Conversation ID required."}, status=status.HTTP_400_BAD_REQUEST)
        
        messages = self.get_queryset().filter(conversation_id=conversation_id).order_by('timestamp')
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
