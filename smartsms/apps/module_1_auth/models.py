from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid


class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Includes phone number as primary identifier for SMS-based authentication.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None  # Remove username field
    email = models.EmailField(unique=True, blank=True, null=True)
    
    # Phone number with validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='Phone number must be between 9 and 15 digits and may start with +.'
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=15,
        unique=True,
        help_text='Phone number format: +1234567890 or 1234567890'
    )
    
    full_name = models.CharField(max_length=255, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
    # Custom related names to avoid conflicts with default User model
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='customuser_set'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='customuser_permission_set'
    )
    
    USERNAME_FIELD = 'phone'  # Use phone as username for authentication
    REQUIRED_FIELDS = ['email', 'full_name']  # Required fields for createsuperuser
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.phone})"
    
    def get_full_name(self):
        """Return the user's full name."""
        return self.full_name.strip()
    
    def get_short_name(self):
        """Return the user's short name."""
        return self.full_name.split()[0] if self.full_name else 'User'


class OTPVerification(models.Model):
    """
    Model to store OTP verification records.
    Handles OTP generation, storage, and expiry for user authentication.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='otp_verification'
    )
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(
        max_length=20,
        choices=[
            ('registration', 'Registration'),
            ('phone_verification', 'Phone Verification'),
            ('password_reset', 'Password Reset'),
            ('login', 'Login'),
        ],
        default='registration'
    )
    
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    # Track attempts to prevent brute force
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['otp_code']),
        ]
    
    def __str__(self):
        return f"OTP for {self.user} - {self.purpose}"
    
    def is_expired(self):
        """Check if OTP has expired."""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def is_valid_for_verification(self):
        """Check if OTP is still valid for verification."""
        return not self.is_expired() and self.attempts < self.max_attempts


class UserLoginHistory(models.Model):
    """
    Model to track user login history for security monitoring.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='login_history'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    login_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-login_at']
        verbose_name_plural = 'User Login Histories'
        indexes = [
            models.Index(fields=['user', '-login_at']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.login_at}"
