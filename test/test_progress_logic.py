"""
Phase 2 — Unit Tests: Progress Update Logic

Tests update_user_progress() from progress.py — the function that tracks
how many chat sessions a user has had on each topic.
These tests use the `session` fixture (in-memory SQLite) since the function
operates directly on the database via SQLAlchemy.
"""

import models
import progress


# ---------------------------------------------------------------------------
# Progress creation & increment
# ---------------------------------------------------------------------------

def test_create_new_progress(session):
    """First call for a topic creates a new Progress row with chat_count=1."""
    # Create a user directly in the DB (bypass API, this is a unit test)
    user = models.User(
        name="ProgressUser",
        email="progress@test.com",
        password_hash="fakehash",
        skill="Python"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    result = progress.update_user_progress(session, user.id, "Recursion")

    assert result is not None
    assert result.topic == "Recursion"
    assert result.chat_count == 1
    assert result.user_id == user.id


def test_increment_existing_progress(session):
    """Second call for the same topic increments chat_count to 2."""
    user = models.User(
        name="ProgressUser",
        email="progress@test.com",
        password_hash="fakehash",
        skill="Python"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    progress.update_user_progress(session, user.id, "Sorting")
    result = progress.update_user_progress(session, user.id, "Sorting")

    assert result.chat_count == 2


def test_topic_normalization(session):
    """'python' and '  Python  ' should map to the same 'Python' record."""
    user = models.User(
        name="ProgressUser",
        email="progress@test.com",
        password_hash="fakehash",
        skill="Python"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    progress.update_user_progress(session, user.id, "python")
    progress.update_user_progress(session, user.id, "  Python  ")

    # Should be a single row, not two separate ones
    rows = session.query(models.Progress).filter(
        models.Progress.user_id == user.id
    ).all()
    assert len(rows) == 1
    assert rows[0].topic == "Python"
    assert rows[0].chat_count == 2


def test_empty_topic_returns_none(session):
    """Empty string topic returns None without creating a row."""
    user = models.User(
        name="ProgressUser",
        email="progress@test.com",
        password_hash="fakehash",
        skill="Python"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    result = progress.update_user_progress(session, user.id, "")

    assert result is None
    # No progress rows should exist
    count = session.query(models.Progress).filter(
        models.Progress.user_id == user.id
    ).count()
    assert count == 0


def test_different_topics_create_separate_rows(session):
    """Two different topics create two separate Progress rows."""
    user = models.User(
        name="ProgressUser",
        email="progress@test.com",
        password_hash="fakehash",
        skill="Python"
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    progress.update_user_progress(session, user.id, "Sorting")
    progress.update_user_progress(session, user.id, "Recursion")

    rows = session.query(models.Progress).filter(
        models.Progress.user_id == user.id
    ).all()
    assert len(rows) == 2
    topics = {row.topic for row in rows}
    assert topics == {"Sorting", "Recursion"}
