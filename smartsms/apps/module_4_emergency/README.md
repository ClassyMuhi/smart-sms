# Emergency & Safety System Module (Module 4)

## Overview

The Emergency & Safety System module extends your Smart SMS project with SOS emergency triggering, emergency contact management, live location tracking, and automated alert messaging.

**Key Features:**
- 🚨 One-click SOS emergency trigger
- 📍 Real-time location tracking
- 📞 Automatic emergency contact notification
- 💬 Integrated messaging alerts
- 📋 Complete emergency action logging
- 🔐 Per-user isolation (users can only access their own emergencies)

---

## Project Structure

```
smartsms/
├── apps/
│   ├── module_1_auth/          (Auth & Users)
│   ├── module_2_messaging/     (SMS Messages)
│   ├── module_3_contacts/      (Contacts & Emergency Contacts)
│   └── module_4_emergency/     (NEW: Emergency & Safety System)
│       ├── migrations/
│       │   ├── __init__.py
│       │   └── 0001_initial.py
│       ├── __init__.py
│       ├── admin.py            (Django admin interface)
│       ├── apps.py             (App configuration)
│       ├── models.py           (EmergencySOS, EmergencyLog, LocationUpdate)
│       ├── serializers.py      (DRF serializers)
│       ├── urls.py             (API routing)
│       ├── views.py            (EmergencySOSViewSet)
│       └── README.md           (This file)
└── smartsms/
    ├── settings.py            (Updated with new app)
    ├── urls.py                (Updated with new routes)
```

---

## Installation & Setup

### 1. **Models Are Already Created**

The module includes three main models with automatic relationships:

#### **EmergencySOS**
- Tracks emergency triggers
- Stores reason, description, location
- Manages emergency status (active/resolved/cancelled)
- Links to user

#### **EmergencyLog**
- Audits every emergency action
- Types: triggered, contact_notified, message_sent, location_updated, resolved, failed
- Stores action details as JSON

#### **LocationUpdate**
- Stores live GPS coordinates during emergency
- Tracks latitude, longitude, accuracy, address
- Historical location trail

---

### 2. **Run Migrations**

```bash
cd smartsms
python manage.py migrate
```

This creates the following database tables:
- `module_4_emergency_emergencysos`
- `module_4_emergency_emergencylog`
- `module_4_emergency_locationupdate`

---

### 3. **Integration Points**

**The module automatically integrates with:**

✅ **module_1_auth** - Uses CustomUser for authentication  
✅ **module_3_contacts** - Reuses Contact and EmergencyContact models  
✅ **module_2_messaging** - Uses SMSMessage to send alerts  

**No code changes needed** in existing modules!

---

## API Endpoints

### **Base URL**
```
http://127.0.0.1:8000/api/emergency/
```

---

### **1. Trigger Emergency (SOS)**

**Request:**
```
POST /api/emergency/sos/
Authorization: Bearer {token}
Content-Type: application/json

{
    "reason": "medical",              // medical, accident, fire, theft, lost, other
    "description": "Acute chest pain",
    "location_lat": 40.7128,
    "location_lon": -74.0060
}
```

**Response (201 Created):**
```json
{
    "id": "uuid...",
    "reason": "medical",
    "reason_display": "Medical Emergency",
    "description": "Acute chest pain",
    "status": "active",
    "status_display": "Active - Emergency ongoing",
    "location_lat": 40.7128,
    "location_lon": -74.0060,
    "created_at": "2026-04-12T10:30:00Z",
    "resolved_at": null,
    "logs": [
        {
            "id": "uuid...",
            "action_type": "triggered",
            "action_display": "SOS Triggered",
            "details": {
                "reason": "medical",
                "location": "40.7128, -74.0060"
            },
            "created_at": "2026-04-12T10:30:00Z"
        },
        {
            "id": "uuid...",
            "action_type": "contact_notified",
            "action_display": "Emergency Contact Notified",
            "details": {
                "contact_count": 2,
                "contacts": [
                    {
                        "name": "John Doe",
                        "phone": "9876543210",
                        "relationship": "Doctor"
                    }
                ]
            },
            "created_at": "2026-04-12T10:30:00Z"
        },
        {
            "id": "uuid...",
            "action_type": "message_sent",
            "action_display": "Alert Message Sent",
            "details": {
                "recipient": "9876543210",
                "contact_name": "John Doe",
                "message_id": "uuid..."
            },
            "created_at": "2026-04-12T10:30:00Z"
        }
    ],
    "location_updates": []
}
```

