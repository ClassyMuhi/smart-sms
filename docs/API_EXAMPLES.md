# API Examples - cURL Commands

This file contains all API endpoints with cURL examples for testing.

## Base URL
```
http://localhost:8000/api/
```

---

## 1. REGISTRATION & AUTHENTICATION

### 1.1 Register New User

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

**Response (201 Created):**
```json
{
  "message": "Registration successful. Please verify your phone with OTP.",
  "phone": "+1234567890",
  "otp_sent_to": "+1234567890",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Console Output:**
```
==================================================
OTP for registration: 123456
Valid for 5 minutes
==================================================
```

---

### 1.2 Verify OTP

```bash
curl -X POST http://localhost:8000/api/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "otp_code": "123456"
  }'
```

**Response (200 OK):**
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

---

### 1.3 User Login

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_or_email": "+1234567890",
    "password": "SecurePass123!"
  }'
```

**Response (200 OK):**
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
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Save the `access` token for authenticated requests!**

---

### 1.4 Logout

```bash
curl -X POST http://localhost:8000/api/logout/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGci..."
```

**Response (200 OK):**
```json
{
  "message": "Logged out successfully."
}
```

---

## 2. USER PROFILE MANAGEMENT

### 2.1 Get User Profile (Authenticated)

```bash
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGci..."
```

**Response (200 OK):**
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

---

### 2.2 Update User Profile

```bash
curl -X PATCH http://localhost:8000/api/update-profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Updated",
    "email": "newemail@example.com"
  }'
```

**Response (200 OK):**
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

---

### 2.3 Get Login History

```bash
curl -X GET http://localhost:8000/api/login-history/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGci..."
```

**Response (200 OK):**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "ip_address": "127.0.0.1",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "login_at": "2024-01-15T10:40:00Z"
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174000",
    "ip_address": "192.168.1.100",
    "user_agent": "curl/7.64.1",
    "login_at": "2024-01-15T09:15:00Z"
  }
]
```

---

## 3. PASSWORD MANAGEMENT

### 3.1 Change Password (Authenticated)

```bash
curl -X POST http://localhost:8000/api/change-password/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePass123!",
    "new_password": "NewSecurePass123!",
    "new_password_confirm": "NewSecurePass123!"
  }'
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully."
}
```

---

### 3.2 Forgot Password - Request OTP

```bash
curl -X POST http://localhost:8000/api/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_or_email": "+1234567890"
  }'
```

**Response (200 OK):**
```json
{
  "message": "OTP sent to your registered phone/email.",
  "phone_or_email": "+1234567890"
}
```

**Console Output:**
```
==================================================
Password reset OTP: 654321
Valid for 5 minutes
==================================================
```

---

### 3.3 Reset Password with OTP

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

**Response (200 OK):**
```json
{
  "message": "Password reset successfully.",
  "phone_or_email": "+1234567890"
}
```

---

## 4. TOKEN MANAGEMENT

### 4.1 Refresh Access Token

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## ERROR EXAMPLES

### Invalid Phone Format
```json
{
  "phone": [
    "Phone number must be between 9 and 15 digits. Format: +1234567890 or 1234567890"
  ]
}
```

### Weak Password
```json
{
  "password": [
    "Password must contain at least one uppercase letter."
  ]
}
```

### OTP Expired
```json
{
  "error": "OTP has expired. Request a new one."
}
```

### Invalid OTP
```json
{
  "error": "Invalid OTP.",
  "remaining_attempts": 3
}
```

### Max Attempts Exceeded
```json
{
  "error": "Maximum OTP verification attempts exceeded."
}
```

### User Not Found
```json
{
  "error": "No user found with this phone/email."
}
```

### Passwords Don't Match
```json
{
  "error": "Passwords do not match."
}
```

### Phone Already Registered
```json
{
  "phone": [
    "Phone number already registered."
  ]
}
```

### Unauthorized (Missing Token)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Invalid Token
```json
{
  "detail": "Given token not valid for any token type"
}
```

---

## Testing Tips

1. **Use Postman** for easier request management
   - Import this file as a collection
   - Save tokens in environment variables
   - Use pre-request scripts to automate flows

2. **Use Python Requests** for automation
   ```python
   import requests
   
   response = requests.post(
       'http://localhost:8000/api/register/',
       json={
           "phone": "+1234567890",
           "email": "user@example.com",
           "full_name": "John Doe",
           "password": "SecurePass123!",
           "password_confirm": "SecurePass123!"
       }
   )
   print(response.json())
   ```

3. **Check Console Output** for OTP codes during development

4. **Token Duration:**
   - Access Token: 1 hour
   - Refresh Token: 7 days

5. **OTP Duration:** 5 minutes (check settings.py to change)

---

## Common Workflows

### Complete Registration Flow
```bash
# 1. Register
curl -X POST http://localhost:8000/api/register/ ...

# 2. Verify OTP (use OTP from console)
curl -X POST http://localhost:8000/api/verify-otp/ ...

# 3. Login
curl -X POST http://localhost:8000/api/login/ ...

# 4. Access Protected Routes (use access token)
curl -X GET http://localhost:8000/api/profile/ ...
```

### Password Reset Flow
```bash
# 1. Request Password Reset OTP
curl -X POST http://localhost:8000/api/forgot-password/ ...

# 2. Reset Password (use OTP from console)
curl -X POST http://localhost:8000/api/reset-password/ ...

# 3. Login with New Password
curl -X POST http://localhost:8000/api/login/ ...
```

### Change Password Flow
```bash
# 1. Login with Old Password
curl -X POST http://localhost:8000/api/login/ ...

# 2. Change to New Password (use access token)
curl -X POST http://localhost:8000/api/change-password/ ...

# 3. Login with New Password
curl -X POST http://localhost:8000/api/login/ ...
```

---

**Happy Testing! 🧪**
