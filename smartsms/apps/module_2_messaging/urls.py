from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SMSMessageViewSet, MessageTemplateViewSet

router = DefaultRouter()
router.register(r'messages', SMSMessageViewSet)
router.register(r'templates', MessageTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
