from rest_framework import serializers
from .models import Message
from auth_module.models import CustomUser

class MessageSerializer(serializers.ModelSerializer):
    sender_phone = serializers.CharField(source='sender.phone', read_only=True)
    receiver_phone = serializers.CharField(source='receiver.phone', read_only=True)

    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='receiver'
    )

    class Meta:
        model = Message
        fields = ['id', 'sender_id', 'sender_phone', 'receiver_id', 'receiver_phone', 
                  'conversation_id', 'content', 'timestamp', 'status']
        read_only_fields = ['id', 'sender_id', 'timestamp', 'status']
