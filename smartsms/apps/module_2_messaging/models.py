from django.db import models
from django.utils import timezone
import uuid


class SMSMessage(models.Model):
    """
    Model for storing SMS messages sent and received.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('received', 'Received'),
    ]
    
    MESSAGE_TYPE_CHOICES = [
        ('outbound', 'Outbound'),
        ('inbound', 'Inbound'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.CharField(max_length=255)  # Phone or email
    recipient = models.CharField(max_length=255)  # Phone or email
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    message_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Provider ID
    characters_count = models.IntegerField(null=True, blank=True)
    segments_count = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', '-created_at']),
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"SMS to {self.recipient} - {self.status}"


class DeliveryStatus(models.Model):
    """
    Track SMS delivery status and reports.
    """
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('accepted', 'Accepted'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('undelivered', 'Undelivered'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.OneToOneField(SMSMessage, on_delete=models.CASCADE, related_name='delivery_status')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    status_description = models.TextField(blank=True)
    
    # Delivery info
    delivery_timestamp = models.DateTimeField(null=True, blank=True)
    error_code = models.CharField(max_length=100, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # Tracking
    last_checked = models.DateTimeField(auto_now=True)
    check_count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Delivery Statuses"
        ordering = ['-delivery_timestamp']
    
    def __str__(self):
        return f"Delivery: {self.message.recipient} - {self.status}"


class MessageTemplate(models.Model):
    """
    Pre-defined message templates for quick messaging.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content = models.TextField()
    variables = models.JSONField(default=list, blank=True)  # Variables like {{name}}, {{code}}
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
