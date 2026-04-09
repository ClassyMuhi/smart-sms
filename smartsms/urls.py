"""
URL configuration for smartsms project.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def root_status(request):
    return JsonResponse({"message": "Smart SMS API is running"})

urlpatterns = [
    path('', root_status),
    path('admin/', admin.site.urls),
    path('api/', include('apps.module_1_auth.urls')),
]
