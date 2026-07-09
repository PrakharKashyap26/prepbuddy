"""
PrepBuddy Test Configuration — Shared Fixture Hub

All fixtures defined here are automatically available to every test file
in this directory (and subdirectories) without any imports.

Fixture chain:
    session → client → test_user → token → authorized_client
"""

import sys
import os

# ---------------------------------------------------------------------------
# Path & Environment Setup (MUST happen before any backend imports)
# ---------------------------------------------------------------------------

# Add backend/ to sys.path so bare imports like `import models` resolve
BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Force-set env vars (not setdefault) so load_dotenv() inside main.py/config.py
# cannot overwrite them with placeholder values from a .env file
os.environ["GEMINI_API_KEY"] = "test_fake_key_not_real"
os.environ["SECRET_KEY"] = "test_secret_key_for_jwt"

# ---------------------------------------------------------------------------
# Imports (now safe after path + env setup)
# ---------------------------------------------------------------------------

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
import auth


# ---------------------------------------------------------------------------
# Test Database — In-Memory SQLite (fast, isolated, no cleanup)
# ---------------------------------------------------------------------------
# StaticPool ensures ALL connections share the same in-memory database.
# Without it, each connection gets its own empty DB and tables created
# by create_all wouldn't be visible to sessions.

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def session():
    """
    Provides a fresh database session for each test.

    - Drops all tables → creates fresh tables (full isolation)
    - Yields the session for use in the test
    - Closes the session after the test finishes

    This prevents test pollution where one test's data leaks into another.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    """
    Provides a FastAPI TestClient with the database dependency overridden
    to use the test session (in-memory SQLite).

    Uses dependency_overrides to swap the real get_db with our test version.
    App is imported here (not at module level) to avoid side-effect issues
    with main.py's module-level code (table creation, static file mounts).
    """
    from main import app

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    # Clean up the override after the test
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user(client):
    """
    Creates a test user via the /register endpoint.

    Returns the user response dict with the raw password attached,
    so login tests can use it (the API only returns the hashed version).
    """
    user_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "password123",
        "skill": "Python"
    }
    res = client.post("/register", json=user_data)
    assert res.status_code == 200, f"User registration failed: {res.json()}"
    new_user = res.json()
    # Attach raw password for login tests
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture()
def test_user2(client):
    """
    Creates a second test user for ownership/authorization boundary tests.

    e.g., User1 shouldn't be able to delete User2's saved course.
    """
    user_data = {
        "name": "Second User",
        "email": "seconduser@example.com",
        "password": "password456",
        "skill": "JavaScript"
    }
    res = client.post("/register", json=user_data)
    assert res.status_code == 200, f"User2 registration failed: {res.json()}"
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture()
def token(test_user):
    """
    Generates a valid JWT access token for test_user.

    Uses the app's own create_access_token utility to ensure consistency
    with how the real app creates tokens.
    """
    return auth.create_access_token(data={"sub": test_user["email"]})


@pytest.fixture()
def authorized_client(client, token):
    """
    Provides a TestClient that is pre-authenticated with a valid JWT.

    Builds on client + token fixtures (fixture chaining/composition).
    Injects the Authorization header so every request is authenticated.
    """
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client
