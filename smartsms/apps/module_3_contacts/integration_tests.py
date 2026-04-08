from rest_framework import status
from rest_framework.test import APITestCase

from apps.module_1_auth.models import CustomUser, OTPVerification
from apps.module_2_messaging.models import DeliveryStatus, SMSMessage


class ThreeModuleIntegrationTests(APITestCase):
    def test_auth_contacts_messaging_flow(self):
        register_payload = {
            "phone": "9876543555",
            "email": "flow@example.com",
            "full_name": "Flow User",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
        }
        reg_response = self.client.post("/api/auth/register/", register_payload)
        assert reg_response.status_code == status.HTTP_201_CREATED

        user = CustomUser.objects.get(phone="9876543555")
        otp = OTPVerification.objects.get(user=user, purpose="registration")

        verify_response = self.client.post(
            "/api/auth/verify_otp/",
            {"user_id": str(user.id), "otp_code": otp.otp_code},
        )
        assert verify_response.status_code == status.HTTP_200_OK

        login_response = self.client.post(
            "/api/auth/login/",
            {"phone_or_email": "9876543555", "password": "StrongPass123!"},
        )
        assert login_response.status_code == status.HTTP_200_OK
        access = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        contact_response = self.client.post(
            "/api/contacts/contacts/",
            {
                "name": "Receiver",
                "phone": "+91 98765 49999",
                "email": "receiver@example.com",
            },
        )
        assert contact_response.status_code == status.HTTP_201_CREATED
        recipient_phone = contact_response.data["phone_display"]

        send_response = self.client.post(
            "/api/messaging/messages/",
            {
                "sender": "ignored",
                "recipient": recipient_phone,
                "message": "Integrated message",
                "message_type": "outbound",
                "status": "pending",
            },
        )
        assert send_response.status_code == status.HTTP_201_CREATED

        sent_message = SMSMessage.objects.get(id=send_response.data["id"])
        assert sent_message.sender == "9876543555"
        assert sent_message.recipient == recipient_phone
        assert DeliveryStatus.objects.filter(message=sent_message).exists()
