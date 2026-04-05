# Module 2: Messaging (SMS Core)

**Location:** `smartsms/apps/module_2_messaging/`

---

## 📌 Overview

Module 2 is the core SMS messaging system. It handles sending SMS messages, receiving inbound messages, tracking delivery status, and managing message templates.

## 🗂️ Folder Structure

```
module_2_messaging/
├── __init__.py
├── admin.py                    # Django admin configurations
├── apps.py                     # App configuration
├── models.py                   # Database models (SMSMessage, DeliveryStatus, etc.)
├── serializers.py              # DRF serializers for messages
├── views.py                    # API endpoints and viewsets
├── urls.py                     # URL routing
├── migrations/                 # Database migrations
```

## 📊 Database Models

### SMSMessage Model
```python
{
    "id": "uuid",
    "sender": "+1234567890",
    "recipient": "+0987654321",
    "message": "Hello, this is a test message!",
    "message_type": "outbound",  # or "inbound"
    "status": "sent",
    "created_at": "2024-04-05T10:30:00Z",
    "updated_at": "2024-04-05T10:30:30Z",
    "sent_at": "2024-04-05T10:30:05Z",
    "characters_count": 32,
    "segments_count": 1,
    "message_id": "twilio_1234567890"
}
```

**Status Values:**
- `draft` - Message saved but not sent
- `pending` - Queued for sending
- `sending` - Currently being transmitted
- `sent` - Successfully sent
- `failed` - Delivery failed
- `received` - Inbound message received

### DeliveryStatus Model
```python
{
    "id": "uuid",
    "message_id": "message_uuid",
    "status": "delivered",
    "status_description": "Message delivered successfully",
    "delivery_timestamp": "2024-04-05T10:30:10Z",
    "error_code": null,
    "cost": "0.0050",
    "last_checked": "2024-04-05T10:35:00Z",
    "check_count": 1
}
```

**Status Values:**
- `queued` - Waiting to be sent
- `accepted` - Provider accepted the message
- `sent` - Sent by provider
- `delivered` - Delivered to recipient
- `failed` - Delivery failed
- `undelivered` - Unable to deliver
- `rejected` - Provider rejected

### MessageTemplate Model
```python
{
    "id": "uuid",
    "name": "Welcome Message",
    "description": "New user welcome SMS",
    "content": "Welcome {{name}}! Your verification code is {{code}}.",
    "variables": ["name", "code"],
    "is_active": true,
    "created_at": "2024-04-05T10:00:00Z"
}
```

---

## 🔌 API Endpoints

### 1. Send SMS Message
```
POST /api/messaging/messages/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
    "recipient": "+1234567890",
    "message": "Hello, this is a test message!",
    "message_type": "outbound"
}
```

**Response (201):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "recipient": "+1234567890",
    "message": "Hello, this is a test message!",
    "status": "pending",
    "created_at": "2024-04-05T10:30:00Z",
    "characters_count": 32,
    "segments_count": 1
}
```

### 2. List All Messages
```
GET /api/messaging/messages/?page=1&page_size=20
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)
- `status` - Filter by status (pending, sent, failed)
- `message_type` - Filter by type (outbound, inbound)
- `created_after` - Filter by date
- `search` - Search in recipient or message content

**Response (200):**
```json
{
    "count": 150,
    "next": "http://api.example.com/messaging/messages/?page=2",
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "recipient": "+1234567890",
            "message": "Test message",
            "status": "sent",
            "created_at": "2024-04-05T10:30:00Z"
        }
    ]
}
```

### 3. Get Message Details
```
GET /api/messaging/messages/{id}/
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "sender": "+1234567890",
    "recipient": "+0987654321",
    "message": "Hello, this is a test message!",
    "status": "sent",
    "created_at": "2024-04-05T10:30:00Z",
    "sent_at": "2024-04-05T10:30:05Z",
    "characters_count": 32,
    "segments_count": 1,
    "delivery_status": {
        "status": "delivered",
        "delivery_timestamp": "2024-04-05T10:30:10Z",
        "error_code": null,
        "cost": "0.0050"
    }
}
```

### 4. Check Delivery Status
```
GET /api/messaging/messages/{id}/delivery_status/
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
    "id": "ds-uuid",
    "status": "delivered",
    "status_description": "Message delivered successfully",
    "delivery_timestamp": "2024-04-05T10:30:10Z",
    "error_code": null,
    "cost": "0.0050",
    "last_checked": "2024-04-05T10:35:00Z",
    "check_count": 2
}
```

### 5. Delete Message
```
DELETE /api/messaging/messages/{id}/
Authorization: Bearer {access_token}
```

**Response (204):** No content

### 6. Create Message Template
```
POST /api/messaging/templates/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
    "name": "Verification Code",
    "description": "Send verification code to user",
    "content": "Your verification code is: {{code}}",
    "variables": ["code"]
}
```

