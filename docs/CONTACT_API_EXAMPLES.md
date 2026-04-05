# Contact Management Module - API Testing & Examples

## Quick Start Testing

### 1. Get Authentication Token

First, you need a JWT token. Use your existing auth module endpoints:

```bash
# Register user (if not already done)
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+91 9876543210",
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "full_name": "Test User"
  }'

# Response: { "user_id": "..." }

# Verify OTP (check console for OTP)
curl -X POST http://localhost:8000/api/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "...",
    "otp_code": "123456"  # from console
  }'

# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_or_email": "+91 9876543210",
    "password": "SecurePass123!"
  }'

# Response: { "access": "YOUR_TOKEN", "refresh": "..." }
```

Save the `access` token for all Contact API calls.

---

## Contact Management API - Complete Examples

### Headers for All Requests
```bash
-H "Authorization: Bearer YOUR_TOKEN"
-H "Content-Type: application/json"
```

---

## 1. CREATE CONTACTS

### Basic Create
```bash
curl -X POST http://localhost:8000/api/contacts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone": "+91 98765 43210",
    "email": "john@example.com"
  }'
```

**Response (201 Created):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "phone_display": "98765 43210",
    "email": "john@example.com",
    "created_at": "2026-04-05T10:30:00Z",
    "updated_at": "2026-04-05T10:30:00Z"
}
```

### Minimal Create (No Email)
```bash
curl -X POST http://localhost:8000/api/contacts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "phone": "9987654321"
  }'
```

### Error: Duplicate Phone
```bash
curl -X POST http://localhost:8000/api/contacts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Another John",
    "phone": "+91 98765 43210"
  }'
```

**Response (400 Bad Request):**
```json
{
    "phone": [
        "You already have a contact with phone 98765 43210."
    ]
}
```

### Error: Invalid Phone
```bash
curl -X POST http://localhost:8000/api/contacts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Invalid Contact",
    "phone": "abc"
  }'
```

**Response (400 Bad Request):**
```json
{
    "phone": [
        "Phone number must be 9-15 digits. Format: +91 98765 43210 or 9876543210"
    ]
}
```

---

## 2. LIST CONTACTS

### Simple List
```bash
curl -X GET http://localhost:8000/api/contacts/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK):**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "John Doe",
            "phone_display": "98765 43210",
            "email": "john@example.com",
            "created_at": "2026-04-05T10:30:00Z",
            "updated_at": "2026-04-05T10:30:00Z"
        }
    ]
}
```

### With Pagination (Page 1, 10 per page)
```bash
curl -X GET "http://localhost:8000/api/contacts/?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### With Pagination (Page 2, 20 per page)
```bash
curl -X GET "http://localhost:8000/api/contacts/?page=2&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### With Sorting (Most Recent First)
```bash
curl -X GET "http://localhost:8000/api/contacts/?ordering=-created_at" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### With Sorting (By Name A-Z)
```bash
curl -X GET "http://localhost:8000/api/contacts/?ordering=name" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Global Search
```bash
curl -X GET "http://localhost:8000/api/contacts/?search=john" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 3. GET SPECIFIC CONTACT

### Get by ID
```bash
curl -X GET http://localhost:8000/api/contacts/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (200 OK):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "phone_display": "98765 43210",
    "email": "john@example.com",
    "created_at": "2026-04-05T10:30:00Z",
    "updated_at": "2026-04-05T10:30:00Z"
}
```

### Not Found
```bash
curl -X GET http://localhost:8000/api/contacts/00000000-0000-0000-0000-000000000000/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (404 Not Found):**
```json
{
    "detail": "Not found."
}
```

---

## 4. UPDATE CONTACTS

### Full Update (PUT - all fields required)
```bash
curl -X PUT http://localhost:8000/api/contacts/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "phone": "+91 99876 54321",
    "email": "john.smith@example.com"
  }'
```

### Partial Update (PATCH - only required fields)
```bash
curl -X PATCH http://localhost:8000/api/contacts/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Johnny Doe"
  }'
```

### Update Only Email
```bash
curl -X PATCH http://localhost:8000/api/contacts/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com"
  }'
```

**Response (200 OK):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Johnny Doe",
    "phone_display": "98765 43210",
    "email": "newemail@example.com",
    "created_at": "2026-04-05T10:30:00Z",
    "updated_at": "2026-04-05T10:30:00Z"
}
```

---

## 5. DELETE CONTACTS

### Delete Contact (No Emergency Association)
```bash
curl -X DELETE http://localhost:8000/api/contacts/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (204 No Content):**
- Empty response body, status 204

### Delete Contact (With Emergency Association)
```bash
curl -X DELETE http://localhost:8000/api/contacts/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (400 Bad Request):**
```json
{
    "detail": "This contact is marked as emergency contact. Remove from emergency contacts first.",
    "emergency_contact_count": 1
}
```

**Solution: First remove from emergency contacts**
```bash
# Get emergency contacts
curl -X GET http://localhost:8000/api/emergency-contacts/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Delete the emergency association
curl -X DELETE http://localhost:8000/api/emergency-contacts/{emergency_id}/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Now you can delete the contact
curl -X DELETE http://localhost:8000/api/contacts/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 6. SEARCH CONTACTS

### Search by Name (Partial Match)
```bash
curl -X GET "http://localhost:8000/api/contacts/search/?name=john" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "John Doe",
            "phone_display": "98765 43210",
            "email": "john@example.com",
            "created_at": "2026-04-05T10:30:00Z",
            "updated_at": "2026-04-05T10:30:00Z"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "Johnny Smith",
            "phone_display": "99876 54321",
            "email": "johnny@example.com",
            "created_at": "2026-04-05T10:35:00Z",
            "updated_at": "2026-04-05T10:35:00Z"
        }
    ]
}
```

### Search by Phone (Partial Match)
```bash
curl -X GET "http://localhost:8000/api/contacts/search/?phone=9876" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Combined Search
```bash
curl -X GET "http://localhost:8000/api/contacts/search/?name=john&phone=9876" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search Without Parameters (Error)
```bash
curl -X GET "http://localhost:8000/api/contacts/search/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (400 Bad Request):**
```json
{
    "detail": "Provide either name or phone parameter."
}
```

