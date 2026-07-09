"""
Smoke test to verify the test infrastructure (Phase 1 fixtures) works.

Run with: pytest test/test_smoke.py -v
"""


def test_session_fixture_creates_tables(session):
    """Verify the session fixture creates a working database."""
    from sqlalchemy import inspect
    inspector = inspect(session.bind)
    tables = inspector.get_table_names()
    # All 5 model tables should exist
    assert "users" in tables
    assert "chats" in tables
    assert "courses" in tables
    assert "saved_courses" in tables
    assert "progress" in tables


def test_client_fixture_returns_testclient(client):
    """Verify the client fixture provides a working TestClient."""
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "PrepBuddy Backend Running"}


def test_test_user_fixture_creates_user(test_user):
    """Verify the test_user fixture creates a user and returns correct data."""
    assert test_user["email"] == "testuser@example.com"
    assert test_user["name"] == "Test User"
    assert test_user["skill"] == "Python"
    # Raw password should be attached for login tests
    assert test_user["password"] == "password123"
    # Should have an auto-generated id
    assert "id" in test_user


def test_test_user2_fixture_creates_second_user(test_user, test_user2):
    """Verify test_user2 is a different user from test_user."""
    assert test_user2["email"] == "seconduser@example.com"
    assert test_user2["id"] != test_user["id"]


def test_token_fixture_returns_string(token):
    """Verify the token fixture returns a JWT string."""
    assert isinstance(token, str)
    # JWT format: header.payload.signature (3 dot-separated parts)
    assert len(token.split(".")) == 3


def test_authorized_client_has_auth_header(authorized_client):
    """Verify the authorized_client has the Authorization header set."""
    assert "Authorization" in authorized_client.headers
    assert authorized_client.headers["Authorization"].startswith("Bearer ")


def test_authorized_client_can_access_protected_route(authorized_client):
    """Verify the authorized_client can hit /me without 401."""
    res = authorized_client.get("/me")
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "testuser@example.com"


def test_unauthenticated_client_gets_401(client):
    """Verify the plain client gets 401 on protected routes."""
    res = client.get("/me")
    assert res.status_code == 401
