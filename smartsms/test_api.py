import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def test_register():
    """Test user registration"""
    print("\n" + "=" * 70)
    print("TEST 1: REGISTER USER")
    print("=" * 70)
    
    register_data = {
        "phone": "9876543456",
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return data.get('user_id')
        else:
            print(f"❌ Registration failed: {data.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_login():
    """Test user login"""
    print("\n" + "=" * 70)
    print("TEST 2: LOGIN USER")
    print("=" * 70)
    
    login_data = {
        "phone_or_email": "9876543456",
        "password": "TestPass123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Login successful!")
            print(f"User: {data['user']['phone']}")
            token = data.get('access')
            print(f"Access Token: {token[:30]}...")
            return token
        else:
            print(f"❌ Login failed: {data}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_create_contact(token):
    """Test creating a contact"""
    print("\n" + "=" * 70)
    print("TEST 3: CREATE CONTACT")
    print("=" * 70)
    
    if not token:
        print("❌ No token provided")
        return None
    
    contact_data = {
        "name": "Alice Johnson",
        "phone": "+91 98765 43210",
        "email": "alice@example.com"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/contacts/", json=contact_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        
        if response.status_code == 201:
            print("✅ Contact created successfully!")
            print(f"Contact: {json.dumps(data, indent=2)}")
            return data.get('id')
        else:
            print(f"❌ Creation failed: {data}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_list_contacts(token):
    """Test listing contacts"""
    print("\n" + "=" * 70)
    print("TEST 4: LIST CONTACTS")
    print("=" * 70)
    
    if not token:
        print("❌ No token provided")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/contacts/", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    try:
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Contacts retrieved successfully!")
            print(f"Total Contacts: {data.get('count', 0)}")
            if data.get('results'):
                print("\nContacts:")
                for contact in data['results']:
                    print(f"  - {contact['name']} ({contact['phone_display']})")
            else:
                print("  No contacts found")
        else:
            print(f"❌ Failed to retrieve: {data}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    print("\n" + "🚀" * 35)
    print("SMART SMS API - COMPREHENSIVE TEST")
    print("🚀" * 35)
    
    # Test registration
    user_id = test_register()
    
    # Test login
    token = test_login()
    
    # Test creating contact
    if token:
        contact_id = test_create_contact(token)
        
        # Test listing contacts
        test_list_contacts(token)
    
    print("\n" + "=" * 70)
    print("TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
