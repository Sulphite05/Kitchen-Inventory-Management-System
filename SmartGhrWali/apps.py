from django.apps import AppConfig


class SmartghrwaliConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "SmartGhrWali"

    def ready(self):
        from . import signals