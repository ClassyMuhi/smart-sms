# Django signals for contact management

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Contact, EmergencyContact


@receiver(pre_delete, sender=Contact)
def contact_pre_delete(sender, instance, **kwargs):
    """
    Signal handler before contact deletion.
    
    Currently just logs - could be extended for:
    - Backup data before deletion
    - Trigger notifications
    - Audit logging
    """
    # Could add audit logging here
    pass
