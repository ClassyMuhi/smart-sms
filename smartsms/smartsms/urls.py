"""
URL configuration for smartsms project.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def api_root(request):
    """API root endpoint providing links and information."""
    return Response({
        'name': 'Smart SMS API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'auth': {
                'login': 'POST /api/auth/login/',
                'register': 'POST /api/auth/register/',
            },
            'contacts': {
                'list': 'GET /api/contacts/contacts/',
                'create': 'POST /api/contacts/contacts/',
            },
            'messaging': {
                'send': 'POST /api/messaging/messages/',
                'list': 'GET /api/messaging/messages/',
            },
           'emergency': {
                    'smart_trigger': 'POST /api/emergency/trigger/',
               'trigger_sos': 'POST /api/emergency/sos/',
               'list_sos': 'GET /api/emergency/sos/',
               'add_location': 'POST /api/emergency/sos/{id}/add_location/',
           },
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    
    # Module 1: Authentication & User Management
    path('api/auth/', include('apps.module_1_auth.urls')),
    
    # Module 2: Messaging (SMS Core)
    path('api/messaging/', include('apps.module_2_messaging.urls')),
    
    # Module 3: Contact Management
    path('api/contacts/', include('apps.module_3_contacts.urls')),

        # Module 4: Emergency & Safety System
        path('api/emergency/', include('apps.module_4_emergency.urls')),
]
