"""
URL configuration for smartsms project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_module.urls')),
    path('api/', include('contact_management.urls')),
]
