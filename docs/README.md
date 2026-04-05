# Smart SMS - Authentication & User Management Module

A complete **Django + Django REST Framework + PostgreSQL** authentication and user management system for the Smart SMS application.

## Features

### ✅ Authentication & Authorization
- **User Registration** with validation (phone, email, password strength)
- **User Login** with JWT token generation
- **OTP Verification** (6-digit OTP with 5-minute expiry)
- **Forgot Password** with OTP verification
- **Reset Password** using OTP
- **Secure Logout** with token management
- **JWT-based Authentication** with access + refresh tokens

### ✅ Security Features
- **Password Hashing** using Django's PBKDF2 algorithm
- **Password Strength Validation** (uppercase, lowercase, digit, special char)
- **Phone Number Validation** with regex pattern
- **OTP Rate Limiting** (Max 5 attempts per OTP)
- **OTP Expiry** (Default: 5 minutes)
- **CORS Configuration** for safe cross-origin requests
- **Login History Tracking** (IP address, user agent, timestamp)

### ✅ Models
- **CustomUser** - Extended Django User model with phone-based authentication
- **OTPVerification** - Stores OTP records with expiry and attempt tracking
- **UserLoginHistory** - Tracks user login activities

### ✅ APIs
- `POST /api/register/` - User registration
- `POST /api/login/` - User login (returns JWT tokens)
- `POST /api/verify-otp/` - OTP verification
- `POST /api/forgot-password/` - Request OTP for password reset
- `POST /api/reset-password/` - Reset password with OTP
- `POST /api/logout/` - Logout (discard tokens)
- `GET /api/profile/` - Get authenticated user profile
- `PATCH /api/update-profile/` - Update user info
- `POST /api/change-password/` - Change password
- `GET /api/login-history/` - View login history
- `POST /api/token/refresh/` - Refresh JWT token

---

## Project Structure

```
smartsms/
├── manage.py
├── requirements.txt
├── README.md
│
├── smartsms/
│   ├── __init__.py
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
│
└── auth_module/
    ├── __init__.py
    ├── apps.py              # App configuration
    ├── admin.py             # Django admin interface
    ├── models.py            # Database models
    ├── serializers.py       # DRF serializers
    ├── views.py             # API views
    ├── urls.py              # App URL routing
    ├── utils.py             # Utility functions
    ├── signals.py           # Django signals
    └── migrations/          # Database migrations
```

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone/Download Project

```bash
cd smartsms
```

### Step 2: Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Database

**Create PostgreSQL Database:**

```sql
-- Open PostgreSQL terminal (psql)
CREATE DATABASE smartsms_db;
CREATE USER postgres WITH PASSWORD 'your_password_here';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET default_transaction_deferrable TO off;
ALTER ROLE postgres SET default_transaction_read_only TO off;
ALTER ROLE postgres SET default_time_zone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE smartsms_db TO postgres;
\q
```

**Update settings.py:**

Edit `smartsms/settings.py` and update the DATABASES configuration:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smartsms_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password_here',  # Use your PostgreSQL password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**OR use SQLite for Development (no PostgreSQL needed):**

If you don't have PostgreSQL installed, comment out the PostgreSQL config and uncomment SQLite:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Step 5: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Enter details:
- Phone: +1234567890
- Email: admin@example.com
- Full Name: Admin User
- Password: Your secure password

### Step 7: Run Development Server

```bash
python manage.py runserver
```

Server starts at: `http://127.0.0.1:8000/`

---

## API Usage Examples

### 1. User Registration

**Request:**
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "email": "user@example.com",
    "full_name": "John Doe",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "message": "Registration successful. Please verify your phone with OTP.",
  "phone": "+1234567890",
  "otp_sent_to": "+1234567890",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Console Output (OTP):**
```
==================================================
OTP for registration: 123456
Valid for 5 minutes
==================================================
```

### 2. Verify OTP

**Request:**
```bash
curl -X POST http://localhost:8000/api/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "otp_code": "123456"
  }'
```

**Response:**
```json
{
  "message": "Phone verified successfully.",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "phone": "+1234567890",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_phone_verified": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z",
    "last_login_at": null
  }
}
```

### 3. User Login

**Request:**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_or_email": "+1234567890",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "message": "Login successful.",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "phone": "+1234567890",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_phone_verified": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z",
    "last_login_at": "2024-01-15T10:40:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 4. Get User Profile (Authenticated)

**Request:**
```bash
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "phone": "+1234567890",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_phone_verified": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "last_login_at": "2024-01-15T10:40:00Z"
}
```

### 5. Update Profile (Authenticated)

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/update-profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Updated",
    "email": "newemail@example.com"
  }'
```

**Response:**
```json
{
  "message": "Profile updated successfully.",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "phone": "+1234567890",
    "email": "newemail@example.com",
    "full_name": "John Updated",
    "is_phone_verified": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:45:00Z",
    "last_login_at": "2024-01-15T10:40:00Z"
  }
}
```

### 6. Change Password (Authenticated)

**Request:**
```bash
curl -X POST http://localhost:8000/api/change-password/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePass123!",
    "new_password": "NewSecurePass123!",
    "new_password_confirm": "NewSecurePass123!"
  }'
```

**Response:**
```json
{
  "message": "Password changed successfully."
}
```

### 7. Forgot Password - Request OTP

**Request:**
```bash
curl -X POST http://localhost:8000/api/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_or_email": "+1234567890"
  }'
