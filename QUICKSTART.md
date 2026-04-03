# Quick Start Guide

Get the Smart SMS Authentication module running in 5 minutes!

## Prerequisites
- Python 3.9+
- pip
- PostgreSQL (or use SQLite for quick testing)

## Quick Setup (Using SQLite)

### 1. Navigate to project directory
```bash
cd smartsms
```


### 2. Create & activate virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create superuser
```bash
python manage.py createsuperuser
# Phone: +1234567890
# Email: admin@example.com
# Full Name: Admin User
# Password: YourPassword123!
```

### 6. Start development server
```bash
python manage.py runserver
```

### 7. Test the API
```bash
# In another terminal, curl or use Postman

curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+9876543210",
    "email": "testuser@example.com",
    "full_name": "Test User",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!"
  }'
```

## Quick Setup (Using PostgreSQL)

### 1-3. Same as above...

### 4. Create PostgreSQL Database
```sql
CREATE DATABASE smartsms_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE smartsms_db TO postgres;
```

### 5. Update settings.py
```python
# In smartsms/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smartsms_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 6-7. Continue with migration & server...

## Test Complete Flow

### 1. Register User
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
**Copy the `user_id` and look for **OTP in console**

### 2. Verify OTP
```bash
curl -X POST http://localhost:8000/api/verify_otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "YOUR_USER_ID_HERE",
    "otp_code": "YOUR_OTP_CODE_HERE"
  }'
```

### 3. Login
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_or_email": "+1234567890",
    "password": "SecurePass123!"
  }'
```
**Copy the `access` token**

### 4. Access Protected Route
```bash
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Admin Panel
- URL: http://localhost:8000/admin/
- Phone: +1234567890
- Password: (the password you set for superuser)

## Useful Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations

# Access Django shell
python manage.py shell

# Create new superuser
python manage.py createsuperuser

# Dump data to JSON
python manage.py dumpdata > data.json

# Load data from JSON
python manage.py loaddata data.json
```

## Environment Variables (Optional)

Create `.env` file in project root:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_NAME=smartsms_db
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
```

Then update `settings.py` to use `.env` values.

## Need Help?

- Check README.md for detailed API documentation
- See API_EXAMPLES.txt for more curl examples
- Check console output for OTP codes during testing

---

**Happy Coding! 🚀**
