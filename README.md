
# Smart SMS - Professional Django SMS Management System

A comprehensive, modular Django backend system for managing SMS communications with features for user authentication, message sending, and contact management.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Django](https://img.shields.io/badge/Django-4.0%2B-green)
![DRF](https://img.shields.io/badge/DRF-3.13%2B-red)
![License](https://img.shields.io/badge/License-MIT-blue)

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Modules](#modules)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Development](#development)

---

## 🎯 Project Overview

Smart SMS is an enterprise-grade SMS management system built with Django REST Framework. It provides a secure, scalable platform for handling SMS communications including sending, receiving, delivery tracking, and contact management.

### Key Capabilities:
- ✅ User authentication with OTP verification
- ✅ SMS sending and receiving
- ✅ Real-time delivery status tracking
- ✅ Contact management and organization
- ✅ Message templates and scheduling
- ✅ Comprehensive audit logging
- ✅ RESTful API with JWT authentication

---

## ✨ Features

### 🔐 Security & Authentication
- Phone-based authentication system
- OTP (One-Time Password) verification
- JWT token-based authorization
- Pin/Password management
- Email verification support

### 📱 Messaging System
- Send SMS messages
- Receive inbound messages
- Message delivery tracking
- Multi-segment SMS handling
- Message templates library
- Scheduled message sending
- Cost tracking per message

### 👥 Contact Management
- Create and manage contacts
- Advanced search and filtering
- Contact grouping and organization
- Contact import/export
- Recent contacts tracking

---

## 📁 Project Structure

```
smart-sms/
│
├── smartsms/                          # Main Django project
│   ├── smartsms/                      # Project configuration
│   │   ├── settings.py               # Django settings
│   │   ├── urls.py                   # Main URL router
│   │   ├── asgi.py                   # ASGI config
│   │   └── wsgi.py                   # WSGI config
│   │
│   ├── apps/                          # All application modules
│   │   ├── module_1_auth/            # Authentication module
│   │   ├── module_2_messaging/       # Messaging module
│   │   └── module_3_contacts/        # Contacts module
│   │
│   ├── manage.py                      # Django management
│   ├── requirements.txt               # Python dependencies
│   └── db.sqlite3                     # Development database
│
├── docs/                              # Documentation
│   ├── API_EXAMPLES.md
│   ├── MODELS_DOCUMENTATION.md
│   ├── CONTACT_MANAGEMENT_GUIDE.md
│   └── ...
│
├── scripts/                           # Utility scripts
│   ├── startup.sh                     # Linux startup
│   ├── startup.bat                    # Windows startup
│   └── create_admin.py                # Admin creation
│
├── tests/                             # Test files
│   └── test_register.py
│
├── .env.example                       # Environment template
├── .gitignore
├── README.md
└── venv/                              # Virtual environment (excluded)
```

---

## 🏗️ Modules

### **Module 1: Authentication & User Management**

**Location:** `smartsms/apps/module_1_auth/`

**Responsibility:** Handle user registration, authentication, OTP verification, and account management.

**Key Components:**
- `models.py` - CustomUser model with phone-based auth
- `views.py` - Authentication endpoints
- `serializers.py` - Data validation and serialization
- `utils.py` - OTP generation and verification
- `signals.py` - User signup/account signals

**Main Features:**
- User registration with phone number
- Email verification
- OTP-based authentication
- Password/PIN reset
- User profile management
- Account activation/deactivation
- Login history tracking

**API Endpoints:**
```
POST   /api/auth/register/                  # Register new user
POST   /api/auth/login/                     # User login
POST   /api/auth/verify-otp/                # Verify OTP
POST   /api/auth/refresh-token/             # Refresh JWT token
GET    /api/auth/profile/                   # Get user profile
PATCH  /api/auth/profile/update/            # Update profile
POST   /api/auth/change-password/           # Change password
POST   /api/auth/reset-pin/                 # Reset personal PIN
```

**Database Models:**
- `CustomUser` - Extended Django User model
- `OTPLog` - OTP verification records
- `LoginHistory` - User login tracking
- `UserPreferences` - User settings and preferences

---

### **Module 2: Messaging (SMS Core)**

**Location:** `smartsms/apps/module_2_messaging/`

**Responsibility:** Handle SMS sending, receiving, delivery tracking, and message management.

**Key Components:**
- `models.py` - SMSMessage, DeliveryStatus, MessageTemplate models
- `views.py` - SMS endpoints and viewsets
- `serializers.py` - Message serialization
- `urls.py` - Message routing

**Main Features:**
- Send SMS messages
- Receive and store inbound messages
- Real-time delivery status tracking
- Message character counting
- Multi-segment SMS handling
- Message templates library
- Cost calculation per message
- Delivery failure handling

**API Endpoints:**
```
GET    /api/messaging/messages/             # List all messages
POST   /api/messaging/messages/             # Send new SMS
GET    /api/messaging/messages/{id}/        # Get message details
GET    /api/messaging/messages/{id}/delivery_status/  # Check delivery
DELETE /api/messaging/messages/{id}/        # Delete message

GET    /api/messaging/templates/            # List templates
POST   /api/messaging/templates/            # Create template
PATCH  /api/messaging/templates/{id}/       # Update template
DELETE /api/messaging/templates/{id}/       # Delete template
```

**Database Models:**
- `SMSMessage` - Core message model
- `DeliveryStatus` - Delivery tracking
- `MessageTemplate` - Reusable templates

**Status Types:**
```
- Draft: Message not yet sent
- Pending: Waiting to be sent
- Sending: Currently transmitting
- Sent: Successfully sent
- Failed: Delivery failed
- Received: Inbound message
```

---

### **Module 3: Contact Management**

**Location:** `smartsms/apps/module_3_contacts/`

**Responsibility:** Handle contact creation, storage, searching, and management.

**Key Components:**
- `models.py` - Contact and Group models
- `views.py` - Contact endpoints
- `serializers.py` - Contact serialization
- `urls.py` - Contact routing

**Main Features:**
- Create and manage contacts
- Contact grouping and organization
- Advanced search and filtering
- Contact import/export (CSV)
- Last contacted tracking
- Favorite contacts
- Contact blocking
- Bulk operations

**API Endpoints:**
```
GET    /api/contacts/                       # List all contacts
POST   /api/contacts/                       # Create new contact
GET    /api/contacts/{id}/                  # Get contact details
PATCH  /api/contacts/{id}/                  # Update contact
DELETE /api/contacts/{id}/                  # Delete contact

GET    /api/contacts/groups/                # List groups
POST   /api/contacts/groups/                # Create group
PATCH  /api/contacts/groups/{id}/           # Update group
DELETE /api/contacts/groups/{id}/           # Delete group

POST   /api/contacts/import/                # Import contacts (CSV)
GET    /api/contacts/export/                # Export contacts
POST   /api/contacts/search/                # Advanced search
```

**Database Models:**
- `Contact` - Individual contact record
- `ContactGroup` - Contact grouping
- `ContactInteraction` - Track last interaction

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/ClassyMuhi/smart-sms.git
cd smart-sms
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
cd smartsms
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Set:
# - SECRET_KEY (generate one: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
# - DEBUG = False (for production)
# - ALLOWED_HOSTS
# - Database URL
# - SMS Provider API Keys
```

### Step 5: Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Or use the script
python manage.py shell < ../scripts/create_admin.py
```

### Step 6: Run Development Server

```bash
python manage.py runserver
```

Access the application at: `http://localhost:8000`

---

## ⚙️ Configuration

### Django Settings

Edit `smartsms/settings.py`:

```python
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ALGORITHM': 'HS256',
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]

# SMS Provider (Configure based on your provider)
SMS_PROVIDER = 'twilio'  # or 'nexmo', 'aws-sns', etc.
SMS_PROVIDER_API_KEY = 'your-api-key'
SMS_PROVIDER_API_SECRET = 'your-api-secret'
```

### Environment Variables (.env)

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
SMS_PROVIDER=twilio
SMS_PROVIDER_API_KEY=your-key
SMS_PROVIDER_API_SECRET=your-secret
REDIS_URL=redis://localhost:6379/0
```

---

## 📚 API Documentation

### Authentication

All endpoints (except registration/login) require JWT token in header:

```bash
Authorization: Bearer {access_token}
```

### Response Format

**Success Response (200):**
```json
{
    "status": "success",
    "data": { ... },
    "message": "Operation completed successfully"
}
```

**Error Response (4xx/5xx):**
```json
{
    "status": "error",
    "error_code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": { ... }
}
```

### Example: Send SMS

**Request:**
```bash
curl -X POST http://localhost:8000/api/messaging/messages/ \
-H "Authorization: Bearer {token}" \
-H "Content-Type: application/json" \
-d '{
    "recipient": "+1234567890",
    "message": "Hello, this is a test message!"
}'
```

**Response:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "recipient": "+1234567890",
    "message": "Hello, this is a test message!",
    "status": "sent",
    "created_at": "2024-04-05T10:30:00Z"
}
```

---

## 🧪 Testing

### Run Tests

```bash
cd smartsms

# Run all tests
python manage.py test

# Run specific module tests
python manage.py test apps.module_1_auth
python manage.py test apps.module_2_messaging
python manage.py test apps.module_3_contacts

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Files Location

```
tests/
├── test_register.py          # Auth module tests
└── ...
```

---

## 👨‍💻 Development

### Project Commands

```bash
# Create admin user
python manage.py createsuperuser

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell

# Check project health
python manage.py check

# Format code
black .

# Run linter
flake8

# Run type checker
mypy .
```

### Startup Scripts

```bash
# Windows
./scripts/startup.bat

# Linux/Mac
./scripts/startup.sh
```

---

## 📖 Documentation Files

- [API Examples](./docs/API_EXAMPLES.md) - Detailed API usage examples
- [Models Documentation](./docs/MODELS_DOCUMENTATION.md) - Database model details
- [Contact Management Guide](./docs/CONTACT_MANAGEMENT_GUIDE.md) - Contact features
- [Architecture & Deployment](./docs/ARCHITECTURE_DEPLOYMENT.md) - Production setup
- [Test Cases](./docs/TEST_CASES.md) - Testing guide

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 4.0+ |
| **REST API** | Django REST Framework |
| **Authentication** | JWT (SimpleJWT) |
| **Database** | SQLite / PostgreSQL |
| **Validation** | Serializers, Validators |
| **Task Queue** | Celery (Optional) |
| **Caching** | Redis (Optional) |
| **Environment** | Python 3.8+ |

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👤 Author

**ClassyMuhi**

- GitHub: [@ClassyMuhi](https://github.com/ClassyMuhi)
- Repository: [smart-sms](https://github.com/ClassyMuhi/smart-sms)

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 Changelog

### v1.0.0 (2024-04-05)
- ✅ Initial modular structure
- ✅ Module 1: Authentication
- ✅ Module 2: Messaging
- ✅ Module 3: Contacts
- ✅ JWT authentication
- ✅ REST API endpoints

---

## 🆘 Support

For support, email support@smartsms.dev or open an issue on GitHub.

---

**⭐ If you find this project useful, please consider giving it a star!**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd smartsms
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create admin user**
   ```bash
   python scripts/create_admin.py
   ```

7. **Start the server**
   ```bash
   python manage.py runserver
   ```

## Features

- Send predefined messages
- Schedule SMS delivery
- Contact management
- Message templates
- User authentication
- Conversation tracking

## Documentation

See the [docs/](./docs/) folder for detailed documentation:
- [API Examples](./docs/API_EXAMPLES.md)
- [Models Documentation](./docs/MODELS_DOCUMENTATION.md)
- [Contact Management Guide](./docs/CONTACT_MANAGEMENT_GUIDE.md)

## Scripts

Utility scripts are located in the [scripts/](./scripts/) folder:
- `startup.sh` / `startup.bat` - Start the application
- `create_admin.py` - Create an admin user

## Testing

Run tests from the project root:
```bash
cd smartsms
python manage.py test
```

Or run specific test files from the [tests/](./tests/) folder.

## Technology Stack

- **Backend**: Django
- **Database**: SQLite
- **Language**: Python
- **API**: REST API

## License

[Add your license here]

## Author

ClassyMuhi
