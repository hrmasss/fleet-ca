import pytest
from django.urls import reverse
from .conftest import UserFactory
from rest_framework import status


@pytest.mark.django_db
class TestAuthenticationEndpoints:
    """Test cases for authentication endpoints."""

    def test_login_success(self, api_client):
        """Test successful login with correct credentials."""
        UserFactory(username="testuser", password="testpass123")
        url = reverse("rest_login")
        data = {"username": "testuser", "password": "testpass123"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self, api_client):
        """Test login failure with wrong password."""
        UserFactory(username="testuser", password="testpass123")
        url = reverse("rest_login")
        data = {"username": "testuser", "password": "wrongpass"}
        response = api_client.post(url, data)
        # dj-rest-auth raises a ValidationError for bad credentials -> 400
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_token_refresh_success(self, api_client):
        """Test successful token refresh."""
        UserFactory(username="testuser", password="testpass123")

        # First login; cookies will carry the refresh token (httpOnly)
        login_url = reverse("rest_login")
        login_data = {"username": "testuser", "password": "testpass123"}
        api_client.post(login_url, login_data)

        # Now refresh the token using cookies (no body needed)
        refresh_url = reverse("token_refresh")
        refresh_response = api_client.post(refresh_url, {})

        assert refresh_response.status_code == status.HTTP_200_OK
        assert "access" in refresh_response.data
