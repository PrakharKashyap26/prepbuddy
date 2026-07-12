"""
Phase 2 — Unit Tests: AI Socratic Fallback Logic

Tests get_socratic_fallback() from ai.py — the local responder that runs
when no valid Gemini API key is configured. Pure function, no API calls.
"""

import pytest

import ai


# ---------------------------------------------------------------------------
# Keyword-based routing tests (parametrized)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("user_input", [
    "How do I write python code?",
    "Help me with this code snippet",
    "I need a program to sort numbers",
    "What is a for loop?",
])
def test_fallback_python_keyword(user_input):
    """Inputs containing python/code/program/loop trigger the coding response."""
    response = ai.get_socratic_fallback(user_input, [])
    # Should mention control mechanisms like for/while/recursion
    assert "loop" in response.lower() or "recursion" in response.lower()


@pytest.mark.parametrize("user_input", [
    "How do I write a SQL query?",
    "Help me SELECT data from users",
    "I need to create a database schema",
    "How to join two tables?",
])
def test_fallback_sql_keyword(user_input):
    """Inputs containing sql/select/database/table trigger the DB response."""
    response = ai.get_socratic_fallback(user_input, [])
    assert "table" in response.lower() or "where" in response.lower() or "join" in response.lower()


@pytest.mark.parametrize("user_input", [
    "How does recursion work?",
    "Why is my function slow?",
])
def test_fallback_how_why(user_input):
    """Inputs with 'how' or 'why' trigger the first-principles response."""
    response = ai.get_socratic_fallback(user_input, [])
    assert "first principles" in response.lower() or "underlying cause" in response.lower()


@pytest.mark.parametrize("user_input", [
    "I keep getting an error in line 5",
    "There's a bug in my function",
    "Getting a KeyError exception",
])
def test_fallback_error_keyword(user_input):
    """Inputs with error/bug/exception trigger the debugging response."""
    response = ai.get_socratic_fallback(user_input, [])
    assert "trace" in response.lower() or "bug" in response.lower()


@pytest.mark.parametrize("user_input", [
    "hello there!",
    "hi buddy",
    "hey, I need help",
])
def test_fallback_greeting(user_input):
    """Inputs with hello/hi/hey trigger the greeting response mentioning Buddy."""
    response = ai.get_socratic_fallback(user_input, [])
    assert "buddy" in response.lower()


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_fallback_generic_input():
    """Random input that doesn't match any keyword returns the generic Socratic response."""
    response = ai.get_socratic_fallback("Tell me about quicksort algorithm", [])
    assert "hypothesis" in response.lower() or "initial" in response.lower()


def test_fallback_empty_history():
    """Empty history list works without error."""
    response = ai.get_socratic_fallback("hello", [])
    assert isinstance(response, str)
    assert len(response) > 0