**Response (201):**
```json
{
    "id": "template-uuid",
    "name": "Verification Code",
    "content": "Your verification code is: {{code}}",
    "variables": ["code"],
    "is_active": true,
    "created_at": "2024-04-05T10:00:00Z"
}
```

### 7. List Templates
```
GET /api/messaging/templates/?is_active=true
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
    "count": 5,
    "results": [
        {
            "id": "template-uuid",
            "name": "Welcome Message",
            "description": "New user welcome",
            "variables": ["name"],
            "is_active": true
        }
    ]
}
```

### 8. Update Template
```
PATCH /api/messaging/templates/{id}/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
    "content": "Updated content: {{code}}"
}
```

**Response (200):** Updated template object

### 9. Delete Template
```
DELETE /api/messaging/templates/{id}/
Authorization: Bearer {access_token}
```

**Response (204):** No content

---

## 📊 Message Lifecycle

```
User sends SMS request
    ↓
Message created (status: draft)
    ↓
Message queued (status: pending)
    ↓
Sent to SMS provider (status: sending)
    ↓
Provider confirms (status: sent)
    ↓
DeliveryStatus created (status: accepted)
    ↓
Provider sends delivery report (status: delivered)
    ↓
Message marked delivered
```

---

## 🔄 SMS Segmentation

Long messages are automatically split:

- **1 segment:** 0-160 characters (ASCII) or 0-70 (Unicode)
- **2 segments:** 161-306 characters (ASCII) or 71-134 (Unicode)
- **3 segments:** 307-459 characters (ASCII) or 135-201 (Unicode)

Concatenation header (UDH): 7 characters per segment

---

## 🧪 Example Usage

### Send Simple SMS
```bash
curl -X POST http://localhost:8000/api/messaging/messages/ \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "recipient": "+1234567890",
    "message": "Hello from Smart SMS!"
}'
```

### Send Using Template
```python
# Get template
template = MessageTemplate.objects.get(name="Verification Code")

# Create message with variables
message = SMSMessage.objects.create(
    sender=user.phone,
    recipient="+1234567890",
    message=template.content.format(code="123456"),
    message_type="outbound"
)

# Create delivery status
DeliveryStatus.objects.create(message=message)
```

### Batch Send Messages
```python
from apps.module_2_messaging.models import SMSMessage

messages = [
    SMSMessage(sender=user.phone, recipient="+123...", message="Hi 1"),
    SMSMessage(sender=user.phone, recipient="+456...", message="Hi 2"),
    SMSMessage(sender=user.phone, recipient="+789...", message="Hi 3"),
]
SMSMessage.objects.bulk_create(messages)
```

---

## 🔧 Configuration

### settings.py
```python
# SMS Provider Configuration
SMS_PROVIDER = 'twilio'  # Options: 'twilio', 'nexmo', 'aws-sns'
SMS_API_KEY = 'your-api-key'
SMS_API_SECRET = 'your-api-secret'
SMS_FROM_NUMBER = '+1234567890'

# SMS Settings
SMS_BATCH_SIZE = 100
SMS_MAX_RETRIES = 3
SMS_RETRY_DELAY = 300  # seconds

# Delivery Tracking
DELIVERY_CHECK_INTERVAL = 3600  # seconds
DELIVERY_TIMEOUT = 86400  # 24 hours
```

---

## 💾 Database Queries

### Get recent messages
```python
from apps.module_2_messaging.models import SMSMessage

# Last 10 sent messages
recent = SMSMessage.objects.filter(
    message_type='outbound',
    status='sent'
).order_by('-created_at')[:10]
```

### Get failed messages
```python
failed = SMSMessage.objects.filter(status='failed')
```

### Get messages by phone
```python
messages = SMSMessage.objects.filter(
    sender='+1234567890'
).order_by('-created_at')
```

---

## 🚀 Best Practices

- **Batch Processing:** Use bulk_create for multiple messages
- **Error Handling:** Implement retry logic for failed messages
- **Rate Limiting:** Respect provider API rate limits
- **Cost Tracking:** Monitor message cost trends
- **Delivery Confirmation:** Always check delivery status
- **Character Encoding:** Validate character count before sending
- **Template Management:** Use templates for recurring messages

---

## ⚠️ Common Issues

**Issue:** Messages stuck in "pending" status
- **Solution:** Check SMS provider credentials
- **Solution:** Check API rate limits
- **Solution:** Verify phone number format

**Issue:** Delivery status not updating
- **Solution:** Implement webhook for delivery callbacks
- **Solution:** Check provider's delivery report format

**Issue:** High message costs
- **Solution:** Optimize message content length
- **Solution:** Review multi-segment messages
- **Solution:** Batch similar messages

---

## 📚 Related Files

- [API Examples](../API_EXAMPLES.md)
- [Models Documentation](../MODELS_DOCUMENTATION.md)
- [Test Cases](../TEST_CASES.md)
