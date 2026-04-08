from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.module_1_auth.models import CustomUser
from .models import SMSMessage, DeliveryStatus, MessageTemplate


def create_user(phone, email):
    user = CustomUser.objects.create(phone=phone, email=email, full_name="Msg User", is_phone_verified=True)
    user.set_password("StrongPass123!")
    user.save()
    return user


class MessagingModelTests(TestCase):
    def test_create_message_template(self):
        template = MessageTemplate.objects.create(
            name="OTP",
            content="Your OTP is {{code}}",
            variables=["code"],
        )
        assert str(template) == "OTP"


class MessagingAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user("9876543330", "msg1@example.com")
        self.client.force_authenticate(user=self.user)

    def test_send_message_creates_delivery_status(self):
        payload = {
            "sender": "ignored",
            "recipient": "9876543999",
            "message": "Hello from tests",
            "message_type": "outbound",
            "status": "pending",
        }
        response = self.client.post("/api/messaging/messages/", payload)

        assert response.status_code == status.HTTP_201_CREATED
        message_id = response.data["id"]
        message = SMSMessage.objects.get(id=message_id)
        assert message.sender == self.user.phone
        assert DeliveryStatus.objects.filter(message=message).exists()

    def test_list_only_current_user_messages(self):
        SMSMessage.objects.create(
            sender=self.user.phone,
            recipient="9000000001",
            message="Mine",
            message_type="outbound",
            status="sent",
        )
        SMSMessage.objects.create(
            sender="9999999999",
            recipient="9000000002",
            message="Other",
            message_type="outbound",
            status="sent",
        )

        response = self.client.get("/api/messaging/messages/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["sender"] == self.user.phone

    def test_message_delivery_status_endpoint(self):
        message = SMSMessage.objects.create(
            sender=self.user.phone,
            recipient="9000000003",
            message="Track me",
            message_type="outbound",
            status="pending",
        )
        DeliveryStatus.objects.create(message=message, status="queued")

        response = self.client.get(f"/api/messaging/messages/{message.id}/delivery_status/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "queued"
