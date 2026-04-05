from django.contrib import admin
from django.utils.html import format_html
from .models import Contact, EmergencyContact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin interface for managing contacts.
    
    Features:
    - Display contacts organized by user
    - Search by name or phone
    - Filter by creation date
    - Read-only fields for system data
    """
    
    list_display = [
        'name',
        'phone_display',
        'user_phone',
        'email',
        'created_at_display'
    ]
    
    list_filter = [
        'created_at',
        'user__phone',
    ]
    
    search_fields = [
        'name',
        'phone',
        'user__phone',
        'email'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'phone_display'
    ]
    
    fieldsets = (
        ('Contact Info', {
            'fields': ('id', 'name', 'phone', 'phone_display', 'email')
        }),
        ('User', {
            'fields': ('user',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def phone_display(self, obj):
        """Display normalized phone with formatting."""
        return format_html(
            '<span style="font-family: monospace;">+{}</span>',
            obj.phone
        )
    phone_display.short_description = 'Phone (Normalized)'
    
    def user_phone(self, obj):
        """Display user's phone number."""
        return obj.user.phone
    user_phone.short_description = 'User Phone'
    
    def created_at_display(self, obj):
        """Display creation date in readable format."""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = 'Added On'
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    """
    Admin interface for emergency contacts.
    
    Readonly interface - allows viewing but not direct modification.
    Edit through Contact admin instead.
    """
    
    list_display = [
        'contact_name',
        'relationship',
        'user_phone',
        'phone_display',
        'created_at_display'
    ]
    
    list_filter = [
        'created_at',
        'user__phone',
    ]
    
    search_fields = [
        'contact__name',
        'contact__phone',
        'user__phone',
        'relationship'
    ]
    
    readonly_fields = [
        'id',
        'user',
        'contact',
        'created_at',
        'contact_details'
    ]
    
    fieldsets = (
        ('Emergency Contact', {
            'fields': ('id', 'user', 'contact', 'contact_details')
        }),
        ('Relationship', {
            'fields': ('relationship',)
        }),
        ('Created', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent adding through admin (use API instead)."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion through admin."""
        return True
    
    def contact_name(self, obj):
        """Display contact name."""
        return obj.contact.name
    contact_name.short_description = 'Contact Name'
    
    def phone_display(self, obj):
        """Display normalized phone."""
        return format_html(
            '<span style="font-family: monospace;">+{}</span>',
            obj.contact.phone
        )
    phone_display.short_description = 'Phone'
    
    def user_phone(self, obj):
        """Display user's phone."""
        return obj.user.phone
    user_phone.short_description = 'User Phone'
    
    def created_at_display(self, obj):
        """Display creation timestamp."""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = 'Added On'
    
    def contact_details(self, obj):
        """Show full contact details."""
        return format_html(
            '<strong>Name:</strong> {}<br>'
            '<strong>Phone:</strong> +{}<br>'
            '<strong>Email:</strong> {}<br>'
            '<strong>Created:</strong> {}',
            obj.contact.name,
            obj.contact.phone,
            obj.contact.email or 'Not set',
            obj.contact.created_at.strftime('%Y-%m-%d %H:%M:%S')
        )
    contact_details.short_description = 'Contact Information'
    
    def get_queryset(self, request):
        """Optimize queries."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'contact')
