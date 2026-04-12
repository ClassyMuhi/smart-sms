import uuid
from django.db import models
from django.utils import timezone
from apps.module_1_auth.models import CustomUser
from apps.module_3_contacts.models import Contact


class EmergencySOS(models.Model):
    """
    Emergency SOS Trigger Model.
    
    Stores emergency SOS activations by users. Each trigger automatically:
    - Fetches emergency contacts
    - Sends emergency alerts via messaging
    - Starts location tracking
    
    Fields:
    - id: UUID primary key
    - user: ForeignKey to CustomUser (who triggered SOS)
    - reason: Emergency reason/description
    - status: Current status (active, resolved, cancelled)
    - location_lat/lon: User's location when SOS triggered
    - created_at: When SOS was triggered
    - resolved_at: When emergency ended
    """
    
    STATUS_CHOICES = [
        ('active', 'Active - Emergency ongoing'),
        ('resolved', 'Resolved - Emergency ended'),
        ('cancelled', 'Cancelled - False alarm'),
    ]
    
    REASON_CHOICES = [
        ('medical', 'Medical Emergency'),
        ('accident', 'Accident'),
        ('fire', 'Fire'),
        ('theft', 'Theft/Crime'),
        ('lost', 'Lost/Missing'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique SOS trigger ID"
    )
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='emergency_sos',
        help_text="User who triggered SOS"
    )
    
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        default='other',
        help_text="Type of emergency"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Additional details about emergency"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,
        help_text="Current emergency status"
    )
    
    # Location when SOS triggered
    location_lat = models.FloatField(
        null=True,
        blank=True,
        help_text="Latitude of user at SOS trigger"
    )
    location_lon = models.FloatField(
        null=True,
        blank=True,
        help_text="Longitude of user at SOS trigger"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When SOS was triggered"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When emergency was resolved"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
        verbose_name = "Emergency SOS"
        verbose_name_plural = "Emergency SOS"
    
    def __str__(self):
        return f"SOS {self.reason} - {self.user.email or self.user.phone} - {self.status}"


class EmergencyLog(models.Model):
    """
    Emergency Action Log Model.
    
    Tracks every action taken during an emergency:
    - Emergency triggered
    - Contacts notified
    - Messages sent
    - Location updated
    
    Fields:
    - id: UUID
    - emergency_sos: ForeignKey to EmergencySOS
    - action_type: Type of action (triggered, contact_notified, message_sent, location_updated, resolved)
    - details: JSON-like description of what happened
    - created_at: When action occurred
    """
    
    ACTION_CHOICES = [
        ('triggered', 'SOS Triggered'),
        ('contact_notified', 'Emergency Contact Notified'),
        ('message_sent', 'Alert Message Sent'),
        ('location_updated', 'Location Updated'),
        ('resolved', 'Emergency Resolved'),
        ('failed', 'Action Failed'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    emergency_sos = models.ForeignKey(
        EmergencySOS,
        on_delete=models.CASCADE,
        related_name='logs',
        help_text="Associated emergency SOS"
    )
    
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text="Type of action performed"
    )
    
    details = models.JSONField(
        default=dict,
        help_text="Additional details about action (who, what, result)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When action was performed"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['emergency_sos', '-created_at']),
            models.Index(fields=['action_type']),
        ]
        verbose_name = "Emergency Log"
        verbose_name_plural = "Emergency Logs"
    
    def __str__(self):
        return f"{self.action_type} - {self.emergency_sos.id}"


class LocationUpdate(models.Model):
    """
    Live Location Update Model.
    
    Stores real-time location updates during active emergency.
    Enables tracking of person in distress.
    
    Fields:
    - id: UUID
    - emergency_sos: ForeignKey to EmergencySOS
    - latitude: GPS latitude
    - longitude: GPS longitude
    - accuracy: Location accuracy in meters
    - address: Human-readable address (optional)
    - created_at: When location was received
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    emergency_sos = models.ForeignKey(
        EmergencySOS,
        on_delete=models.CASCADE,
        related_name='location_updates',
        help_text="Associated emergency SOS"
    )
    
    latitude = models.FloatField(
        help_text="GPS latitude coordinate"
    )
    
    longitude = models.FloatField(
        help_text="GPS longitude coordinate"
    )
    
    accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text="Location accuracy in meters"
    )
    
    address = models.CharField(
        max_length=255,
        blank=True,
        help_text="Human-readable address"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When location was recorded"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['emergency_sos', '-created_at']),
        ]
        verbose_name = "Location Update"
        verbose_name_plural = "Location Updates"
    
    def __str__(self):
        return f"Location {self.latitude}, {self.longitude} - SOS {self.emergency_sos.id}"
