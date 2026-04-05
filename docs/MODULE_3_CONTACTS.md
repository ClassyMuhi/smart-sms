# Module 3: Contact Management

**Location:** `smartsms/apps/module_3_contacts/`

---

## 📌 Overview

Module 3 handles contact creation, storage, searching, and management. It allows users to organize contacts into groups, search contacts, and track interactions.

## 🗂️ Folder Structure

```
module_3_contacts/
├── __init__.py
├── admin.py                    # Django admin configurations
├── apps.py                     # App configuration
├── models.py                   # Database models (Contact, Group, etc.)
├── serializers.py              # DRF serializers for contacts
├── views.py                    # API endpoints and viewsets
├── urls.py                     # URL routing
└── migrations/                 # Database migrations
```

## 📊 Database Models

### Contact Model
```python
{
    "id": "uuid",
    "owner_id": "user-uuid",
    "name": "John Doe",
    "phone": "+1234567890",
    "email": "john@example.com",
    "group_id": "group-uuid",
    "is_favorite": false,
    "is_blocked": false,
    "notes": "Office contact",
    "created_at": "2024-04-05T10:00:00Z",
    "updated_at": "2024-04-05T10:00:00Z",
    "last_contacted": "2024-04-04T15:30:00Z"
}
```

**Fields:**
- `id` - UUID primary key
- `owner_id` - User who created the contact
- `name` - Contact's full name
- `phone` - Phone number (unique per user)
- `email` - Email address
- `group_id` - Group this contact belongs to
- `is_favorite` - Mark as favorite contact
- `is_blocked` - Block contact from communication
- `notes` - Additional notes about contact
- `created_at` - Creation timestamp
- `last_contacted` - Last interaction timestamp

### ContactGroup Model
```python
{
    "id": "uuid",
    "owner_id": "user-uuid",
    "name": "Team Members",
    "description": "Office team members",
    "color": "#FF5733",
    "created_at": "2024-04-05T10:00:00Z"
}
```

**Fields:**
- `id` - UUID primary key
- `owner_id` - User who created the group
- `name` - Group name
- `description` - Group description
- `color` - Color code for UI display
- `created_at` - Creation timestamp

### ContactInteraction Model
```python
{
    "id": "uuid",
    "contact_id": "contact-uuid",
    "interaction_type": "sms_sent",  # sms_sent, sms_received, call
    "description": "Sent SMS",
    "timestamp": "2024-04-05T10:00:00Z"
}
```

---

## 🔌 API Endpoints

### 1. Create Contact
```
POST /api/contacts/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
    "name": "John Doe",
    "phone": "+1234567890",
    "email": "john@example.com",
    "group_id": "group-uuid",
    "notes": "Office contact"
}
```

**Response (201):**
```json
{
    "id": "contact-uuid",
    "name": "John Doe",
    "phone": "+1234567890",
    "email": "john@example.com",
    "is_favorite": false,
    "is_blocked": false,
    "created_at": "2024-04-05T10:00:00Z"
}
```

### 2. List Contacts
```
GET /api/contacts/?page=1&page_size=20
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `page` - Page number
- `page_size` - Items per page
- `search` - Search by name or phone
- `group_id` - Filter by group
- `is_favorite` - Filter favorites (true/false)
- `is_blocked` - Filter blocked contacts
- `ordering` - Order by field (name, created_at)

**Response (200):**
```json
{
    "count": 50,
    "next": "http://api.example.com/contacts/?page=2",
    "results": [
        {
            "id": "contact-uuid",
            "name": "John Doe",
            "phone": "+1234567890",
            "is_favorite": true,
            "last_contacted": "2024-04-04T15:30:00Z"
        }
    ]
}
```

### 3. Get Contact Details
```
GET /api/contacts/{id}/
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
    "id": "contact-uuid",
    "name": "John Doe",
    "phone": "+1234567890",
    "email": "john@example.com",
    "group": {
        "id": "group-uuid",
        "name": "Team Members"
    },
    "is_favorite": true,
    "is_blocked": false,
    "notes": "Office contact",
    "created_at": "2024-04-05T10:00:00Z",
    "last_contacted": "2024-04-04T15:30:00Z"
}
```

### 4. Update Contact
```
PATCH /api/contacts/{id}/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "is_favorite": true
}
```

**Response (200):** Updated contact object

### 5. Delete Contact
```
DELETE /api/contacts/{id}/
Authorization: Bearer {access_token}
```

**Response (204):** No content

### 6. Search Contacts
```
POST /api/contacts/search/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
    "query": "john",
    "search_fields": ["name", "phone", "email"],
    "limit": 10
}
```

**Response (200):**
```json
[
    {
        "id": "contact-uuid",
        "name": "John Doe",
        "phone": "+1234567890",
        "score": 0.95
    }
]
```

### 7. Create Contact Group
```
POST /api/contacts/groups/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
    "name": "Team Members",
    "description": "Office team members",
    "color": "#FF5733"
}
```

**Response (201):**
```json
{
    "id": "group-uuid",
    "name": "Team Members",
    "description": "Office team members",
    "color": "#FF5733",
    "contact_count": 0,
    "created_at": "2024-04-05T10:00:00Z"
}
```

### 8. List Groups
```
GET /api/contacts/groups/?page=1
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
    "count": 5,
    "results": [
        {
            "id": "group-uuid",
            "name": "Team Members",
            "contact_count": 12
        }
    ]
}
```

### 9. Update Group
```
PATCH /api/contacts/groups/{id}/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
    "name": "New Team Name",
    "color": "#00FF00"
}
```

**Response (200):** Updated group object

### 10. Delete Group
```
DELETE /api/contacts/groups/{id}/
Authorization: Bearer {access_token}
```

**Response (204):** No content

### 11. Import Contacts (CSV)
```
POST /api/contacts/import/
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Form Data:**
- `file` - CSV file (name, phone, email, group)