---

## 7. RECENT CONTACTS

### Get Last 5 Recent Contacts
```bash
curl -X GET "http://localhost:8000/api/contacts/recent/?limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
    "count": 5,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Recent Contact 1",
            "phone_display": "9876543210",
            "email": null,
            "created_at": "2026-04-05T10:30:00Z",
            "updated_at": "2026-04-05T10:30:00Z"
        }
    ]
}
```

### Get Last 10 Recent Contacts
```bash
curl -X GET "http://localhost:8000/api/contacts/recent/?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 8. EMERGENCY CONTACTS

### List All Emergency Contacts
```bash
curl -X GET http://localhost:8000/api/emergency-contacts/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "550e8401-e29b-41d4-a716-446655440001",
            "contact": "550e8400-e29b-41d4-a716-446655440000",
            "contact_detail": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "John Doe",
                "phone_display": "98765 43210",
                "email": "john@example.com",
                "created_at": "2026-04-05T10:30:00Z",
                "updated_at": "2026-04-05T10:30:00Z"
            },
            "relationship": "Mother",
            "created_at": "2026-04-05T10:35:00Z"
        }
    ]
}
```

### Add Emergency Contact (By Contact ID)
```bash
curl -X POST http://localhost:8000/api/emergency-contacts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contact": "550e8400-e29b-41d4-a716-446655440000",
    "relationship": "Mother"
  }'
```

**Response (201 Created):**
```json
{
    "id": "550e8401-e29b-41d4-a716-446655440001",
    "contact": "550e8400-e29b-41d4-a716-446655440000",
    "contact_detail": { ... },
    "relationship": "Mother",
    "created_at": "2026-04-05T10:35:00Z"
}
```

### Remove From Emergency Contacts
```bash
curl -X DELETE http://localhost:8000/api/emergency-contacts/550e8401-e29b-41d4-a716-446655440001/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response (204 No Content)**

### Quick Access Emergency Contacts (For Quick Dialing)
```bash
curl -X GET http://localhost:8000/api/emergency-contacts/quick_access/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
    "count": 3,
    "emergency_contacts": [
        {
            "id": "550e8401-e29b-41d4-a716-446655440001",
            "name": "John Doe",
            "phone": "98765 43210",
            "relationship": "Mother"
        },
        {
            "id": "550e8401-e29b-41d4-a716-446655440002",
            "name": "Dr. Smith",
            "phone": "99876 54321",
            "relationship": "Doctor"
        }
    ],
    "message": "Quick access list for emergency calls"
}
```

### Add Emergency Contact by Phone Number
```bash
curl -X POST http://localhost:8000/api/emergency-contacts/add_by_phone/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "9876543210",
    "relationship": "Doctor"
  }'
```

**Response (201 Created):**
```json
{
    "id": "550e8401-e29b-41d4-a716-446655440003",
    "contact": "550e8400-e29b-41d4-a716-446655440000",
    "contact_detail": { ... },
    "relationship": "Doctor",
    "created_at": "2026-04-05T10:40:00Z"
}
```

### Error: Phone Not Found
```bash
curl -X POST http://localhost:8000/api/emergency-contacts/add_by_phone/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "0000000000"
  }'
```

**Response (404 Not Found):**
```json
{
    "detail": "Contact with phone 0000000000 not found."
}
```

---

## Complete Test Workflow

### Step 1: Create Multiple Contacts
```bash
# Contact 1: Mother
curl -X POST http://localhost:8000/api/contacts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mother",
    "phone": "9876543210",
    "email": "mother@example.com"
  }'
# Save the ID as CONTACT_1_ID

# Contact 2: Doctor
curl -X POST http://localhost:8000/api/contacts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. John Smith",
    "phone": "9876543211",
    "email": "doctor@hospital.com"
  }'
# Save the ID as CONTACT_2_ID
```

### Step 2: Mark as Emergency
```bash
curl -X POST http://localhost:8000/api/emergency-contacts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contact": "CONTACT_1_ID",
    "relationship": "Mother"
  }'

curl -X POST http://localhost:8000/api/emergency-contacts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contact": "CONTACT_2_ID",
    "relationship": "Doctor"
  }'
```

### Step 3: Get Quick Access
```bash
curl -X GET http://localhost:8000/api/emergency-contacts/quick_access/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 4: Search Contacts
```bash
curl -X GET "http://localhost:8000/api/contacts/search/?name=doctor" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 5: Update Contact
```bash
curl -X PATCH http://localhost:8000/api/contacts/CONTACT_2_ID/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "9999999999"
  }'
```

---

## Running Tests

```bash
# Run all tests
python manage.py test contact_management

# Run specific test class
python manage.py test contact_management.tests.ContactAPITests

# Run with verbose output
python manage.py test contact_management -v 2

# Run specific test method
python manage.py test contact_management.tests.ContactAPITests.test_create_contact_api
```

---

## Common Response Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | GET successful, PATCH successful |
| 201 | Created | POST contact created successfully |
| 204 | No Content | DELETE successful |
| 400 | Bad Request | Invalid data, duplicate phone |
| 401 | Unauthorized | Missing/invalid token |
| 404 | Not Found | Contact doesn't exist |

---

**That's it!** You now have a complete Contact Management API with full testing capabilities.
