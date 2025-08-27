from django.apps import AppConfig
from .signals import setup_api_logger_signal


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common"

    def ready(self):
        setup_api_logger_signal()
