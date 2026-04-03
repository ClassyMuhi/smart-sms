from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserLoginHistory
from .utils import send_welcome_email
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def user_created_signal(sender, instance, created, **kwargs):
    """Signal handler for new user creation."""
    if created:
        logger.info(f"New user created: {instance.phone}")
        # Optionally send welcome email
        # send_welcome_email(instance.email, instance.full_name)
