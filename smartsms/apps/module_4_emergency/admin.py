from django.contrib import admin
from .models import EmergencySOS, EmergencyLog, LocationUpdate


@admin.register(EmergencySOS)
class EmergencySOSAdmin(admin.ModelAdmin):
    """Admin interface for Emergency SOS."""
    list_display = ('user', 'reason', 'status', 'created_at', 'resolved_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('user__email', 'user__phone', 'description')
    readonly_fields = ('id', 'created_at', 'resolved_at')
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'user', 'reason', 'description')
        }),
        ('Location', {
            'fields': ('location_lat', 'location_lon')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'resolved_at')
        }),
    )


@admin.register(EmergencyLog)
class EmergencyLogAdmin(admin.ModelAdmin):
    """Admin interface for Emergency Logs."""
    list_display = ('emergency_sos', 'action_type', 'created_at')
    list_filter = ('action_type', 'created_at')
    search_fields = ('emergency_sos__user__email', 'details')
    readonly_fields = ('id', 'created_at')


@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    """Admin interface for Location Updates."""
    list_display = ('emergency_sos', 'latitude', 'longitude', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('emergency_sos__user__email', 'address')
    readonly_fields = ('id', 'created_at')
