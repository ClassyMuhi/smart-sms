from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from apps.module_3_contacts.models import EmergencyContact
from apps.module_2_messaging.models import SMSMessage
from .models import EmergencySOS, EmergencyLog, LocationUpdate
from .serializers import (
    EmergencySOSSerializer,
    EmergencySOSCreateSerializer,
    EmergencySOSUpdateSerializer,
    LocationUpdateSerializer,
)


class EmergencySOSViewSet(viewsets.ModelViewSet):
    """
    Emergency SOS Management API ViewSet.
    
    Endpoints:
    - POST /api/emergency/sos/ - Trigger emergency (activate SOS)
    - GET /api/emergency/sos/ - List all user's SOS events
    - GET /api/emergency/sos/{id}/ - Get specific SOS details with logs and location
    - PATCH /api/emergency/sos/{id}/ - Update SOS status (resolve/cancel)
    - POST /api/emergency/sos/{id}/add_location/ - Add location update
    - GET /api/emergency/sos/{id}/emergency_contacts/ - Get emergency contacts for this SOS
    
    Permissions:
    - Only authenticated users
    - Users can only access their own SOS requests
    """
    
    serializer_class = EmergencySOSSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def _user_identifier(self, user):
        """Use email first, then phone for sender identity."""
        return user.email or user.phone

    def _create_and_dispatch_sos(self, *, user, reason='other', description='', location_lat=None, location_lon=None):
        """Create SOS, notify emergency contacts through messaging module, and log all actions."""
        sos = EmergencySOS.objects.create(
            user=user,
            reason=reason,
            description=description or 'Emergency Help activated',
            location_lat=location_lat,
            location_lon=location_lon,
            status='active',
        )

        maps_url = None
        if location_lat is not None and location_lon is not None:
            maps_url = f"https://www.google.com/maps/search/?api=1&query={location_lat},{location_lon}"

        EmergencyLog.objects.create(
            emergency_sos=sos,
            action_type='triggered',
            details={
                'reason': sos.reason,
                'description': sos.description,
                'location': f"{location_lat}, {location_lon}" if location_lat is not None and location_lon is not None else 'Not provided',
                'maps_url': maps_url,
            }
        )

        emergency_contacts = EmergencyContact.objects.filter(user=user).select_related('contact')
        sender_identifier = self._user_identifier(user)
        sent_count = 0
        failed_count = 0

        for ec in emergency_contacts:
            contact = ec.contact
            recipient_identifier = contact.email or contact.phone

            if not recipient_identifier:
                failed_count += 1
                EmergencyLog.objects.create(
                    emergency_sos=sos,
                    action_type='failed',
                    details={
                        'reason': 'message_send_failed',
                        'contact_name': contact.name,
                        'error': 'Emergency contact has no phone/email.'
                    }
                )
                continue

            alert_message = (
                f"Emergency Alert from {user.full_name or sender_identifier}.\n"
                f"They may need immediate help.\n"
                f"Reason: {sos.get_reason_display()}"
            )
            if sos.description:
                alert_message += f"\nNote: {sos.description}"
            if maps_url:
                alert_message += f"\nOpen live location: {maps_url}"
            else:
                alert_message += "\nLocation is currently unavailable."

            try:
                msg = SMSMessage.objects.create(
                    sender=sender_identifier,
                    recipient=recipient_identifier,
                    message=alert_message,
                    message_type='outbound',
                    status='pending'
                )
                sent_count += 1

                EmergencyLog.objects.create(
                    emergency_sos=sos,
                    action_type='message_sent',
                    details={
                        'message_kind': 'sos_trigger',
                        'recipient': recipient_identifier,
                        'contact_name': ec.relationship or contact.name,
                        'message_id': str(msg.id),
                        'maps_url': maps_url,
                    }
                )
            except Exception as e:
                failed_count += 1
                EmergencyLog.objects.create(
                    emergency_sos=sos,
                    action_type='failed',
                    details={
                        'reason': 'message_send_failed',
                        'recipient': recipient_identifier,
                        'error': str(e)
                    }
                )

        EmergencyLog.objects.create(
            emergency_sos=sos,
            action_type='contact_notified',
            details={
                'message_kind': 'sos_trigger',
                'contact_count': emergency_contacts.count(),
                'sent_count': sent_count,
                'failed_count': failed_count,
            }
        )

        return sos, sent_count, failed_count

    def _send_live_location_alerts(self, request_user, sos, location):
        """Send the latest live location to all emergency contacts."""
        emergency_contacts = EmergencyContact.objects.filter(
            user=request_user
        ).select_related('contact')

        sender_identifier = self._user_identifier(request_user)
        maps_url = f"https://www.google.com/maps/search/?api=1&query={location.latitude},{location.longitude}"
        sent_count = 0
        failed_count = 0

        for ec in emergency_contacts:
            contact = ec.contact
            recipient_identifier = contact.email or contact.phone

            if not recipient_identifier:
                failed_count += 1
                EmergencyLog.objects.create(
                    emergency_sos=sos,
                    action_type='failed',
                    details={
                        'reason': 'location_message_send_failed',
                        'contact_name': contact.name,
                        'error': 'Emergency contact has no phone/email.'
                    }
                )
                continue

            location_message = (
                f"Location update from {request_user.full_name or sender_identifier}.\n"
                f"Tap to view current location: {maps_url}"
            )

            try:
                msg = SMSMessage.objects.create(
                    sender=sender_identifier,
                    recipient=recipient_identifier,
                    message=location_message,
                    message_type='outbound',
                    status='pending'
                )
                sent_count += 1

                EmergencyLog.objects.create(
                    emergency_sos=sos,
                    action_type='message_sent',
                    details={
                        'message_kind': 'live_location',
                        'recipient': recipient_identifier,
                        'contact_name': ec.relationship or contact.name,
                        'message_id': str(msg.id),
                        'maps_url': maps_url,
                    }
                )
            except Exception as e:
                failed_count += 1
                EmergencyLog.objects.create(
                    emergency_sos=sos,
                    action_type='failed',
                    details={
                        'reason': 'location_message_send_failed',
                        'recipient': recipient_identifier,
                        'error': str(e)
                    }
                )

        return emergency_contacts.count(), sent_count, failed_count
    
    def get_queryset(self):
        """
        Return only SOS requests belonging to current user.
        Include nested logs and location updates for efficiency.
        """
        return EmergencySOS.objects.filter(
            user=self.request.user
        ).prefetch_related('logs', 'location_updates')
    
    def get_serializer_class(self):
        """Use lightweight serializer for creation, full for others."""
        if self.action == 'create':
            return EmergencySOSCreateSerializer
        elif self.action in ['partial_update', 'update']:
            return EmergencySOSUpdateSerializer
        return EmergencySOSSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Trigger emergency SOS.
        
        Flow:
        1. Create EmergencySOS
        2. Log 'triggered' action
        3. Fetch emergency contacts
        4. Send alert messages to contacts
        5. Return SOS with details
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        sos, sent_count, failed_count = self._create_and_dispatch_sos(
            user=request.user,
            reason=data.get('reason', 'other'),
            description=data.get('description', ''),
            location_lat=data.get('location_lat'),
            location_lon=data.get('location_lon'),
        )
        
        # Return full SOS details
        sos_serializer = EmergencySOSSerializer(sos)
        return Response({
            'sos': sos_serializer.data,
            'notifications': {
                'messages_sent': sent_count,
                'messages_failed': failed_count,
            }
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='trigger', permission_classes=[IsAuthenticated])
    def trigger(self, request):
        """
        Smart SOS trigger endpoint.
        Requires only authenticated user. Optional payload: user_id, latitude, longitude.
        """
        user_id = request.data.get('user_id')
        if user_id and str(user_id) != str(request.user.id):
            return Response(
                {'error': 'user_id does not match authenticated user.'},
                status=status.HTTP_403_FORBIDDEN
            )

        latitude = request.data.get('latitude', None)
        longitude = request.data.get('longitude', None)

        try:
            latitude = float(latitude) if latitude not in (None, '') else None
            longitude = float(longitude) if longitude not in (None, '') else None
        except (TypeError, ValueError):
            return Response(
                {'error': 'latitude and longitude must be valid numbers.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        sos, sent_count, failed_count = self._create_and_dispatch_sos(
            user=request.user,
            reason='other',
            description='Emergency Help triggered via long press',
            location_lat=latitude,
            location_lon=longitude,
        )

        return Response({
            'id': str(sos.id),
            'status': sos.status,
            'created_at': sos.created_at,
            'messages_sent': sent_count,
            'messages_failed': failed_count,
        }, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Update SOS status (resolve or cancel).
        Automatically logs the status change.
        """
        sos = self.get_object()
        serializer = self.get_serializer(sos, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data.get('status')
        
        if new_status and new_status != sos.status:
            old_status = sos.status
            # Update resolved_at timestamp
            if new_status == 'resolved':
                sos.resolved_at = timezone.now()
            
            sos.status = new_status
            sos.save()
            
            # Log status change
            EmergencyLog.objects.create(
                emergency_sos=sos,
                action_type='resolved' if new_status == 'resolved' else 'triggered',
                details={
                    'previous_status': old_status,
                    'new_status': new_status,
                    'updated_at': timezone.now().isoformat()
                }
            )
        
        sos_data = EmergencySOSSerializer(sos).data
        return Response(sos_data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_location(self, request, pk=None):
        """
        Add location update for active emergency.
        
        Expected payload:
        {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "accuracy": 10,
            "address": "New York, NY"
        }
        """
        sos = self.get_object()
        
        # Check if SOS is still active
        if sos.status != 'active':
            return Response(
                {'error': 'Can only add location to active emergencies'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = LocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create location update
        location = serializer.save(emergency_sos=sos)
        
        # Log location update
        EmergencyLog.objects.create(
            emergency_sos=sos,
            action_type='location_updated',
            details={
                'latitude': location.latitude,
                'longitude': location.longitude,
                'accuracy': location.accuracy,
                'address': location.address
            }
        )

        # Send live location update to emergency contacts using existing messaging module.
        contact_count, sent_count, failed_count = self._send_live_location_alerts(
            request_user=request.user,
            sos=sos,
            location=location,
        )

        if contact_count > 0:
            EmergencyLog.objects.create(
                emergency_sos=sos,
                action_type='contact_notified',
                details={
                    'message_kind': 'live_location',
                    'contact_count': contact_count,
                    'sent_count': sent_count,
                    'failed_count': failed_count,
                }
            )
        
        return Response({
            'location_update': LocationUpdateSerializer(location).data,
            'notifications': {
                'contacts_found': contact_count,
                'messages_sent': sent_count,
                'messages_failed': failed_count,
            }
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def emergency_contacts(self, request, pk=None):
        """
        Get list of emergency contacts for this user.
        They will be notified in case of emergency.
        """
        emergency_contacts = EmergencyContact.objects.filter(
            user=request.user
        ).select_related('contact')
        
        contacts_data = [
            {
                'id': ec.contact.id,
                'name': ec.contact.name,
                'phone': ec.contact.phone,
                'email': ec.contact.email,
                'relationship': ec.relationship
            }
            for ec in emergency_contacts
        ]
        
        return Response({
            'count': emergency_contacts.count(),
            'emergency_contacts': contacts_data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def active(self, request):
        """
        Get list of currently active emergencies for user.
        """
        active_sos = self.get_queryset().filter(status='active')
        serializer = EmergencySOSSerializer(active_sos, many=True)
        return Response({
            'count': active_sos.count(),
            'active_emergencies': serializer.data
        })