**CSV Format:**
```csv
Name,Phone,Email,Group
John Doe,+1234567890,john@example.com,Team
Jane Smith,+0987654321,jane@example.com,Team
```

**Response (200):**
```json
{
    "imported": 2,
    "failed": 0,
    "errors": []
}
```

### 12. Export Contacts
```
GET /api/contacts/export/?format=csv
Authorization: Bearer {access_token}
```

**Response:** CSV file download

---

## 🔍 Advanced Searching

### Full-Text Search
```python
from django.db.models import Q

contacts = Contact.objects.filter(
    Q(name__icontains='john') |
    Q(phone__icontains='1234') |
    Q(email__icontains='john')
)
```

### Filter Combinations
```python
# Favorite contacts in specific group
contacts = Contact.objects.filter(
    is_favorite=True,
    group__name='Team Members'
)

# Contacts not contacted in 30 days
from datetime import timedelta
from django.utils import timezone

thirty_days_ago = timezone.now() - timedelta(days=30)
inactive = Contact.objects.filter(
    last_contacted__lt=thirty_days_ago
)
```

---

## 📊 Contact Statistics

### Get contact count by group
```python
from django.db.models import Count

stats = (
    ContactGroup.objects
    .annotate(contact_count=Count('contact'))
    .values('name', 'contact_count')
)
```

### Get most recently contacted
```python
recent = Contact.objects.order_by('-last_contacted')[:10]
```

### Get favorite contacts
```python
favorites = Contact.objects.filter(is_favorite=True)
```

---

## 🧪 Example Usage

### Create Contact Group
```bash
curl -X POST http://localhost:8000/api/contacts/groups/ \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "name": "Work",
    "description": "Work contacts",
    "color": "#FF5733"
}'
```

### Create Contact
```bash
curl -X POST http://localhost:8000/api/contacts/ \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "name": "John Doe",
    "phone": "+1234567890",
    "email": "john@example.com",
    "group_id": "group-uuid",
    "notes": "Office manager"
}'
```

### Search Contacts
```bash
curl "http://localhost:8000/api/contacts/?search=john&is_favorite=true" \
-H "Authorization: Bearer YOUR_TOKEN"
```

### Import Contacts
```bash
curl -X POST http://localhost:8000/api/contacts/import/ \
-H "Authorization: Bearer YOUR_TOKEN" \
-F "file=@contacts.csv"
```

---

## 🔧 Configuration

### settings.py
```python
# Contact Management Settings
CONTACTS_ALLOW_DUPLICATE_PHONES = False
CONTACTS_ALLOW_DUPLICATE_EMAILS = False
CONTACTS_MAX_IMPORT_SIZE = 5000  # rows
CONTACTS_SEARCH_FIELDS = ['name', 'phone', 'email', 'notes']

# Group Settings
CONTACTS_ALLOW_DEFAULT_GROUP = True
CONTACTS_DEFAULT_GROUP_NAME = "All Contacts"

# UI Settings
CONTACTS_COLORS = [
    '#FF5733', '#33FF57', '#3357FF',
    '#FF33F1', '#F1FF33', '#33FFF1'
]
```

---

## 📝 Bulk Operations

### Bulk Add Contacts to Group
```python
from apps.module_3_contacts.models import Contact

contact_ids = ['uuid1', 'uuid2', 'uuid3']
Contact.objects.filter(id__in=contact_ids).update(group_id='group-uuid')
```

### Bulk Delete Old Contacts
```python
from datetime import timedelta
from django.utils import timezone

thirty_days_ago = timezone.now() - timedelta(days=30)
Contact.objects.filter(
    last_contacted__lt=thirty_days_ago
).delete()
```

### Bulk Mark as Favorite
```python
Contact.objects.filter(
    phone__in=['+1234567890', '+0987654321']
).update(is_favorite=True)
```

---

## 🚀 Best Practices

- **Validation:** Validate phone numbers before storing
- **Deduplication:** Check for duplicate contacts before importing
- **Grouping:** Organize contacts logically
- **Favorites:** Use favorites for frequently contacted numbers
- **Interactions:** Track contact interactions for analytics
- **Backup:** Export contacts regularly
- **Privacy:** Handle contact data securely

---

## ⚠️ Common Issues

**Issue:** Import fails with "duplicate phone"
- **Solution:** Check for existing contacts with same phone
- **Solution:** Enable CONTACTS_ALLOW_DUPLICATE_PHONES if needed

**Issue:** Search not finding contacts
- **Solution:** Check search_fields configuration
- **Solution:** Verify contact names/phones are correct

**Issue:** Group deletion fails
- **Solution:** Consider moving contacts to another group first
- **Solution:** Allow cascade deletion in settings

---

## 📚 Related Files

- [API Examples](../API_EXAMPLES.md)
- [Models Documentation](../MODELS_DOCUMENTATION.md)
- [Contact Management Guide](../CONTACT_MANAGEMENT_GUIDE.md)
- [Test Cases](../TEST_CASES.md)
