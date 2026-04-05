import random
import string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def generate_otp(length=None):
    """
    Generate a random OTP of specified length.
    
    Args:
        length: Length of OTP (default from settings.OTP_LENGTH)
    
    Returns:
        str: Random OTP code
    """
    if length is None:
        length = getattr(settings, 'OTP_LENGTH', 6)
    
    return ''.join(random.choices(string.digits, k=length))


def send_otp_sms(phone, otp_code):
    """
    Send OTP via SMS.
    In production, integrate with SMS gateway like Twilio, AWS SNS, etc.
    
    Args:
        phone: User's phone number
        otp_code: OTP code to send
    
    Returns:
        bool: True if sent successfully
    """
    # TODO: Integrate with actual SMS gateway
    # Example with Twilio:
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    #     body=f"Your OTP is: {otp_code}. Valid for 5 minutes.",
    #     from_="+1234567890",
    #     to=phone
    # )
    
    logger.info(f"SMS to {phone}: OTP = {otp_code}")
    print(f"[SMS] To: {phone} | Message: Your OTP is {otp_code}. Valid for 5 minutes.")
    return True


def send_otp_email(email, otp_code, full_name="User"):
    """
    Send OTP via Email.
    In production, integrate with email service.
    
    Args:
        email: User's email address
        otp_code: OTP code to send
        full_name: User's full name
    
    Returns:
        bool: True if sent successfully
    """
    # TODO: Integrate with email service (Django Mail, SendGrid, AWS SES, etc.)
    # Example:
    # from django.core.mail import send_mail
    # send_mail(
    #     'Your Smart SMS OTP',
    #     f'Hi {full_name},\n\nYour OTP is: {otp_code}\nValid for 5 minutes.',
    #     'noreply@smartsms.com',
    #     [email],
    #     fail_silently=False,
    # )
    
    logger.info(f"Email to {email}: OTP = {otp_code}")
    print(f"[EMAIL] To: {email} | Subject: Your OTP | Message: Hi {full_name}, Your OTP is {otp_code}")
    return True


def send_welcome_email(email, full_name):
    """
    Send welcome email after successful registration.
    
    Args:
        email: User's email address
        full_name: User's full name
    
    Returns:
        bool: True if sent successfully
    """
    logger.info(f"Welcome email sent to {email}")
    print(f"[EMAIL] Welcome email sent to {email}")
    return True


def send_password_reset_confirmation(email, full_name):
    """
    Send password reset confirmation email.
    
    Args:
        email: User's email address
        full_name: User's full name
    
    Returns:
        bool: True if sent successfully
    """
    logger.info(f"Password reset confirmation sent to {email}")
    print(f"[EMAIL] Password reset confirmation sent to {email}")
    return True
