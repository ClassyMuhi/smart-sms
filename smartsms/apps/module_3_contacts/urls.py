from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactViewSet, EmergencyContactViewSet

# Router for automatic URL generation from ViewSet actions
router = DefaultRouter()

# Register ContactViewSet
# Provides URLs like:
# /api/contacts/ - list/create
# /api/contacts/{id}/ - retrieve/update/delete
# /api/contacts/search/ - custom search action
# /api/contacts/recent/ - custom recent action
router.register(r'contacts', ContactViewSet, basename='contact')

# Register EmergencyContactViewSet
# Provides URLs like:
# /api/emergency-contacts/ - list/create
# /api/emergency-contacts/{id}/ - retrieve/delete
# /api/emergency-contacts/quick_access/ - custom action
# /api/emergency-contacts/add_by_phone/ - custom action
router.register(r'emergency-contacts', EmergencyContactViewSet, basename='emergency-contact')

urlpatterns = [
    path('', include(router.urls)),
]

"""
Full Contact Management API Endpoints:

CONTACTS:
=========
GET     /api/contacts/                    - List all contacts (paginated)
POST    /api/contacts/                    - Create new contact
GET     /api/contacts/{id}/               - Get specific contact
PUT     /api/contacts/{id}/               - Full update contact
PATCH   /api/contacts/{id}/               - Partial update contact
DELETE  /api/contacts/{id}/               - Delete contact

Search & Features:
GET     /api/contacts/search/?name=john   - Search by name (partial)
GET     /api/contacts/search/?phone=98    - Search by phone (partial)
GET     /api/contacts/recent/?limit=5     - Get 5 most recent

EMERGENCY CONTACTS:
===================
GET     /api/emergency-contacts/          - List emergency contacts
POST    /api/emergency-contacts/          - Mark contact as emergency
DELETE  /api/emergency-contacts/{id}/     - Remove from emergency

Special Actions:
GET     /api/emergency-contacts/quick_access/              - Quick dial list
POST    /api/emergency-contacts/add_by_phone/              - Add by phone

Query Parameters:
==================
?page=2                  - Pagination
?page_size=20           - Items per page
?search=john            - Global search
?ordering=-created_at   - Sort order
?name=john&phone=98     - Combined filters
"""
