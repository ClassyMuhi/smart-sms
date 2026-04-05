#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsms.settings')
django.setup()

from auth_module.models import CustomUser

# Check if admin already exists
if CustomUser.objects.filter(phone='+1234567890').exists():
    print("✅ Admin user already exists!")
    user = CustomUser.objects.get(phone='+1234567890')
    print(f"   Phone: {user.phone}")
    print(f"   Email: {user.email}")
    print(f"   Name: {user.full_name}")
else:
    # Create new admin user
    user = CustomUser(
        phone='+1234567890',
        email='admin@example.com',
        full_name='Admin User',
        is_staff=True,
        is_superuser=True,
        is_active=True,
        is_phone_verified=True
    )
    user.set_password('Admin123!')
    user.save()
    
    print("✅ Superuser created successfully!")
    print(f"   Phone: {user.phone}")
    print(f"   Email: {user.email}")
    print(f"   Name: {user.full_name}")
    print(f"   Password: Admin123!")

print("\n🌐 Admin Panel: http://localhost:8000/admin/")
print("📱 Phone: +1234567890")
print("🔑 Password: Admin123!")
