"""
Phase 2 — Unit Tests: Mock Course Generation

Tests get_mock_courses() from course.py — the local course generator
that returns hardcoded results when Google API keys aren't configured.
Pure function, no external API calls.
"""

import pytest

import course


# ---------------------------------------------------------------------------
# Mock course output validation
# ---------------------------------------------------------------------------

def test_mock_courses_returns_list():
    """get_mock_courses returns a list."""
    result = course.get_mock_courses("Python", "OOP")
    assert isinstance(result, list)


def test_mock_courses_count():
    """Always returns exactly 3 mock courses."""
    result = course.get_mock_courses("Python", "OOP")
    assert len(result) == 3


@pytest.mark.parametrize("skill, topic", [
    ("Python", "OOP"),
    ("JavaScript", "React"),
    ("Java", "Data Structures"),
])
def test_mock_courses_contain_skill_and_topic(skill, topic):
    """Each mock course title or description includes the skill name."""
    result = course.get_mock_courses(skill, topic)
    for item in result:
        # At least the title or description should mention the skill
        combined = (item["title"] + item["description"]).lower()
        assert skill.lower() in combined, f"Skill '{skill}' not found in course: {item['title']}"


def test_mock_courses_have_required_keys():
    """Each course dict has the expected keys: title, url, description."""
    result = course.get_mock_courses("Python", "Loops")
    required_keys = {"title", "url", "description"}
    for item in result:
        assert required_keys.issubset(item.keys()), f"Missing keys in: {item}"
