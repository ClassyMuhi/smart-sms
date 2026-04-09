import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsms.settings')
django.setup()

from apps.module_1_auth.models import CustomUser, OTPVerification
from django.utils import timezone
from django.contrib.auth.hashers import make_password
import requests
import json

# Create a verified test user directly
print("=" * 70)
print("CREATING VERIFIED TEST USER")
print("=" * 70)

phone = "9988776655"
email = "verified@example.com"
password = "TestPass123!"

# Delete if exists
CustomUser.objects.filter(phone=phone).delete()

# Create user
user = CustomUser.objects.create(
    phone=phone,
    email=email,
    full_name="Verified User",
    password=make_password(password),
    is_phone_verified=True
)

print(f"✅ User created: {user.phone}")
print(f"   Email: {user.email}")
print(f"   Phone Verified: {user.is_phone_verified}")

# Now test Login
print("\n" + "=" * 70)
print("TEST: LOGIN WITH VERIFIED USER")
print("=" * 70)

BASE_URL = "http://127.0.0.1:8000/api"

login_data = {
    "phone_or_email": phone,
    "password": password
}

response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print("✅ Login successful!")
    print(f"User: {data['user']['phone']}")
    token = data.get('access')
    print(f"Access Token: {token[:40]}...")
    
    # Test Create Contact
    print("\n" + "=" * 70)
    print("TEST: CREATE CONTACT")
    print("=" * 70)
    
    contact_data = {
        "name": "Bob Smith",
        "phone": "+91 99999 88888",
        "email": "bob@example.com"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/contacts/contacts/", json=contact_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        contact = response.json()
        print("✅ Contact created!")
        print(f"   Name: {contact['name']}")
        print(f"   Phone: {contact['phone_display']}")
        print(f"   Contact ID: {contact['id']}")
        
        # Test List Contacts
        print("\n" + "=" * 70)
        print("TEST: LIST CONTACTS")
        print("=" * 70)
        
        response = requests.get(f"{BASE_URL}/contacts/contacts/", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved contacts!")
            print(f"   Total: {data['count']}")
            for contact in data['results']:
                print(f"   - {contact['name']} ({contact['phone_display']})")
    else:
        print(f"❌ Failed: {response.json()}")
else:
    print(f"❌ Login failed: {response.json()}")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETED ✅")
print("=" * 70)