```

**Response:**
```json
{
  "message": "OTP sent to your registered phone/email.",
  "phone_or_email": "+1234567890"
}
```

### 8. Reset Password with OTP

**Request:**
```bash
curl -X POST http://localhost:8000/api/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_or_email": "+1234567890",
    "otp_code": "654321",
    "new_password": "NewSecurePass456!",
    "new_password_confirm": "NewSecurePass456!"
  }'
```

**Response:**
```json
{
  "message": "Password reset successfully.",
  "phone_or_email": "+1234567890"
}
```

### 9. Refresh JWT Token

**Request:**
```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 10. Login History

**Request:**
```bash
curl -X GET http://localhost:8000/api/login-history/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "ip_address": "127.0.0.1",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0...",
    "login_at": "2024-01-15T10:40:00Z"
  }
]
```

---

## Configuration Details

### JWT Settings (in `settings.py`)

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),      # Token expires in 1 hour
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # Refresh token valid for 7 days
    'ROTATE_REFRESH_TOKENS': True,                    # Always rotate refresh tokens
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
}
```

### OTP Settings (in `settings.py`)

```python
OTP_EXPIRY_MINUTES = 5      # OTP valid for 5 minutes
OTP_LENGTH = 6              # 6-digit OTP
```

### Database Indexes

For optimal performance, the following database indexes are created:
- `CustomUser` - indexes on `phone`, `email`, and `created_at`
- `OTPVerification` - indexes on `(user, created_at)` and `otp_code`
- `UserLoginHistory` - indexes on `(user, login_at)`

---

## Admin Panel

Access Django Admin at: `http://localhost:8000/admin/`

**Login Credentials:**
- Username (Phone): +1234567890
- Password: (Your superuser password)

### Admin Features:
- View/manage users
- Monitor OTP records
- Track login history
- User permissions management

---

## Password Requirements

The system enforces strong password requirements:
- ✅ Minimum 8 characters
- ✅ At least 1 uppercase letter
- ✅ At least 1 lowercase letter
- ✅ At least 1 digit
- ✅ At least 1 special character (!@#$%^&*)

**Example Valid Passwords:**
- `SecurePass123!`
- `MyP@ssw0rd2024`
- `Admin#2024`

---

## Phone Number Format

Accepted international phone number formats:
- `+1234567890` (with country code)
- `1234567890` (without country code)

Must be 9-15 digits long without spaces or special characters (except leading +).

---

## Error Handling

### Common Error Responses

**Invalid Phone Format:**
```json
{
  "phone": ["Phone number must be between 9 and 15 digits..."]
}
```

**Weak Password:**
```json
{
  "password": ["Password must contain at least one uppercase letter."]
}
```

**OTP Expired:**
```json
{
  "error": "OTP has expired. Request a new one."
}
```

**Max OTP Attempts Exceeded:**
```json
{
  "error": "Maximum OTP verification attempts exceeded."
}
```

**User Not Found:**
```json
{
  "error": "No user found with this phone/email."
}
```

---

## Testing with Postman

1. Import the API collection (example):
   - Base URL: `http://localhost:8000/api/`
   - Copy endpoints from examples above

2. Test Registration → Verify OTP → Login flow

3. Use access token with "Bearer" prefix in Authorization header

---

## Security Best Practices

✅ **Implemented:**
- Password hashing using PBKDF2
- JWT token-based authentication
- OTP rate limiting (5 attempts max)
- OTP expiry (5 minutes)
- Login history tracking
- CORS configuration
- Phone number validation

⚠️ **Production Recommendations:**
1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS` properly
4. Use HTTPS only
5. Configure email/SMS gateway
6. Set up logging and monitoring
7. Regular security audits
8. Enable rate limiting on APIs
9. Add 2FA/MFA support
10. Use environment variables for sensitive data

---

## Troubleshooting

### PostgreSQL Connection Error
**Error:** `could not connect to server: Connection refused`

**Solution:**
- Ensure PostgreSQL is running
- Check connection credentials in `settings.py`
- Use SQLite instead for development

### Migration Errors
**Error:** `No changes detected in app 'auth_module'`

**Solution:**
```bash
python manage.py makemigrations auth_module
python manage.py migrate
```

### OTP Not Appearing
**Issue:** OTP is printed to console instead of being sent

**Solution:**
- Integration with SMS/Email gateway needed in `utils.py`
- Check console output for OTP code during testing

### JWT Token Invalid
**Error:** `Token is invalid or expired`

**Solution:**
- Tokens expire after 1 hour
- Use refresh token endpoint to get new access token
- Check token format in Authorization header

---

## Future Enhancements

- [ ] Email verification before login
- [ ] Social authentication (Google, Facebook)
- [ ] Two-Factor Authentication (2FA)
- [ ] Biometric authentication
- [ ] API rate limiting
- [ ] User roles and permissions
- [ ] Email/SMS gateway integration
- [ ] Password reset via email link
- [ ] Account lockout after failed attempts
- [ ] User activity audit log
- [ ] Multi-device session management

---

## Support & Documentation

For more information:
- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- JWT: https://django-rest-framework-simplejwt.readthedocs.io/

---

## License

This project is open source and available under the MIT License.

---

**Built with ❤️ for Smart SMS Authentication**

Last Updated: 2024
