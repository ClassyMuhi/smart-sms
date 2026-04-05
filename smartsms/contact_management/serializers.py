from rest_framework import serializers
from django.db import IntegrityError
from .models import Contact, EmergencyContact, normalize_phone, validate_phone


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for Contact model.
    
    Handles:
    - Validation of phone number format
    - Normalization of phone numbers
    - Read-only fields (id, created_at, updated_at)
    - User is automatically set from request
    """
    
    # Phone field with custom validation
    phone = serializers.CharField(
        write_only=True,  # Only accept on input, don't return
        help_text="Phone number (will be normalized)"
    )
    
    # Display normalized phone on response
    phone_display = serializers.CharField(
        source='phone',
        read_only=True,
        help_text="Normalized phone number"
    )
    
    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone', 'phone_display', 'email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {
                'help_text': 'Contact name (required)',
                'error_messages': {
                    'blank': 'Name cannot be empty',
                    'max_length': 'Name must be less than 150 characters'
                }
            },
            'email': {
                'help_text': 'Contact email (optional)'
            }
        }
    
    def validate_phone(self, value):
        """
        Validate and normalize phone number.
        
        - Remove country codes
        - Remove spaces and special chars
        - Ensure proper format
        """
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        
        # Validate format
        try:
            validate_phone(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        
        # Normalize for storage
        normalized = normalize_phone(value)
        
        # Check for duplicates (user can't have duplicate phone numbers)
        user = self.context.get('request').user
        
        # If updating, exclude the current contact
        contact_id = self.instance.id if self.instance else None
        
        duplicate = Contact.objects.filter(
            user=user,
            phone=normalized
        ).exclude(id=contact_id).exists()
        
        if duplicate:
            raise serializers.ValidationError(
                f"You already have a contact with phone {normalized}."
            )
        
        return normalized
    
    def validate_name(self, value):
        """Validate name field."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        
        return value.strip()
    
    def validate_email(self, value):
        """Validate email if provided."""
        if value:
            # Email validation is handled by Django's EmailField
            return value.lower().strip()
        return value
    
    def create(self, validated_data):
        """Create contact (user set by viewset.perform_create)."""
        return super().create(validated_data)


class EmergencyContactSerializer(serializers.ModelSerializer):
    """
    Serializer for EmergencyContact model.
    
    Allows users to mark specific contacts as emergency contacts.
    """
    
    # Display nested contact details
    contact_detail = ContactSerializer(
        source='contact',
        read_only=True,
        help_text="Full contact details"
    )
    
    class Meta:
        model = EmergencyContact
        fields = ['id', 'contact', 'contact_detail', 'relationship', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'contact': {
                'help_text': 'Contact ID to mark as emergency',
                'write_only': True
            },
            'relationship': {
                'help_text': 'Relationship to user (e.g., Mother, Doctor)',
                'required': False
            }
        }
    
    def validate_contact(self, value):
        """Ensure contact belongs to the requesting user."""
        user = self.context['request'].user
        
        if value.user != user:
            raise serializers.ValidationError(
                "You can only add your own contacts as emergency contacts."
            )
        
        return value
    
    def create(self, validated_data):
        """Create emergency contact association (user set by viewset)."""
        # Check if already exists
        if EmergencyContact.objects.filter(
            user=self.context['request'].user,
            contact=validated_data['contact']
        ).exists():
            raise serializers.ValidationError(
                "This contact is already marked as an emergency contact."
            )
        
        return super().create(validated_data)


class ContactSearchSerializer(serializers.Serializer):
    """
    Serializer for contact search/filter query parameters.
    
    Allows filtering by:
    - name: Partial name match (case-insensitive)
    - phone: Partial phone match
    """
    
    name = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Search contacts by name (partial match)"
    )
    
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Search contacts by phone (partial match)"
    )
    
    def validate_phone(self, value):
        """Normalize phone if provided for search."""
        if value:
            return normalize_phone(value)
        return value
