from dj_rest_auth.registration.serializers import (
    RegisterSerializer as BaseRegisterSerializer,
)
from allauth.account import app_settings as allauth_account_settings
from rest_framework import serializers


class RegisterSerializer(BaseRegisterSerializer):
    username = serializers.CharField(
        max_length=allauth_account_settings.USERNAME_MAX_LENGTH
        if hasattr(allauth_account_settings, "USERNAME_MAX_LENGTH")
        else 150,
        min_length=allauth_account_settings.USERNAME_MIN_LENGTH,
        required=allauth_account_settings.SIGNUP_FIELDS.get("username", {}).get(
            "required", True
        ),
    )
    email = serializers.EmailField(
        required=allauth_account_settings.SIGNUP_FIELDS.get("email", {}).get(
            "required", False
        )
    )
