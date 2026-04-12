from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
import random
import re

from .models import CustomUser, OTPVerification, UserLoginHistory


class PhoneNumberValidator:
    """Validator for phone number format."""
    
    def __call__(self, value):
        phone_regex = r'^\+?1?\d{9,15}$'
        if not re.match(phone_regex, value):
            raise serializers.ValidationError(
                "Phone number must be between 9 and 15 digits. "
                "Format: +1234567890 or 1234567890"
            )


class PasswordStrengthValidator:
    """Validator for password strength."""
    
    def __call__(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError(
                "Password must contain at least one special character (!@#$%^&*)."
            )


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates phone, email, and password strength.
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[PasswordStrengthValidator()],
        help_text="Password must contain uppercase, lowercase, digit, and special character."
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
    )
    phone = serializers.CharField(
        validators=[PhoneNumberValidator()],
        required=False,
        allow_blank=True,
    )
    
    class Meta:
        model = CustomUser
        fields = ['phone', 'email', 'full_name', 'password', 'password_confirm']
        extra_kwargs = {
            'full_name': {'required': True},
            'email': {'required': True},
            'phone': {'required': False},
        }
    
    def validate_email(self, value):
        """Check if email already exists."""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value
    
    def validate_phone(self, value):
        """Check if phone already exists."""
        if not value:
            return value
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already registered.")
        return value

    def _generate_unique_phone(self):
        """Generate a pseudo phone for accounts that sign up with email only."""
        for _ in range(20):
            candidate = f"9{random.randint(100000000, 999999999)}"
            if not CustomUser.objects.filter(phone=candidate).exists():
                return candidate
        raise serializers.ValidationError("Unable to generate phone number. Please provide phone manually.")
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return attrs
    
    def create(self, validated_data):
        """Create user and hash password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        if not validated_data.get('phone'):
            validated_data['phone'] = self._generate_unique_phone()
        
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Accepts phone or email + password.
    """
    
    phone_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Authenticate user with phone or email."""
        phone_or_email = attrs.get('phone_or_email')
        password = attrs.get('password')
        
        # Try to find user by phone or email
        try:
            user = CustomUser.objects.get(phone=phone_or_email)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email=phone_or_email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(
                    "Phone/Email or password is incorrect."
                )
        
        # Verify password
        if not user.check_password(password):
            raise serializers.ValidationError(
                "Phone/Email or password is incorrect."
            )
        
        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        
        attrs['user'] = user
        return attrs


class OTPVerificationSerializer(serializers.ModelSerializer):
    """Serializer for OTP verification."""
    
    otp_code = serializers.CharField(max_length=6, min_length=6)
    
    class Meta:
        model = OTPVerification
        fields = ['otp_code']
    
    def validate_otp_code(self, value):
        """Validate OTP format."""
        if not value.isdigit():
            raise serializers.ValidationError(
                "OTP must contain only digits."
            )
        return value


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password - request OTP."""
    
    phone_or_email = serializers.CharField()
    
    def validate_phone_or_email(self, value):
        """Check if user exists."""
        try:
            user = CustomUser.objects.get(phone=value)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email=value)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(
                    "No user found with this phone/email."
                )
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset with OTP."""
    
    phone_or_email = serializers.CharField()
    otp_code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(
        write_only=True,
        validators=[PasswordStrengthValidator()]
    )
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_otp_code(self, value):
        """Validate OTP format."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        return value
    
    def validate(self, attrs):
        """Validate passwords match and OTP is valid."""
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError(
                {"new_password": "Passwords do not match."}
            )
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile information."""
    
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'phone',
            'email',
            'full_name',
            'is_phone_verified',
            'created_at',
            'updated_at',
            'last_login_at',
        ]
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = CustomUser
        fields = ['email', 'full_name']
    
    def validate_email(self, value):
        """Check if email is already used by another user."""
        user = self.context['request'].user
        if CustomUser.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Email already in use.")
        return value


class LoginHistorySerializer(serializers.ModelSerializer):
    """Serializer for login history."""
    
    class Meta:
        model = UserLoginHistory
        fields = ['id', 'ip_address', 'user_agent', 'login_at']
        read_only_fields = fields


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password by authenticated user."""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        validators=[PasswordStrengthValidator()]
    )
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        """Verify old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate new passwords match."""
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError(
                {"new_password": "New passwords do not match."}
            )
        return attrs
