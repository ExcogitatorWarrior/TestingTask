from django.apps import AppConfig
from django.db.models.signals import post_migrate

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'


    def ready(self):
        from .models import Role
        def create_default_roles(sender, **kwargs):
            roles = ["Admin", "Moderator", "User", "Guest"]
            for role_name in roles:
                Role.objects.get_or_create(name=role_name)

        post_migrate.connect(create_default_roles, sender=self)