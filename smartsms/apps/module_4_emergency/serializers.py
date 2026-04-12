from rest_framework import serializers
from .models import EmergencySOS, EmergencyLog, LocationUpdate


class LocationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for LocationUpdate model.
    Used for recording location updates during emergency.
    """
    
    class Meta:
        model = LocationUpdate
        fields = [
            'id', 'latitude', 'longitude', 'accuracy',
            'address', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmergencyLogSerializer(serializers.ModelSerializer):
    """
    Serializer for EmergencyLog model.
    Read-only serializer for viewing action logs.
    """
    
    action_display = serializers.CharField(
        source='get_action_type_display',
        read_only=True
    )
    
    class Meta:
        model = EmergencyLog
        fields = [
            'id', 'action_type', 'action_display',
            'details', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmergencySOSSerializer(serializers.ModelSerializer):
    """
    Serializer for EmergencySOS model.
    
    Used for:
    - Creating new SOS (trigger emergency)
    - Retrieving SOS details
    - Updating SOS status (resolve/cancel)
    """
    
    reason_display = serializers.CharField(
        source='get_reason_display',
        read_only=True
    )
    
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    
    # Nested read-only data
    logs = EmergencyLogSerializer(many=True, read_only=True)
    location_updates = LocationUpdateSerializer(many=True, read_only=True)
    
    class Meta:
        model = EmergencySOS
        fields = [
            'id', 'reason', 'reason_display', 'description',
            'status', 'status_display', 'location_lat', 'location_lon',
            'created_at', 'resolved_at', 'logs', 'location_updates'
        ]
        read_only_fields = ['id', 'created_at', 'resolved_at', 'logs', 'location_updates']


class EmergencySOSCreateSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for creating/triggering SOS.
    Only accepts reason, description, and initial location.
    """
    
    class Meta:
        model = EmergencySOS
        fields = [
            'reason', 'description', 'location_lat', 'location_lon'
        ]


class EmergencySOSUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating SOS status (resolve/cancel).
    """
    
    class Meta:
        model = EmergencySOS
        fields = ['status']
