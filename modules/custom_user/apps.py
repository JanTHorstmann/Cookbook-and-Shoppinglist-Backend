from django.apps import AppConfig


class CustomUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.custom_user'
    label = 'custom_user'
