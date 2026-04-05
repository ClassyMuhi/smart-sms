import re
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from apps.module_1_auth.models import CustomUser


def normalize_phone(phone):
    """
    Normalize phone number:
    - Remove +91, +1, country codes
    - Remove spaces, hyphens, parentheses
    - Keep only digits
    
    Example: "+91 98765 43210" → "98765 43210"
    """
    if not phone:
        return phone
    
    # Remove common country codes
    phone = re.sub(r'^\+?91|^\+?1\s?', '', str(phone).strip())
    
    # Remove spaces and hyphens
    phone = re.sub(r'[\s\-\(\)]+', '', phone)
    
    return phone


def validate_phone(phone):
    """
    Validate phone number format.
    Must be 9-15 digits.
    """
    normalized = normalize_phone(phone)
    
    # Check if it's only digits and proper length
    if not re.match(r'^\d{9,15}$', normalized):
        raise ValidationError(
            'Phone number must be 9-15 digits. Format: +91 98765 43210 or 9876543210'
        )


class Contact(models.Model):
    """
    Contact model for storing user's contacts.
    
    Fields:
    - id: UUID primary key (unique identifier)
    - user: ForeignKey to CustomUser (who owns this contact)
    - name: Contact person's full name (searchable)
    - phone: Contact phone number (normalized and searchable)
    - email: Optional email address
    - created_at: Auto timestamp when created
    - updated_at: Auto timestamp when modified
    
    Constraints:
    - (user, phone) must be unique - no duplicate contacts per user
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for contact"
    )
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='contacts',
        help_text="User who owns this contact"
    )
    
    name = models.CharField(
        max_length=150,
        db_index=True,  # Index for name search
        help_text="Contact person's name"
    )
    
    phone = models.CharField(
        max_length=20,
        validators=[validate_phone],
        db_index=True,  # Index for phone search
        help_text="Normalized phone number"
    )
    
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Contact email (optional)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,  # For sorting by creation
        help_text="When this contact was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    
    class Meta:
        # Ensure no duplicate contacts per user
        unique_together = [['user', 'phone']]
        
        # Index for efficient queries by user and creation time
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'name']),
        ]
        
        ordering = ['-created_at']
        verbose_name_plural = "Contacts"
    
    def save(self, *args, **kwargs):
        """Override save to normalize phone number before storing."""
        self.phone = normalize_phone(self.phone)
        validate_phone(self.phone)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.phone})"


class EmergencyContact(models.Model):
    """
    Emergency Contact model - marks specific contacts as emergency contacts.
    
    This is a separate model that links users to their emergency contacts.
    A user can have multiple emergency contacts.
    
    Fields:
    - id: UUID primary key
    - user: ForeignKey to CustomUser (whose emergency contact)
    - contact: ForeignKey to Contact (the emergency contact)
    - relationship: Description of relationship (e.g., "Mother", "Doctor")
    - created_at: When marked as emergency contact
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='emergency_contacts',
        help_text="User who has this emergency contact"
    )
    
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='as_emergency_for',
        help_text="Contact marked as emergency"
    )
    
    relationship = models.CharField(
        max_length=100,
        blank=True,
        help_text="Relationship to user (e.g., Mother, Doctor, Friend)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When marked as emergency contact"
    )
    
    class Meta:
        # A contact can be emergency contact multiple times? No!
        # Each contact is emergency contact only once per user
        unique_together = [['user', 'contact']]
        
        ordering = ['created_at']
        verbose_name_plural = "Emergency Contacts"
    
    def clean(self):
        """Validate that contact belongs to the same user."""
        if self.contact.user != self.user:
            raise ValidationError(
                "Emergency contact must belong to the same user."
            )
    
    def __str__(self):
        return f"{self.contact.name} (Emergency for {self.user.phone})"
