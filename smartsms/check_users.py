import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsms.settings')
django.setup()

from apps.module_1_auth.models import CustomUser

print("=" * 60)
print("USERS IN DATABASE")
print("=" * 60)

users = CustomUser.objects.all()
if not users.exists():
    print("❌ No users found!")
else:
    for u in users:
        print(f"\n📱 Phone: {u.phone}")
        print(f"📧 Email: {u.email}")
        print(f"✅ Active: {u.is_active}")
        print(f"✓ Phone Verified: {u.is_phone_verified}")
        print(f"Full Name: {u.full_name}")

print("\n" + "=" * 60)
