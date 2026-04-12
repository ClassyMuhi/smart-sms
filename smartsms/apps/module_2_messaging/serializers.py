from rest_framework import serializers
from .models import SMSMessage, DeliveryStatus, MessageTemplate


class DeliveryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryStatus
        fields = [
            'id', 'status', 'status_description', 'delivery_timestamp',
            'error_code', 'cost', 'last_checked'
        ]
        read_only_fields = ['id', 'last_checked']


class SMSMessageSerializer(serializers.ModelSerializer):
    delivery_status = DeliveryStatusSerializer(read_only=True)
    
    class Meta:
        model = SMSMessage
        fields = [
            'id', 'sender', 'recipient', 'message', 'message_type',
            'status', 'created_at', 'updated_at', 'sent_at',
            'characters_count', 'segments_count', 'delivery_status'
        ]
        read_only_fields = [
            'id', 'sender', 'message_type', 'status',
            'created_at', 'updated_at', 'sent_at',
            'characters_count', 'segments_count'
        ]


class MessageTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageTemplate
        fields = ['id', 'name', 'description', 'content', 'variables', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
