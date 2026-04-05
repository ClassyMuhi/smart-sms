from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import SMSMessage, DeliveryStatus, MessageTemplate
from .serializers import SMSMessageSerializer, DeliveryStatusSerializer, MessageTemplateSerializer


class SMSMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing SMS messages.
    
    Features:
    - Send SMS messages
    - Retrieve message history
    - Check delivery status
    """
    queryset = SMSMessage.objects.all()
    serializer_class = SMSMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter messages by current user"""
        user = self.request.user
        return SMSMessage.objects.filter(sender=user.phone)
    
    def create(self, request, *args, **kwargs):
        """Send a new SMS message"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create message
        message = serializer.save(
            sender=request.user.phone,
            message_type='outbound',
            status='pending'
        )
        
        # Create delivery status tracking
        DeliveryStatus.objects.create(message=message)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['get'])
    def delivery_status(self, request, pk=None):
        """Get delivery status of a specific message"""
        message = self.get_object()
        try:
            delivery_status = message.delivery_status
            serializer = DeliveryStatusSerializer(delivery_status)
            return Response(serializer.data)
        except DeliveryStatus.DoesNotExist:
            return Response(
                {'error': 'No delivery status found'},
                status=status.HTTP_404_NOT_FOUND
            )


class MessageTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing message templates.
    
    Features:
    - Create reusable message templates
    - Use template variables
    - Quick message sending
    """
    queryset = MessageTemplate.objects.filter(is_active=True)
    serializer_class = MessageTemplateSerializer
    permission_classes = [IsAuthenticated]