**What Happens Automatically:**
1. ✅ EmergencySOS created
2. ✅ "triggered" log created
3. ✅ Emergency contacts fetched
4. ✅ Alert messages created for each emergency contact
5. ✅ Logs created for each notification

---

### **2. List All SOS Events**

**Request:**
```
GET /api/emergency/sos/
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
[
    {
        "id": "uuid1...",
        "reason": "medical",
        "status": "active",
        "created_at": "2026-04-12T10:30:00Z",
        ...
    },
    {
        "id": "uuid2...",
        "reason": "accident",
        "status": "resolved",
        "created_at": "2026-04-11T15:20:00Z",
        ...
    }
]
```

---

### **3. Get SOS Details with Logs & Location**

**Request:**
```
GET /api/emergency/sos/{id}/
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
    "id": "uuid...",
    "reason": "medical",
    "description": "Chest pain",
    "status": "active",
    "location_lat": 40.7128,
    "location_lon": -74.0060,
    "created_at": "2026-04-12T10:30:00Z",
    "resolved_at": null,
    "logs": [...],           // Full action history
    "location_updates": []   // Location trail
}
```

---

### **4. Update SOS Status (Resolve/Cancel)**

**Request:**
```
PATCH /api/emergency/sos/{id}/
Authorization: Bearer {token}
Content-Type: application/json

{
    "status": "resolved"  // or "cancelled"
}
```

**Response (200 OK):**
```json
{
    "id": "uuid...",
    "status": "resolved",
    "resolved_at": "2026-04-12T10:45:00Z",
    "logs": [
        ...previous logs...,
        {
            "id": "uuid...",
            "action_type": "resolved",
            "details": {
                "previous_status": "active",
                "new_status": "resolved",
                "updated_at": "2026-04-12T10:45:00Z"
            },
            "created_at": "2026-04-12T10:45:00Z"
        }
    ]
}
```

---

### **5. Add Location Update (Real-time Tracking)**

**Request:**
```
POST /api/emergency/sos/{id}/add_location/
Authorization: Bearer {token}
Content-Type: application/json

{
    "latitude": 40.7150,
    "longitude": -74.0080,
    "accuracy": 15,
    "address": "Near Empire State Building, NYC"
}
```

**Response (201 Created):**
```json
{
    "id": "uuid...",
    "latitude": 40.7150,
    "longitude": -74.0080,
    "accuracy": 15,
    "address": "Near Empire State Building, NYC",
    "created_at": "2026-04-12T10:35:00Z"
}
```

A log entry is automatically created for this location update.

---

### **6. Get Emergency Contacts**

**Request:**
```
GET /api/emergency/sos/{id}/emergency_contacts/
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
    "count": 2,
    "emergency_contacts": [
        {
            "id": "uuid...",
            "name": "John Doe",
            "phone": "9876543210",
            "email": "john@example.com",
            "relationship": "Doctor"
        },
        {
            "id": "uuid...",
            "name": "Jane Smith",
            "phone": "9123456789",
            "email": "jane@example.com",
            "relationship": "Sister"
        }
    ]
}
```

---

### **7. Get Active Emergencies**

**Request:**
```
GET /api/emergency/sos/active/
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
    "count": 1,
    "active_emergencies": [
        {
            "id": "uuid...",
            "reason": "medical",
            "status": "active",
            "created_at": "2026-04-12T10:30:00Z",
            ...
        }
    ]
}
```

---

## database Relationships

```
CustomUser
├── emergency_sos (ForeignKey)
│   └── EmergencySOS
│       ├── logs (ForeignKey to EmergencyLog)
│       ├── location_updates (ForeignKey to LocationUpdate)
│       └── Uses emergency_contacts from module_3_contacts
│           └── EmergencyContact
│               └── Contact
```

