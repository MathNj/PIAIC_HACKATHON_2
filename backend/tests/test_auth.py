"""
Tests for authentication endpoints (signup, login, JWT).

Tests cover:
- User signup with validation
- User login and JWT token generation
- Password requirements
- Duplicate email prevention
- Invalid credentials handling
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.user import User


@pytest.mark.auth
class TestSignup:
    """Tests for user signup endpoint."""

    def test_signup_success(self, client: TestClient, session: Session):
        """Test successful user registration."""
        response = client.post(
            "/api/signup",
            json={
                "email": "newuser@example.com",
                "name": "New User",
                "password": "ValidPass123"
            }
        )

        assert response.status_code == 201
        data = response.json()

        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

        # Verify user was created in database
        user = session.query(User).filter(User.email == "newuser@example.com").first()
        assert user is not None
        assert user.name == "New User"

    def test_signup_duplicate_email(self, client: TestClient, test_user: User):
        """Test signup with existing email returns 400."""
        response = client.post(
            "/api/signup",
            json={
                "email": "test@example.com",  # Already exists
                "name": "Duplicate User",
                "password": "ValidPass123"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_signup_missing_uppercase(self, client: TestClient):
        """Test password validation: requires uppercase letter."""
        response = client.post(
            "/api/signup",
            json={
                "email": "testpass@example.com",
                "name": "Test User",
                "password": "lowercase123"  # No uppercase
            }
        )

        assert response.status_code == 400
        assert "uppercase" in response.json()["detail"].lower()

    def test_signup_missing_lowercase(self, client: TestClient):
        """Test password validation: requires lowercase letter."""
        response = client.post(
            "/api/signup",
            json={
                "email": "testpass@example.com",
                "name": "Test User",
                "password": "UPPERCASE123"  # No lowercase
            }
        )

        assert response.status_code == 400
        assert "lowercase" in response.json()["detail"].lower()

    def test_signup_missing_number(self, client: TestClient):
        """Test password validation: requires number."""
        response = client.post(
            "/api/signup",
            json={
                "email": "testpass@example.com",
                "name": "Test User",
                "password": "NoNumbersHere"  # No numbers
            }
        )

        assert response.status_code == 400
        assert "number" in response.json()["detail"].lower()

    def test_signup_password_too_short(self, client: TestClient):
        """Test password validation: minimum 8 characters."""
        response = client.post(
            "/api/signup",
            json={
                "email": "testpass@example.com",
                "name": "Test User",
                "password": "Short1"  # Only 6 chars
            }
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_signup_invalid_email(self, client: TestClient):
        """Test email validation."""
        response = client.post(
            "/api/signup",
            json={
                "email": "not-an-email",  # Invalid email
                "name": "Test User",
                "password": "ValidPass123"
            }
        )

        assert response.status_code == 422  # Pydantic validation error


@pytest.mark.auth
class TestLogin:
    """Tests for user login endpoint."""

    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login returns JWT token."""
        response = client.post(
            "/api/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["name"] == "Test User"
        assert "id" in data["user"]

    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email."""
        response = client.post(
            "/api/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123"
            }
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_wrong_password(self, client: TestClient, test_user: User):
        """Test login with incorrect password."""
        response = client.post(
            "/api/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword123"
            }
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing required fields."""
        response = client.post(
            "/api/login",
            json={"email": "test@example.com"}  # Missing password
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.auth
@pytest.mark.integration
class TestJWTAuthentication:
    """Tests for JWT token validation and usage."""

    def test_jwt_token_structure(self, auth_token: str):
        """Test JWT token has correct structure."""
        # JWT tokens have 3 parts separated by dots
        parts = auth_token.split(".")
        assert len(parts) == 3

    def test_protected_endpoint_with_valid_token(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test accessing protected endpoint with valid JWT."""
        response = client.get(
            f"/api/{test_user.id}/tasks",
            headers=auth_headers
        )

        # Should succeed (200 or return empty list)
        assert response.status_code == 200

    def test_protected_endpoint_without_token(self, client: TestClient, test_user: User):
        """Test accessing protected endpoint without JWT returns 403."""
        response = client.get(f"/api/{test_user.id}/tasks")

        # Should fail with 403 Forbidden (no auth header provided)
        assert response.status_code == 403

    def test_protected_endpoint_with_invalid_token(
        self, client: TestClient, test_user: User
    ):
        """Test accessing protected endpoint with invalid JWT."""
        response = client.get(
            f"/api/{test_user.id}/tasks",
            headers={"Authorization": "Bearer invalid.token.here"}
        )

        assert response.status_code == 401

    def test_user_id_mismatch_returns_403(
        self, client: TestClient, test_user: User, second_user: User, auth_headers: dict
    ):
        """Test accessing another user's resources returns 403."""
        # Try to access second user's tasks with first user's token
        response = client.get(
            f"/api/{second_user.id}/tasks",
            headers=auth_headers
        )

        assert response.status_code == 403
        assert "forbidden" in response.json()["detail"].lower()
