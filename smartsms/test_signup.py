import json
import urllib.request
import urllib.error

# Test signup with new phone number
import time
payload = {
    "phone": f"9{int(time.time() % 1000000000):09d}",
    "email": f"test{int(time.time())}@example.com",
    "full_name": "Test User",
    "password": "Test@12345",
    "password_confirm": "Test@12345"
}

try:
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/auth/register/',
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode('utf-8'))
    print("✅ SUCCESS (201):")
    print(json.dumps(result, indent=2))
except urllib.error.HTTPError as e:
    error_data = json.loads(e.read().decode('utf-8'))
    print(f"❌ ERROR ({e.code}):")
    print(json.dumps(error_data, indent=2))
except Exception as e:
    print(f"❌ ERROR: {e}")
