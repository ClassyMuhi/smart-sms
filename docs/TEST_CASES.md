# Django Smart SMS Authentication Module
# Testing and Development Configuration

## Quick Test Case Examples

### Test Case 1: Valid Registration
**Scenario:** User registers with valid credentials
**Input:**
```json
{
  "phone": "+15551234567",
  "email": "testuser@example.com",
  "full_name": "Test User",
  "password": "TestSecure123!",
  "password_confirm": "TestSecure123!"
}
```
**Expected:** 201 Created - User registered successfully
**OTP:** Check console for 6-digit code

---

### Test Case 2: Invalid Phone Format
**Scenario:** User registers with invalid phone format
**Input:**
```json
{
  "phone": "12345",
  "email": "testuser@example.com",
  "full_name": "Test User",
  "password": "TestSecure123!",
  "password_confirm": "TestSecure123!"
}
```
**Expected:** 400 Bad Request - Phone validation error

---

### Test Case 3: Weak Password
**Scenario:** User tries to register with weak password (no special char)
**Input:**
```json
{
  "phone": "+15551234567",
  "email": "testuser@example.com",
  "full_name": "Test User",
  "password": "TestSecure123",
  "password_confirm": "TestSecure123"
}
```
**Expected:** 400 Bad Request - Password must contain special character

---

### Test Case 4: Password Mismatch
**Scenario:** Password and confirm password don't match
**Input:**
```json
{
  "phone": "+15551234567",
  "email": "testuser@example.com",
  "full_name": "Test User",
  "password": "TestSecure123!",
  "password_confirm": "DifferentPass123!"
}
```
**Expected:** 400 Bad Request - Passwords do not match

---

### Test Case 5: Duplicate Phone
**Scenario:** User tries to register with already registered phone
**Steps:**
1. Register user with phone +15551234567
2. Try to register another user with same phone
**Expected:** 400 Bad Request - Phone number already registered

---

### Test Case 6: Duplicate Email
**Scenario:** User tries to register with already registered email
**Expected:** 400 Bad Request - Email already registered

---

### Test Case 7: Valid OTP Verification
**Scenario:** User verifies with correct OTP within 5 minutes
**Input:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "otp_code": "123456"
}
```
**Expected:** 200 OK - Phone verified successfully

---

### Test Case 8: Invalid OTP
**Scenario:** User enters wrong OTP
**Input:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "otp_code": "000000"
}
```
**Expected:** 400 Bad Request - Invalid OTP
**Side Effect:** Attempt counter incremented

---

### Test Case 9: OTP Expired
**Scenario:** User tries to verify OTP after 5+ minutes
**Wait:** 5 minutes after registration
**Input:** Valid OTP code (but expired)
**Expected:** 400 Bad Request - OTP has expired

---

### Test Case 10: Max OTP Attempts
**Scenario:** User makes 5 failed OTP attempts
**Steps:**
1. Try invalid OTP 5 times
2. Try with valid OTP on 6th attempt
**Expected:** 400 Bad Request - Maximum OTP verification attempts exceeded

---

### Test Case 11: Login with Phone - Success
**Scenario:** Verified user logs in with phone
**Input:**
```json
{
  "phone_or_email": "+15551234567",
  "password": "TestSecure123!"
}
```
**Expected:** 200 OK - Login successful, access token returned

---

### Test Case 12: Login with Email - Success
**Scenario:** Verified user logs in with email
**Input:**
```json
{
  "phone_or_email": "testuser@example.com",
  "password": "TestSecure123!"
}
```
**Expected:** 200 OK - Login successful, access token returned

---

### Test Case 13: Login Unverified User
**Scenario:** User tries to login without phone verification
**Input:** Valid credentials but not verified
**Expected:** 403 Forbidden - Phone number not verified

---

### Test Case 14: Invalid Login Credentials
**Scenario:** User enters wrong password
**Input:**
```json
{
  "phone_or_email": "+15551234567",
  "password": "WrongPassword123!"
}
```
**Expected:** 400 Bad Request - Phone/Email or password is incorrect

---

### Test Case 15: User Not Found
**Scenario:** User tries to login with non-existent phone
**Input:**
```json
{
  "phone_or_email": "+19999999999",
  "password": "TestSecure123!"
}
```
**Expected:** 400 Bad Request - Phone/Email or password is incorrect

---

### Test Case 16: Get Profile Authenticated
**Scenario:** Logged-in user accesses profile endpoint
**Headers:** Authorization: Bearer {access_token}
**Expected:** 200 OK - Return user profile data

---

### Test Case 17: Get Profile Unauthenticated
**Scenario:** User accesses profile without token
**Expected:** 401 Unauthorized - Authentication credentials were not provided

