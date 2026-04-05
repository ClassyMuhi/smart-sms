import os
import django
import sys
import threading
import json
import time
import websocket

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsms.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken

from auth_module.models import CustomUser
from messaging.models import Message

def get_or_create_user(phone, name):
    user, created = CustomUser.objects.get_or_create(
        phone=phone,
        defaults={'email': f"{name.lower()}@example.com", 'full_name': name, 'is_phone_verified': True}
    )
    if created:
        user.set_password("SecurePass123!")
        user.save()
    return user

def generate_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

# 1. Setup Users
alice = get_or_create_user('+1111111111', 'Alice')
bob = get_or_create_user('+2222222222', 'Bob')

alice_token = generate_token(alice)
bob_token = generate_token(bob)

print(f"Alice ID: {alice.id}")
print(f"Bob ID: {bob.id}")
print("-" * 50)

# Websocket listener for Bob
def bob_socket_listen():
    def on_message(ws, message):
        data = json.loads(message)
        print(f"\n[Bob's Screen] 💬 Real-time message received from Alice!")
        print(f"[Bob's Screen] Content: '{data.get('content')}'")
        ws.close()

    ws_url = f"ws://127.0.0.1:8000/ws/chat/{bob.id}/?token={bob_token}"
    ws = websocket.WebSocketApp(ws_url, on_message=on_message)
    ws.run_forever()

print("1. Bob coming online (starting WebSocket listener)...")
t = threading.Thread(target=bob_socket_listen)
t.daemon = True
t.start()

# Give bob a second to connect
time.sleep(2)

print("\n2. Alice is sending a message to Bob via REST API...")
import requests
send_url = "http://127.0.0.1:8000/api/messages/send/"
headers = {"Authorization": f"Bearer {alice_token}"}
payload = {
    "receiver_id": str(bob.id),
    "content": "Hey Bob! This is Alice writing to you from the new Messaging Core API! 🚀",
    "conversation_id": "conv_alice_bob_1"
}

response = requests.post(send_url, json=payload, headers=headers)
print(f"Alice API Response: {response.status_code}")
if response.status_code == 201:
    print("✅ Message successfully queued in DB by Alice!")
else:
    print(f"❌ Error: See out_api.html")
    with open('out_api.html', 'w') as f:
        f.write(response.text)

# Wait to ensure Bob's websocket receives the message
time.sleep(2)
print("-" * 50)
print("Finished!")
