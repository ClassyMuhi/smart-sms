"""
URL configuration for smartsms project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Module 1: Authentication & User Management
    path('api/auth/', include('apps.module_1_auth.urls')),
    
    # Module 2: Messaging (SMS Core)
    path('api/messaging/', include('apps.module_2_messaging.urls')),
    
    # Module 3: Contact Management
    path('api/contacts/', include('apps.module_3_contacts.urls')),
]
