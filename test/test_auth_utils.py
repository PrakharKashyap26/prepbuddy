"""
Phase 2 — Unit Tests: Auth Utility Functions

Tests pure functions in auth.py: password hashing/verification and JWT creation.
No database, no HTTP, no FastAPI — fast and deterministic.
"""

import pytest
from datetime import timedelta
from jose import jwt

import auth


# ---------------------------------------------------------------------------
# Password Hashing & Verification
# ---------------------------------------------------------------------------

def test_hash_password():
    """get_password_hash returns a bcrypt hash (starts with $2b$)."""
    hashed = auth.get_password_hash("mypassword")
    assert hashed.startswith("$2b$")


def test_verify_correct_password():
    """verify_password returns True when plain text matches its hash."""
    password = "securepass123"
    hashed = auth.get_password_hash(password)
    assert auth.verify_password(password, hashed) is True


def test_verify_wrong_password():
    """verify_password returns False for an incorrect password."""
    hashed = auth.get_password_hash("correct_password")
    assert auth.verify_password("wrong_password", hashed) is False


def test_verify_password_with_invalid_hash():
    """verify_password returns False (not crash) when given a non-bcrypt string."""
    assert auth.verify_password("anything", "not_a_valid_hash") is False


def test_hash_uniqueness():
    """Two calls with the same password produce different hashes (due to random salt)."""
    hash1 = auth.get_password_hash("samepassword")
    hash2 = auth.get_password_hash("samepassword")
    assert hash1 != hash2
    # But both should still verify against the original password
    assert auth.verify_password("samepassword", hash1) is True
    assert auth.verify_password("samepassword", hash2) is True


# ---------------------------------------------------------------------------
# JWT Token Creation
# ---------------------------------------------------------------------------

def test_create_access_token_contains_sub():
    """Decoded token payload should contain the 'sub' key we passed in."""
    token = auth.create_access_token(data={"sub": "user@example.com"})
    payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    assert payload.get("sub") == "user@example.com"


def test_create_access_token_has_expiry():
    """Token payload should contain an 'exp' field (expiration timestamp)."""
    token = auth.create_access_token(data={"sub": "user@example.com"})
    payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    assert "exp" in payload


def test_create_access_token_custom_expiry():
    """Passing a custom expires_delta should still produce a valid token."""
    short_delta = timedelta(minutes=5)
    token = auth.create_access_token(
        data={"sub": "user@example.com"},
        expires_delta=short_delta
    )
    # Should decode without error (not expired yet)
    payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    assert payload.get("sub") == "user@example.com"
    assert "exp" in payload
