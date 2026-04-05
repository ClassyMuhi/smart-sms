# Model Structure Documentation

## Custom User Model (CustomUser)

The application uses a custom user model that extends Django's AbstractUser with phone-based authentication.

### Fields:
- **id** (UUID): Primary key, auto-generated unique identifier
- **phone** (CharField, unique): User's phone number (username field)
  - Validation: +1234567890 or 1234567890 format
  - Length: 9-15 digits
  - Indexed for fast lookups

- **email** (EmailField, unique): User's email address
  - Optional but recommended for password recovery

- **full_name** (CharField): User's full name
  - Max length: 255 characters

- **password** (CharField): Hashed password (never plain text)
  - Hashed using PBKDF2 (Django default)
  - Min length: 8 characters
  - Requirements: uppercase, lowercase, digit, special char

- **is_phone_verified** (BooleanField): Phone verification status
  - Default: False
  - Set to True after OTP verification

- **is_active** (BooleanField): Account active status
  - Default: True
  - Set to False by admin to disable account

- **is_staff** (BooleanField): Admin access flag
  - Default: False

- **is_superuser** (BooleanField): Superuser flag
  - Default: False

- **created_at** (DateTimeField): Account creation timestamp
  - Auto-set on creation
  - Indexed

- **updated_at** (DateTimeField): Account last update timestamp
  - Auto-updated

- **last_login_at** (DateTimeField): Last successful login timestamp
  - Null initially
  - Updated on every login

### Indexes:
```python
['phone']           # Quick phone lookup for login
['email']           # Quick email lookup
['-created_at']     # Recent users first
```

### Methods:
```python
get_full_name()          # Returns full name
get_short_name()         # Returns first name
check_password(pwd)      # Verify password
set_password(pwd)        # Hash and set password
```

---

## OTP Verification Model (OTPVerification)

Stores One-Time Password records for phone/email verification and password reset.

### Fields:
- **id** (UUID): Primary key
- **user** (ForeignKey): Reference to CustomUser (OneToOne)
  - On delete: CASCADE
  - Can query: user.otp_verification

- **otp_code** (CharField): The 6-digit OTP
  - Max length: 6
  - Indexed for lookup

- **purpose** (CharField): OTP usage purpose
  - Choices:
    - 'registration': Phone verification on signup
    - 'phone_verification': Verify phone later
    - 'password_reset': Password reset OTP
    - 'login': OTP-based login (future)
  - Default: 'registration'

- **is_verified** (BooleanField): Verification status
  - Default: False
  - Set True after correct OTP entry

- **verified_at** (DateTimeField): When OTP was verified
  - Null initially
  - Timestamp of verification

- **created_at** (DateTimeField): OTP generation time
  - Auto-set on creation

- **expires_at** (DateTimeField): OTP expiration time
  - Calculated as created_at + 5 minutes
  - Checked before OTP verification

- **attempts** (IntegerField): Failed verification attempts
  - Default: 0
  - Incremented on wrong OTP

- **max_attempts** (IntegerField): Maximum allowed attempts
  - Default: 5
  - Prevents brute force

### Indexes:
```python
['user', '-created_at']     # Find recent OTP for user
['otp_code']                # Direct OTP lookup
```

### Methods:
```python
is_expired()                    # Check if OTP is expired
is_valid_for_verification()    # Check if valid & attempts OK
```

---

## User Login History Model (UserLoginHistory)

Tracks and audits user login activities for security monitoring.

### Fields:
- **id** (UUID): Primary key
- **user** (ForeignKey): Reference to CustomUser
  - On delete: CASCADE
  - Can query: user.login_history

- **ip_address** (GenericIPAddressField): IPv4 or IPv6 address
  - Extracted from request
  - Can be null for local testing

- **user_agent** (CharField): Browser/client information
  - Max length: 500
  - Useful for device tracking

- **login_at** (DateTimeField): Login timestamp
  - Auto-set on creation
  - Default: timezone.now()

### Indexes:
```python
['user', '-login_at']    # Recent logins for user
```

### Usage:
- View past 10 logins: `/api/login-history/`
- Detect suspicious activity
- Security audit trail

---

## Relationships Diagram

```
CustomUser (1)
    ├── has (1) OTPVerification
    └── has (many) UserLoginHistory

OTPVerification (many) ← belongs to → (1) CustomUser

UserLoginHistory (many) ← belongs to → (1) CustomUser
```

---

## Database Schema SQL (Reference)

```sql
-- CustomUser Table
CREATE TABLE auth_module_customuser (
    id UUID PRIMARY KEY,
    phone VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE,
    full_name VARCHAR(255),
    password VARCHAR(128) NOT NULL,
    is_phone_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    last_login_at TIMESTAMP,
    CONSTRAINT phone_format CHECK (phone ~ '^\+?1?\d{9,15}$')
);

CREATE INDEX idx_customuser_phone ON auth_module_customuser(phone);
CREATE INDEX idx_customuser_email ON auth_module_customuser(email);
CREATE INDEX idx_customuser_created ON auth_module_customuser(created_at DESC);

-- OTPVerification Table
CREATE TABLE auth_module_otpverification (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE,
    otp_code VARCHAR(6) NOT NULL,
    purpose VARCHAR(20) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 5,
    FOREIGN KEY (user_id) REFERENCES auth_module_customuser(id) ON DELETE CASCADE
);

CREATE INDEX idx_otpverification_code ON auth_module_otpverification(otp_code);
CREATE INDEX idx_otpverification_user_created ON auth_module_otpverification(user_id, created_at DESC);

-- UserLoginHistory Table
CREATE TABLE auth_module_userloginhistory (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    ip_address INET,
    user_agent VARCHAR(500),
    login_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_module_customuser(id) ON DELETE CASCADE
);

CREATE INDEX idx_loginhistory_user_login ON auth_module_userloginhistory(user_id, login_at DESC);
```

---

## Migration Management

### Create Migrations:
```bash
python manage.py makemigrations auth_module
```

### Apply Migrations:
```bash
python manage.py migrate auth_module
```

### Check Migration Status:
```bash
python manage.py showmigrations auth_module
```

### Rollback Migration:
```bash
python manage.py migrate auth_module <migration_name> --plan  # Check first
python manage.py migrate auth_module 0001  # Migrate back to specific version
```

---

## Data Integrity

### Constraints:
1. **Phone uniqueness**: Only one user per phone number
2. **Email uniqueness**: Only one user per email
3. **One OTP per user**: OneToOne relationship ensures latest OTP only
4. **OTP expiry**: Automatic validation before verification
5. **Password hashing**: Never store plain text passwords

### Cascade Delete:
- Deleting user → Deletes its OTP record
- Deleting user → Deletes its login history

### Foreign Key Integrity:
- OTP cannot exist without user
- Login history cannot exist without user

---

**Model documentation complete! Use this as reference for database understanding.**
