from django.apps import AppConfig


class Module1AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.module_1_auth'
    verbose_name = 'Module 1: Authentication & User Management'
    
    def ready(self):
        """Import signals when app is ready."""
        from . import signals
