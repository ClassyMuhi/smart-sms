from django.contrib import admin
from .models import SMSMessage, DeliveryStatus, MessageTemplate


@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'status', 'message_type', 'created_at')
    list_filter = ('status', 'message_type', 'created_at')
    search_fields = ('recipient', 'sender', 'message')
    readonly_fields = ('id', 'created_at', 'updated_at', 'sent_at')
    
    fieldsets = (
        ('Message Info', {
            'fields': ('id', 'sender', 'recipient', 'message')
        }),
        ('Status', {
            'fields': ('status', 'message_type')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'sent_at')
        }),
        ('Metadata', {
            'fields': ('message_id', 'characters_count', 'segments_count')
        }),
    )


@admin.register(DeliveryStatus)
class DeliveryStatusAdmin(admin.ModelAdmin):
    list_display = ('message', 'status', 'delivery_timestamp', 'last_checked')
    list_filter = ('status', 'delivery_timestamp')
    search_fields = ('message__recipient', 'error_code')
    readonly_fields = ('id', 'last_checked')
    
    fieldsets = (
        ('Delivery Info', {
            'fields': ('id', 'message', 'status', 'status_description')
        }),
        ('Details', {
            'fields': ('delivery_timestamp', 'error_code', 'cost')
        }),
        ('Tracking', {
            'fields': ('last_checked', 'check_count')
        }),
    )


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'content')
    readonly_fields = ('id', 'created_at', 'updated_at')
