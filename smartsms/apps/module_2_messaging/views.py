from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
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
        payload = request.data.copy()
        recipient = payload.get('recipient') or payload.get('recipient_phone')
        message = payload.get('message') or payload.get('message_body')

        if not recipient or not message:
            return Response(
                {'detail': 'recipient/message or recipient_phone/message_body are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload['sender'] = request.user.phone
        payload['recipient'] = recipient
        payload['message'] = message
        payload['message_type'] = 'outbound'
        payload['status'] = 'pending'

        serializer = self.get_serializer(data=payload)
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

    @action(detail=False, methods=['get'])
    def thread(self, request):
        """Get message history between the current user and a contact phone."""
        contact_phone = request.query_params.get('contact_phone') or request.query_params.get('recipient_phone')
        if not contact_phone:
            return Response(
                {'detail': 'contact_phone is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = SMSMessage.objects.filter(
            Q(sender=request.user.phone, recipient=contact_phone) |
            Q(sender=contact_phone, recipient=request.user.phone)
        ).order_by('created_at')

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'contact_phone': contact_phone,
            'count': queryset.count(),
            'results': serializer.data,
        })
    
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