---

## Example Usage Flow

### **Scenario: User triggers SOS during medical emergency**

```python
# 1. User calls POST /api/emergency/sos/ with GPS location
{
    "reason": "medical",
    "description": "Missing for 2 hours",
    "location_lat": 40.7128,
    "location_lon": -74.0060
}

# 2. Backend automatically:
#    - Creates EmergencySOS
#    - Logs "triggered" action
#    - Fetches emergency_contacts (Doctor, Sister, Spouse)
#    - Creates SMSMessages for each contact
#      "🚨 EMERGENCY ALERT: [Name] triggered SOS!"
#    - Logs "contact_notified" action
#    - Logs "message_sent" action x3

# 3. User sends live location updates
PATCH /api/emergency/sos/{id}/add_location/
{
    "latitude": 40.7150,  # Updated position
    "longitude": -74.0080
}
# Backend logs this location

# 4. Emergency resolved
PATCH /api/emergency/sos/{id}/
{
    "status": "resolved"
}
# Backend logs "resolved" action with timestamp
```

---

## Admin Interface

Access Django admin:
```
http://127.0.0.1:8000/admin/
```

You can:
- View all emergencies
- View logs & location trail
- Filter by status, reason, date
- Search by user email/phone

---

## Testing

### **Test with curl:**

```bash
# 1. Login and get token
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"phone_or_email": "user@example.com", "password": "pass"}'

# 2. Trigger SOS (using token from above)
curl -X POST http://127.0.0.1:8000/api/emergency/sos/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "medical",
    "description": "Test",
    "location_lat": 40.7128,
    "location_lon": -74.0060
  }'

# 3. List SOS events
curl -X GET http://127.0.0.1:8000/api/emergency/sos/ \
  -H "Authorization: Bearer {token}"
```

---

## Code Examples

### **Python (requests)**

```python
import requests

BASE_URL = "http://127.0.0.1:8000/api"
TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Trigger SOS
response = requests.post(
    f"{BASE_URL}/emergency/sos/",
    json={
        "reason": "medical",
        "description": "Lost consciousness",
        "location_lat": 40.7128,
        "location_lon": -74.0060
    },
    headers=headers
)
sos = response.json()
sos_id = sos['id']

# Add location update
requests.post(
    f"{BASE_URL}/emergency/sos/{sos_id}/add_location/",
    json={
        "latitude": 40.7150,
        "longitude": -74.0080
    },
    headers=headers
)

# Resolve emergency
requests.patch(
    f"{BASE_URL}/emergency/sos/{sos_id}/",
    json={"status": "resolved"},
    headers=headers
)
```

---

## Important Notes

**✅ What's reused from existing modules:**
- Authentication (module_1_auth)
- Contacts system (module_3_contacts)
- Messaging system (module_2_messaging)
- User model (CustomUser)

**🔐 Security:**
- Users can only access their own emergencies
- Authentication required on all endpoints
- Per-user filtering at queryyset level

**📊 Database:**
- No changes to existing tables
- Three new tables created
- Foreign key relationships to existing models
- Indexed for performance

**🔄 Workflow:**
```
SOS Trigger → Create Log → Fetch Contacts → Send Messages → Create Logs → Location Tracking
```

---

## What's NOT Included (For Future)

- Actual SMS sending (use Twilio/AWS SNS)
- Real location geofencing
- Push notifications
- Reverse geocoding (coords → address)
- 911/Emergency service API integration
- Voice call dispatch

---

## Summary

The Emergency & Safety System module:
1. ✅ Integrates cleanly without breaking existing code
2. ✅ Reuses existing models (User, Contact, Message)
3. ✅ Adds 3 new models (SOS, Log, Location)
4. ✅ Provides complete API for SOS workflow
5. ✅ Automatically notifies emergency contacts
6. ✅ Tracks all actions in audit logs
7. ✅ Supports real-time location updates
8. ✅ Per-user data isolation

Ready to use! 🚀
