from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmergencySOSViewSet

router = DefaultRouter()
router.register(r'sos', EmergencySOSViewSet, basename='sos')

urlpatterns = [
    path('trigger/', EmergencySOSViewSet.as_view({'post': 'trigger'}), name='emergency-trigger'),
    path('', include(router.urls)),
]
