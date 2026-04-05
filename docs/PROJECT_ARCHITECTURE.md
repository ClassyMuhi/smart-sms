# Smart SMS - Project Architecture & Structure Guide

A professional guide to understanding and navigating the Smart SMS modular Django project.

---

## 📚 Table of Contents

1. [Project Overview](#project-overview)
2. [Folder Structure](#folder-structure)
3. [Module Breakdown](#module-breakdown)
4. [File Organization](#file-organization)
5. [Data Models & Relationships](#data-models--relationships)
6. [API Routing](#api-routing)
7. [Development Workflow](#development-workflow)
8. [Deployment](#deployment)

---

## 🎯 Project Overview

**Smart SMS** is a professional-grade Django REST Framework backend for managing SMS communications. It's organized into **3 independent modules** that work together seamlessly.

### Architecture Principles

✅ **Modularity** - Each module is independent and self-contained
✅ **Scalability** - Easy to add new modules or features
✅ **Maintainability** - Clear separation of concerns
✅ **Reusability** - SharedUtilities and base models
✅ **Testability** - Each module has its own test suite

---

## 📁 Folder Structure

```
smart-sms/                                 # Project root
│
├── smartsms/                              # Django project container
│   ├── smartsms/                          # Project configuration
│   │   ├── settings.py                   # Django settings
│   │   ├── urls.py                       # Main URL router
│   │   ├── asgi.py                       # ASGI config (Async)
│   │   ├── wsgi.py                       # WSGI config (Sync)
│   │   └── __init__.py
│   │
│   ├── apps/                              # All application modules
│   │   ├── module_1_auth/                # ✅ Module 1: Authentication
│   │   │   ├── models.py                # CustomUser, OTPLog models
│   │   │   ├── views.py                 # Authentication endpoints
│   │   │   ├── serializers.py           # Request/Response validation
│   │   │   ├── urls.py                  # Module-specific routes
│   │   │   ├── admin.py                 # Django admin config
│   │   │   ├── utils.py                 # OTP, JWT utilities
│   │   │   ├── signals.py               # Django signals
│   │   │   ├── apps.py                  # Module config
│   │   │   ├── migrations/              # Database migrations
│   │   │   └── __init__.py
│   │   │
│   │   ├── module_2_messaging/          # ✅ Module 2: Messaging
│   │   │   ├── models.py                # SMSMessage, DeliveryStatus
│   │   │   ├── views.py                 # Message endpoints
│   │   │   ├── serializers.py           # Message validation
│   │   │   ├── urls.py                  # Module routes
│   │   │   ├── admin.py                 # Admin config
│   │   │   ├── apps.py                  # Module config
│   │   │   ├── migrations/              # Database migrations
│   │   │   └── __init__.py
│   │   │
│   │   └── module_3_contacts/           # ✅ Module 3: Contacts
│   │       ├── models.py                # Contact, ContactGroup models
│   │       ├── views.py                 # Contact endpoints
│   │       ├── serializers.py           # Contact validation
│   │       ├── urls.py                  # Module routes
│   │       ├── admin.py                 # Admin config
│   │       ├── apps.py                  # Module config
│   │       ├── migrations/              # Database migrations
│   │       ├── tests.py                 # Unit tests
│   │       └── __init__.py
│   │
│   ├── manage.py                        # Django CLI tool
│   ├── requirements.txt                 # Python dependencies
│   └── db.sqlite3                       # Development database
│
├── docs/                                  # Project documentation
│   ├── README.md                         # Project overview
│   ├── MODULE_1_AUTH.md                 # Auth module guide
│   ├── MODULE_2_MESSAGING.md            # Messaging module guide
│   ├── MODULE_3_CONTACTS.md             # Contacts module guide
│   ├── API_EXAMPLES.md                  # Practical API examples
│   ├── MODELS_DOCUMENTATION.md          # Database models detail
│   ├── ARCHITECTURE_DEPLOYMENT.md       # This file
│   └── [other docs]
│
├── scripts/                               # Utility scripts
│   ├── startup.sh                        # Linux/Mac startup
│   ├── startup.bat                       # Windows startup
│   ├── create_admin.py                  # Create superuser
│   └── summa.py                         # Project summary
│
├── tests/                                 # Test suite
│   ├── test_register.py                 # Auth tests
│   └── [other tests]
│
├── .env.example                          # Environment template
├── .gitignore                            # Git ignore rules
├── README.md                             # Root README
└── venv/                                 # Virtual environment (ignored)
```

---

## 🏗️ Module Breakdown

### **Module 1: Authentication & User Management**

**Path:** `smartsms/apps/module_1_auth/`

**Purpose:** Handle user accounts, authentication, and authorization.

**Key Components:**
```python
# Models
- CustomUser(AbstractUser)
  * UUID primary key
  * Phone-based identification
  * Email verification
  * Personal PIN

- OTPLog
  * Track OTP requests
  * Validation records

- LoginHistory
  * User login tracking
  * IP address logging
```

**API Endpoints:**
```
POST   /api/auth/register/          # Register new user
POST   /api/auth/login/             # Login with phone/password
POST   /api/auth/request-otp/       # Request OTP
POST   /api/auth/verify-otp/        # Verify OTP code
GET    /api/auth/profile/           # Get current user
PATCH  /api/auth/profile/           # Update profile
POST   /api/auth/change-password/   # Change password
POST   /api/auth/token/refresh/     # Refresh JWT token
```

**Responsibilities:**
- User registration & validation
- OTP generation & verification
- JWT token creation & refresh
- Password & PIN management
- User profile management
- Account activation/deactivation

---

### **Module 2: Messaging (SMS Core)**

**Path:** `smartsms/apps/module_2_messaging/`

**Purpose:** Core SMS sending, receiving, and tracking system.

**Key Components:**
```python
# Models
- SMSMessage
  * UUID primary key
  * Sender/recipient phone
  * Message content
  * Status tracking
  * Timestamp info
  * Character/segment count

- DeliveryStatus
  * OneToOne with SMSMessage
  * Delivery status updates
  * Error codes
  * Cost tracking

- MessageTemplate
  * Pre-defined messages
  * Variable support
  * Active/inactive status
```

**API Endpoints:**
```
GET    /api/messaging/messages/           # List messages
POST   /api/messaging/messages/           # Send SMS
GET    /api/messaging/messages/{id}/      # Get message
GET    /api/messaging/messages/{id}/delivery_status/  # Delivery info
DELETE /api/messaging/messages/{id}/      # Delete message

GET    /api/messaging/templates/          # List templates
POST   /api/messaging/templates/          # Create template
PATCH  /api/messaging/templates/{id}/     # Update template
DELETE /api/messaging/templates/{id}/     # Delete template
```

**Responsibilities:**
- SMS message sending
- Message storage & retrieval
- Delivery status tracking
- Message template management
- Character counting & segmentation
- Cost calculation
- Failure handling & retries

---

### **Module 3: Contact Management**

**Path:** `smartsms/apps/module_3_contacts/`

**Purpose:** User contact organization and management.

**Key Components:**
```python
# Models
- Contact
  * UUID primary key
  * Foreign key to user
  * Name, phone, email
  * Group assignment
  * Favorite flag
  * Block flag
  * Notes
  * Last contacted timestamp

- ContactGroup
  * Group organization
  * Custom colors
  * Descriptions
  * Contact count

- ContactInteraction
  * Track interactions
  * Type (sms_sent, sms_received, call)
  * Timestamp
```

**API Endpoints:**
```
GET    /api/contacts/                     # List contacts
POST   /api/contacts/                     # Create contact
GET    /api/contacts/{id}/                # Get contact
PATCH  /api/contacts/{id}/                # Update contact
DELETE /api/contacts/{id}/                # Delete contact

GET    /api/contacts/groups/              # List groups
POST   /api/contacts/groups/              # Create group
PATCH  /api/contacts/groups/{id}/         # Update group
DELETE /api/contacts/groups/{id}/         # Delete group

POST   /api/contacts/search/              # Advanced search
POST   /api/contacts/import/              # CSV import
GET    /api/contacts/export/              # CSV export
```

**Responsibilities:**
- Contact creation & management
- Contact grouping
- Search & filtering
- Import/export functionality
- Interaction tracking
- Duplicate detection
- Bulk operations

---

## 📊 File Organization

Each module follows this structure:

```
module_name/
├── __init__.py              # Package marker
├── apps.py                  # Django app config
├── models.py                # Database models
├── serializers.py           # DRF serializers (validation, representation)
├── views.py                 # API endpoints (ViewSets, Views)
├── urls.py                  # URL routing
├── admin.py                 # Django admin interface
├── signals.py               # Django signals (post_save, pre_delete, etc.)
├── utils.py                 # Utility functions
├── tests.py                 # Unit tests
├── apps.py                  # Module metadata
└── migrations/              # Database migrations
    ├── __init__.py
    ├── 0001_initial.py
    └── XXXX_description.py
```

### File Purposes

**models.py** - Database schema
- Table definitions
- Fields & relationships
- Validators
- Methods & properties
- Meta options

**serializers.py** - Data validation & transformation
- Request validation
- Response formatting
- Nested relationships
- Custom fields
- Validators

**views.py** - Business logic & API endpoints
- ViewSets (CRUD operations)
- Custom endpoints
- Permissions & authentication
- Filtering & searching
- Pagination

**urls.py** - URL routing
- Router registration
- Custom routes
- Path parameters
- Query parameters

**admin.py** - Django admin customization
- Model registration
- List displays
- Search fields
- Filters
- Custom actions

**signals.py** - Event handlers
- Post-save operations
- Pre-delete cleanup
- User creation workflow
- Notification triggers

---

## 🔗 Data Models & Relationships

### Entity Relationship Diagram

```
┌─────────────────┐
│   CustomUser    │ (Module 1)
│   (inherits     │
│   AbstractUser) │
└────────┬────────┘
         │
         ├──────────────────┬──────────────┬──────────────┐
         │                  │              │              │
    (1:N)│ owns         (1:N)│ owns    (1:N)│ sent     (M:N)│
         │              (contacts) │   (messages)  │
┌─────────▼──────────┐  ┌────▼──────────┐  ┌──────▼─────┐  ├──────────────┐
│ Contact           │  │ ContactGroup  │  │ SMSMessage │  │ MessageTemplate
│ (Module 3)        │  │ (Module 3)    │  │(Module 2)  │  │ (Module 3)
│                   │  │               │  │            │  │
│ - id (UUID)       │  │ - id (UUID)   │  │ - id (UUID)│  │ - id (UUID)
│ - owner_id (FK)   │  │ - owner_id    │  │ - sender   │  │ - name
│ - name            │  │ - name        │  │ - recipient│  │ - content
│ - phone           │  │ - color       │  │ - message  │  │ - variables
│ - email           │  │               │  │ - status   │  │ - is_active
│ - group_id (FK)   │  │               │  │            │  │
│ - is_favorite     │  │               │  │            │  │
│ - is_blocked      │  │               │  │  1:1       │  │
│ - notes           │  │               │  └────┬───────┘  └─────────────┘
│                   │  │               │       │
└──────────────────┘  └───────────────┘  (1:1)│
                                        ┌──────▼─────────────┐
                                        │ DeliveryStatus     │
                                        │ (Module 2)         │
                                        │                    │
                                        │ - id (UUID)        │
                                        │ - message_id (FK)  │
                                        │ - status           │
                                        │ - delivery_time    │
                                        │ - error_code       │
                                        │ - cost             │
                                        └────────────────────┘
```

### Relationships Summary

| From | To | Type | Description |
|------|-----|------|----------|
| CustomUser | Contact | 1:N | User owns multiple contacts |
| CustomUser | SMSMessage | 1:N | User sends multiple messages |
| ContactGroup | Contact | 1:N | Group has multiple contacts |
| SMSMessage | DeliveryStatus | 1:1 | Message has one delivery status |

---

## 🌐 API Routing

### Main Router (`smartsms/urls.py`)

```python
# Module 1: Authentication
/api/auth/*                    → apps.module_1_auth.urls

# Module 2: Messaging
/api/messaging/*               → apps.module_2_messaging.urls

# Module 3: Contacts
/api/contacts/*                → apps.module_3_contacts.urls

# Admin
/admin/                        → Django admin
```

### Module 1 Routes (`module_1_auth/urls.py`)

```
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/request-otp/
POST   /api/auth/verify-otp/
GET    /api/auth/profile/
PATCH  /api/auth/profile/
POST   /api/auth/change-password/
POST   /api/auth/token/refresh/
```

### Module 2 Routes (`module_2_messaging/urls.py`)

```
GET/POST    /api/messaging/messages/
GET/PATCH   /api/messaging/messages/{id}/
GET         /api/messaging/messages/{id}/delivery_status/
DELETE      /api/messaging/messages/{id}/
GET/POST    /api/messaging/templates/
```

### Module 3 Routes (`module_3_contacts/urls.py`)

```
GET/POST    /api/contacts/
GET/PATCH   /api/contacts/{id}/
DELETE      /api/contacts/{id}/
GET/POST    /api/contacts/groups/
GET/PATCH   /api/contacts/groups/{id}/
DELETE      /api/contacts/groups/{id}/
POST        /api/contacts/search/
POST        /api/contacts/import/
GET         /api/contacts/export/
```

---

## 🚀 Development Workflow

### Project Setup

```bash
# 1. Clone repository
git clone https://github.com/ClassyMuhi/smart-sms.git
cd smart-sms

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
cd smartsms
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Database setup
python manage.py migrate
python manage.py createsuperuser

# 6. Run server
python manage.py runserver
```

### Database Migrations

```bash
# Create migrations for a specific app
python manage.py makemigrations apps.module_1_auth
python manage.py makemigrations apps.module_2_messaging
python manage.py makemigrations apps.module_3_contacts

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

### Testing

```bash
# Run all tests
python manage.py test

# Run module-specific tests
python manage.py test apps.module_1_auth
python manage.py test apps.module_2_messaging
python manage.py test apps.module_3_contacts

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Adding New Features

#### For Module 1 (Auth):
1. Add model in `module_1_auth/models.py`
2. Create serializer in `module_1_auth/serializers.py`
3. Add viewset in `module_1_auth/views.py`
4. Register in `module_1_auth/urls.py`
5. Update `module_1_auth/admin.py`
6. Create migration: `python manage.py makemigrations apps.module_1_auth`
7. Test the endpoint

Similar workflow for Module 2 & 3.

---

## 🌍 Deployment

### Production Checklist

```
□ Set DEBUG = False in settings.py
□ Update SECRET_KEY (keep it secret!)
□ Configure ALLOWED_HOSTS
□ Set up HTTPS/SSL certificates
□ Configure CORS for frontend domain
□ Set up database (PostgreSQL recommended)
□ Configure Redis for caching
□ Set up Celery for async tasks
□ Configure SMS provider credentials
□ Enable CSRF protection
□ Set up logging & monitoring
□ Run security checks: python manage.py check --deploy
```

### Environment Variables for Production

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DATABASE_URL=postgresql://user:password@host:5432/smartsms
REDIS_URL=redis://localhost:6379/0

SMS_PROVIDER=twilio
SMS_API_KEY=your-api-key
SMS_API_SECRET=your-api-secret

DJANGO_SETTINGS_MODULE=smartsms.settings
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY smartsms/ .
RUN pip install -r requirements.txt
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Kubernetes Deployment

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: smartsms-app
spec:
  containers:
  - name: smartsms
    image: yourdomain/smartsms:latest
    ports:
    - containerPort: 8000
    env:
    - name: DEBUG
      value: "False"
    - name: SECRET_KEY
      valueFrom:
        secretKeyRef:
          name: smartsms-secrets
          key: secret-key
```

---

## 📋 Checklist for New Developers

- [ ] Clone repository
- [ ] Set up virtual environment
- [ ] Install requirements
- [ ] Configure `.env` file
- [ ] Run migrations
- [ ] Create superuser
- [ ] Understand module structure
- [ ] Read MODULE_1/2/3_*.md docs
- [ ] Explore API using admin panel
- [ ] Run tests locally
- [ ] Make your first API request
- [ ] Start developing!

---

## 🔗 Related Documentation

- [PROJECT README](../README.md) - Project overview
- [MODULE 1 AUTH](./MODULE_1_AUTH.md) - Authentication module
- [MODULE 2 MESSAGING](./MODULE_2_MESSAGING.md) - Messaging module
- [MODULE 3 CONTACTS](./MODULE_3_CONTACTS.md) - Contacts module
- [API EXAMPLES](./API_EXAMPLES.md) - Practical examples
- [MODELS DOCUMENTATION](./MODELS_DOCUMENTATION.md) - Database details

---

**Last Updated:** 2024-04-05
**Author:** ClassyMuhi
**Version:** 1.0.0
