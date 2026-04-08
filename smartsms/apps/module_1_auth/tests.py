from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CustomUser, OTPVerification, UserLoginHistory


class AuthModelTests(TestCase):
    def test_otp_expiry_check(self):
        user = CustomUser.objects.create(phone="9876543000", email="u1@example.com", full_name="User One")
        user.set_password("StrongPass123!")
        user.save()

        expired = OTPVerification.objects.create(
            user=user,
            otp_code="123456",
            purpose="registration",
            expires_at=timezone.now() - timezone.timedelta(minutes=1),
        )
        assert expired.is_expired() is True


class AuthAPITests(APITestCase):
    def test_register_creates_user_and_otp(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "phone": "+919876543220",
                "email": "newuser@example.com",
                "full_name": "New User",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        user = CustomUser.objects.get(phone="+919876543220")
        assert OTPVerification.objects.filter(user=user, purpose="registration").exists()

    def test_verify_otp_marks_phone_verified(self):
        user = CustomUser.objects.create(phone="9876543221", email="otp@example.com", full_name="OTP User")
        user.set_password("StrongPass123!")
        user.save()

        OTPVerification.objects.create(
            user=user,
            otp_code="111222",
            purpose="registration",
            expires_at=timezone.now() + timezone.timedelta(minutes=5),
        )

        response = self.client.post(
            "/api/auth/verify_otp/",
            {"user_id": str(user.id), "otp_code": "111222"},
        )

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_phone_verified is True

    def test_login_requires_verified_phone(self):
        user = CustomUser.objects.create(phone="9876543222", email="login1@example.com", full_name="Login User")
        user.set_password("StrongPass123!")
        user.is_phone_verified = False
        user.save()

        response = self.client.post(
            "/api/auth/login/",
            {"phone_or_email": "9876543222", "password": "StrongPass123!"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_login_returns_tokens_and_records_history(self):
        user = CustomUser.objects.create(phone="9876543223", email="login2@example.com", full_name="Verified User")
        user.set_password("StrongPass123!")
        user.is_phone_verified = True
        user.save()

        response = self.client.post(
            "/api/auth/login/",
            {"phone_or_email": "9876543223", "password": "StrongPass123!"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert UserLoginHistory.objects.filter(user=user).count() == 1