---

### Test Case 18: Update Profile Success
**Scenario:** User updates profile information
**Input:**
```json
{
  "full_name": "Updated Name",
  "email": "newemail@example.com"
}
```
**Expected:** 200 OK - Profile updated, returns updated user data

---

### Test Case 19: Update Profile Email Duplicate
**Scenario:** User tries to update email to already used email
**Expected:** 400 Bad Request - Email already in use

---

### Test Case 20: Change Password Success
**Scenario:** User changes password with correct old password
**Input:**
```json
{
  "old_password": "TestSecure123!",
  "new_password": "NewSecure123!",
  "new_password_confirm": "NewSecure123!"
}
```
**Expected:** 200 OK - Password changed successfully

---

### Test Case 21: Change Password Wrong Old Password
**Scenario:** User enters incorrect old password
**Input:**
```json
{
  "old_password": "WrongOldPass123!",
  "new_password": "NewSecure123!",
  "new_password_confirm": "NewSecure123!"
}
```
**Expected:** 400 Bad Request - Old password is incorrect

---

### Test Case 22: Change Password Weak New Password
**Scenario:** New password doesn't meet strength requirements
**Expected:** 400 Bad Request - Password must contain special character

---

### Test Case 23: Forgot Password Success
**Scenario:** User requests password reset OTP
**Input:**
```json
{
  "phone_or_email": "+15551234567"
}
```
**Expected:** 200 OK - OTP sent message
**OTP:** Check console for code

---

### Test Case 24: Reset Password Success
**Scenario:** User resets password with correct OTP
**Input:**
```json
{
  "phone_or_email": "+15551234567",
  "otp_code": "654321",
  "new_password": "ResetPass123!",
  "new_password_confirm": "ResetPass123!"
}
```
**Expected:** 200 OK - Password reset successfully

---

### Test Case 25: Reset Password Invalid OTP
**Scenario:** User provides wrong OTP for password reset
**Expected:** 400 Bad Request - Invalid OTP

---

### Test Case 26: Refresh Token Success
**Scenario:** Access token expired, use refresh token
**Input:**
```json
{
  "refresh": "{refresh_token}"
}
```
**Expected:** 200 OK - New access token returned

---

### Test Case 27: Logout Success
**Scenario:** Authenticated user logs out
**Expected:** 200 OK - Logged out successfully message

---

### Test Case 28: Login History
**Scenario:** User views login history
**Expected:** 200 OK - Returns list of recent logins with IP and user agent

---

### Test Case 29: Disabled User Login
**Scenario:** Admin disables user, user tries to login
**Expected:** 400 Bad Request - User account is disabled

---

### Test Case 30: OTP Security - SQL Injection Prevention
**Scenario:** Attacker tries SQL injection in OTP field
**Input:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "otp_code": "' OR '1'='1"
}
```
**Expected:** 400 Bad Request - OTP must contain only digits

---

## Performance Test Cases

### Test Case 31: Concurrent Registration
**Scenario:** Multiple users register simultaneously
**Expected:** All registrations processed without data integrity issues

---

### Test Case 32: Bulk Login Attempts
**Scenario:** Same user makes 10 concurrent login requests
**Expected:** All authenticated successfully, separate sessions created

---

### Test Case 33: Token Expiry Behavior
**Scenario:** Token used 61 minutes after generation
**Expected:** 401 Unauthorized - Given token not valid for any token type

---

## Security Test Cases

### Test Case 34: Password Hash Verification
**Scenario:** Check user password never stored in plain text
**Expected:** All stored passwords are hashed

---

### Test Case 35: Rate Limiting (Future Enhancement)
**Scenario:** Make 100 requests to login endpoint in 1 minute
**Expected:** Should implement rate limiting to prevent brute force

---

### Test Case 36: HTTPS Requirement (Production)
**Scenario:** Access API via HTTP in production
**Expected:** Should enforce HTTPS redirect

---

## Test Execution Report Template

```
Test Suite: Smart SMS Authentication
Date: 2024-01-15
Environment: Development
Python Version: 3.9+
Django Version: 4.2.11

Total Tests: 36
Passed: __
Failed: __
Skipped: __

Priority Bugs: __
Critical Issues: __

Notes:
- 
- 
```

## Battery Test - All Endpoints

1. ✅ Register
2. ✅ Verify OTP
3. ✅ Login
4. ✅ Get Profile
5. ✅ Update Profile
6. ✅ Change Password
7. ✅ Logout
8. ✅ Forgot Password
9. ✅ Reset Password
10. ✅ Refresh Token
11. ✅ Login History

---

**Use these test cases to validate the entire authentication module!**
