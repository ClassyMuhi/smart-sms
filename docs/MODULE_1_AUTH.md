# Module 1: Authentication & User Management

**Location:** `smartsms/apps/module_1_auth/`

---

## 📌 Overview

Module 1 handles user registration, authentication, OTP verification, and account management. It provides secure phone-based authentication using JWT tokens.

## 🗂️ Folder Structure

```
module_1_auth/
├── __init__.py
├── admin.py                    # Django admin configurations
├── apps.py                     # App configuration
├── models.py                   # Database models (CustomUser, OTP, etc.)
├── serializers.py              # DRF serializers for validation
├── views.py                    # API endpoints and viewsets
├── urls.py                     # URL routing
├── utils.py                    # Utility functions (OTP generation, etc.)
├── signals.py                  # Django signals (user creation, etc.)
└── migrations/                 # Database migrations
```

## 📊 Database Models

### CustomUser Model
```python
{
    "id": "uuid",
    "email": "user@example.com",
    "phone": "+1234567890",
    "full_name": "John Doe",
    "is_phone_verified": true,
    "is_active": true,
    "date_joined": "2024-04-05T10:00:00Z"
}
```

**Fields:**
- `id` - UUID primary key
- `email` - Unique email address
- `phone` - Unique phone number (primary identifier)
- `full_name` - User's full name
- `is_phone_verified` - Phone verification status
- `is_active` - Account active status

### OTP Log Model
- Tracks all OTP requests and verification attempts
- Includes timestamp and phone number

### Login History Model
- Records all user login events
- Useful for security and auditing

---

## 🔌 API Endpoints

### 1. User Registration
```
POST /api/auth/register/
```

**Request:**
```json
{
    "phone": "+1234567890",
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
}
```

**Response (201):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "phone": "+1234567890",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_phone_verified": false
}
```

### 2. Request OTP
```
POST /api/auth/request-otp/
```

**Request:**
```json
{
    "phone": "+1234567890"
}
```

**Response (200):**
```json
{
    "message": "OTP sent successfully",
    "phone": "+1234567890"
}
```

### 3. Verify OTP
```
POST /api/auth/verify-otp/
```

**Request:**
```json
{
    "phone": "+1234567890",
    "otp": "123456"
}
```

**Response (200):**
```json
{
    "is_verified": true,
    "message": "Phone verified successfully"
}
```

### 4. User Login
```
POST /api/auth/login/
```

**Request:**
```json
{
    "phone": "+1234567890",
    "password": "securepassword"
}
```

**Response (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "phone": "+1234567890",
        "email": "user@example.com"
    }
}
```

### 5. Refresh Token
```
POST /api/auth/token/refresh/
```

**Request:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 6. Get User Profile
```
GET /api/auth/profile/
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "phone": "+1234567890",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_phone_verified": true,
    "is_active": true,
    "date_joined": "2024-04-05T10:00:00Z"
}
```

### 7. Update Profile
```
PATCH /api/auth/profile/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
    "email": "newemail@example.com",
    "full_name": "Jane Doe"
}
```

**Response (200):** Updated user object

### 8. Change Password
```
POST /api/auth/change-password/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
    "old_password": "oldpassword",
    "new_password": "newpassword"
}
```

**Response (200):**
```json
{
    "message": "Password changed successfully"
}
```

### 9. Reset PIN
```
POST /api/auth/reset-pin/
Authorization: Bearer {access_token}
```

**Request:**
```json
{
    "new_pin": "1234"
}
```

**Response (200):**
```json
{
    "message": "PIN reset successfully"
}
```

---

## 🔐 Security Features

### Password Validation
- Minimum 8 characters
- Mix of uppercase and lowercase letters
- At least one number
- At least one special character

### Phone Validation
- Format: +1234567890 or 1234567890
- 9-15 digits
- International format support

### OTP Security
- 6-digit random OTP
- 5-minute expiration
- Rate limiting (max 3 attempts per hour)
- Account lockout after failed attempts

### JWT Tokens
- Access token: 5 minutes validity
- Refresh token: 24 hours validity
- Algorithm: HS256
- Claims: user_id, phone, email

---

## 🧪 Testing

```python
# Test user registration
POST /api/auth/register/
{
    "phone": "+1234567890",
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
}

# Test OTP flow
POST /api/auth/request-otp/
POST /api/auth/verify-otp/

# Test login
POST /api/auth/login/

# Test profile access (requires token)
GET /api/auth/profile/
Header: Authorization: Bearer {token}
```

---

## 🔧 Configuration

### settings.py
```python
AUTH_USER_MODEL = 'module_1_auth.CustomUser'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ALGORITHM': 'HS256',
}

# OTP Configuration
OTP_VALIDITY_MINUTES = 5
OTP_LENGTH = 6
OTP_MAX_ATTEMPTS = 3
```

---

## 📝 Common Use Cases

### 1. User Registration & Verification
1. Call `/register/` endpoint
2. Request OTP via `/request-otp/`
3. Verify OTP via `/verify-otp/`
4. Login with credentials

### 2. Password Reset Flow
1. Generate OTP for phone
2. Verify OTP
3. Allow user to set new password

### 3. Session Management
1. Login with phone + password
2. Delete refresh token to logout
3. Use access token for all requests

---

## 🚀 Best Practices

- Always use HTTPS in production
- Never log passwords or OTPs
- Implement rate limiting on OTP requests
- Store hashed passwords only
- Implement account lockout after failed attempts
- Use JWT refresh tokens for long-lived sessions
- Validate phone numbers before OTP generation

---

## ⚠️ Common Issues

**Issue:** OTP not received
- **Solution:** Check phone number format (+1234567890)
- **Solution:** Verify SMS provider credentials
- **Solution:** Check rate limiting

**Issue:** Login fails with valid credentials
- **Solution:** Check phone number verification status
- **Solution:** Verify account is active

**Issue:** Token expiration errors
- **Solution:** Refresh token using refresh endpoint
- **Solution:** Re-login if refresh token expired

---

## 📚 Related Files

- [API Examples](../API_EXAMPLES.md)
- [Models Documentation](../MODELS_DOCUMENTATION.md)
- [Test Cases](../TEST_CASES.md)
