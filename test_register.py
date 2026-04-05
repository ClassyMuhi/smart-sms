import requests
import json

url = "http://127.0.0.1:8000/api/register/"
data = {
    "phone": "+9876543210",
    "email": "testuser@example.com",
    "full_name": "Test User",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
