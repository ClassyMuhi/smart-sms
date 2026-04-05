from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, OTPVerification, UserLoginHistory


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin interface for CustomUser model."""
    
    fieldsets = (
        (None, {'fields': ('id', 'phone', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email')}),
        ('Verification', {'fields': ('is_phone_verified',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login_at', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'email', 'full_name', 'password1', 'password2'),
        }),
    )
    
    list_display = ('phone', 'full_name', 'email', 'is_phone_verified', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_phone_verified', 'created_at')
    search_fields = ('phone', 'email', 'full_name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_login_at')


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    """Admin interface for OTPVerification model."""
    
    list_display = ('user', 'purpose', 'otp_code', 'is_verified', 'created_at', 'expires_at', 'is_expired_display')
    list_filter = ('purpose', 'is_verified', 'created_at')
    search_fields = ('user__phone', 'user__email', 'otp_code')
    readonly_fields = ('id', 'user', 'otp_code', 'created_at', 'expires_at', 'verified_at')
    ordering = ('-created_at',)
    
    def is_expired_display(self, obj):
        """Display if OTP is expired."""
        return obj.is_expired()
    is_expired_display.boolean = True
    is_expired_display.short_description = 'Is Expired'
    
    def has_add_permission(self, request):
        """Prevent manual creation of OTP records."""
        return False


@admin.register(UserLoginHistory)
class UserLoginHistoryAdmin(admin.ModelAdmin):
    """Admin interface for UserLoginHistory model."""
    
    list_display = ('user', 'ip_address', 'login_at')
    list_filter = ('login_at', 'user')
    search_fields = ('user__phone', 'user__email', 'ip_address')
    readonly_fields = ('id', 'user', 'ip_address', 'user_agent', 'login_at')
    ordering = ('-login_at',)
    
    def has_add_permission(self, request):
        """Prevent manual creation of login history."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing login history."""
        return False
