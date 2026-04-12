from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Contact, EmergencyContact, normalize_phone
from .serializers import (
    ContactSerializer,
    EmergencyContactSerializer,
    ContactSearchSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """
    Pagination class for contact listings.
    
    - page_size: 10 contacts per page
    - page_size_query_param: allow ?page_size=20 in URL
    - max_page_size: prevent huge requests
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ContactViewSet(viewsets.ModelViewSet):
    """
    Contact Management API ViewSet.
    
    Endpoints:
    - GET /api/contacts/ - List all contacts (paginated)
    - POST /api/contacts/ - Create new contact
    - GET /api/contacts/{id}/ - Get specific contact
    - PUT /api/contacts/{id}/ - Update contact (full update)
    - PATCH /api/contacts/{id}/ - Partial update
    - DELETE /api/contacts/{id}/ - Delete contact (safe if emergency)
    - GET /api/contacts/search/?name=john - Search by name
    - GET /api/contacts/search/?phone=9876 - Search by phone
    
    Permissions:
    - Only authenticated users
    - Users can only access their own contacts (user_id filter)
    """
    
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    # Enable search and filtering
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone']  # Search on these fields
    ordering_fields = ['created_at', 'name']  # Allow sorting
    ordering = ['-created_at']  # Default: newest first
    
    def get_queryset(self):
        """
        Return only contacts belonging to the current user.
        
        This ensures user-specific data isolation - users can't see
        other users' contacts.
        """
        return Contact.objects.filter(
            user=self.request.user
        ).select_related('user')  # Optimize: avoid extra queries
    
    def perform_create(self, serializer):
        """
        Create a new contact and assign to current user.
        
        This is called by create() action. Ensures user is always the
        authenticated request user (security best practice).
        """
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new contact.
        
        POST /api/contacts/
        {
            "name": "John Doe",
            "phone": "+91 98765 43210",
            "email": "john@example.com"
        }
        
        Returns 201 Created with contact details.
        User is automatically set from authenticated request.
        """
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Update contact (full update - all fields required).
        
        PUT /api/contacts/{id}/
        """
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update contact (only send fields to update).
        
        PATCH /api/contacts/{id}/
        {
            "name": "New Name"
        }
        """
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a contact.
        
        Safe deletion: Automatically removes from emergency contacts too.
        CASCADE delete handles this.
        
        DELETE /api/contacts/{id}/
        
        Returns 204 No Content on success.
        """
        contact = self.get_object()
        
        # Check if this contact is used as emergency contact
        emergency_count = contact.as_emergency_for.count()
        if emergency_count > 0:
            return Response(
                {
                    'detail': f'This contact is marked as emergency contact. '
                              f'Remove from emergency contacts first.',
                    'emergency_contact_count': emergency_count
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search contacts by name or phone.
        
        GET /api/contacts/search/?name=john
        GET /api/contacts/search/?phone=9876
        GET /api/contacts/search/?name=john&phone=98
        
        Supports partial matches (case-insensitive).
        """
        serializer = ContactSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        queryset = self.get_queryset()
        search_name = serializer.validated_data.get('name', '')
        search_phone = serializer.validated_data.get('phone', '')
        
        # Build query
        if search_name:
            queryset = queryset.filter(
                name__icontains=search_name  # Case-insensitive substring match
            )
        
        if search_phone:
            queryset = queryset.filter(
                phone__icontains=search_phone  # Phone number partial match
            )
        
        if not search_name and not search_phone:
            return Response(
                {'detail': 'Provide either name or phone parameter.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recently used contacts (sorted by creation).
        
        GET /api/contacts/recent/?limit=5
        
        Returns contacts sorted by most recent first.
        """
        limit = request.query_params.get('limit', 5)
        try:
            limit = int(limit)
            limit = min(limit, 50)  # Max 50 to prevent abuse
        except ValueError:
            limit = 5
        
        queryset = self.get_queryset()[:limit]
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'count': len(queryset),
            'results': serializer.data
        })


class EmergencyContactViewSet(viewsets.ModelViewSet):
    """
    Emergency Contacts API ViewSet.
    
    Endpoints:
    - GET /api/emergency-contacts/ - List emergency contacts
    - POST /api/emergency-contacts/ - Mark contact as emergency
    - DELETE /api/emergency-contacts/{id}/ - Remove from emergency
    
    Features:
    - Only show emergency contacts for the requesting user
    - Prevent adding contacts that don't belong to user
    - Cascade delete: Removing contact removes emergency association
    """
    
    serializer_class = EmergencyContactSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Return only emergency contacts for the current user."""
        return EmergencyContact.objects.filter(
            user=self.request.user
        ).select_related('contact', 'user')
    
    def perform_create(self, serializer):
        """
        Create emergency contact association.
        
        Ensures user is always the authenticated request user.
        """
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Mark a contact as emergency contact.
        
        POST /api/emergency-contacts/
        {
            "contact": "contact-uuid-here",
            "relationship": "Mother"
        }
        
        Returns 201 Created with emergency contact details.
        User is automatically set from authenticated request.
        """
        return super().create(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Remove a contact from emergency contacts.
        
        DELETE /api/emergency-contacts/{id}/
        
        Note: This only removes emergency status, doesn't delete the contact.
        """
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def quick_access(self, request):
        """
        Get emergency contacts with quick summary.
        
        GET /api/emergency-contacts/quick_access/
        
        Returns minimal info for quick dialing.
        """
        emergency = self.get_queryset()
        
        data = [
            {
                'id': e.id,
                'name': e.contact.name,
                'phone': e.contact.phone,
                'relationship': e.relationship or 'Emergency Contact'
            }
            for e in emergency
        ]
        
        return Response({
            'count': len(data),
            'emergency_contacts': data,
            'message': 'Quick access list for emergency calls'
        })
    
    @action(detail=False, methods=['post'])
    def add_by_phone(self, request):
        """
        Mark a contact as emergency by phone number.
        
        POST /api/emergency-contacts/add_by_phone/
        {
            "phone": "9876543210",
            "relationship": "Doctor"
        }
        
        Easier than finding contact UUID first.
        """
        phone = request.data.get('phone')
        relationship = request.data.get('relationship', '')
        
        if not phone:
            return Response(
                {'detail': 'Phone number is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        normalized_phone = normalize_phone(phone)

        try:
            contact = Contact.objects.get(
                user=request.user,
                phone=normalized_phone
            )
        except Contact.DoesNotExist:
            return Response(
                {'detail': f'Contact with phone {phone} not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already emergency
        if EmergencyContact.objects.filter(
            user=request.user,
            contact=contact
        ).exists():
            return Response(
                {'detail': 'Already marked as emergency contact.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create emergency contact
        emergency = EmergencyContact.objects.create(
            user=request.user,
            contact=contact,
            relationship=relationship
        )
        
        serializer = self.get_serializer(emergency)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
