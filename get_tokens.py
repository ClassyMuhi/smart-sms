import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsms.settings')
django.setup()

from auth_module.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
import json

alice = CustomUser.objects.filter(phone='+1111111111').first()
bob = CustomUser.objects.filter(phone='+2222222222').first()

if not alice or not bob:
    print("Run `test_messaging.py` first to create the users!")
    exit()

def get_token(u):
    return str(RefreshToken.for_user(u).access_token)

print("\n--- TEST CREDENTIALS FOR FRONTEND ---")
print(f"\n[ALICE]")
print(f"USER ID: {alice.id}")
print(f"TOKEN:   {get_token(alice)}")

print(f"\n[BOB]")
print(f"USER ID: {bob.id}")
print(f"TOKEN:   {get_token(bob)}\n")
