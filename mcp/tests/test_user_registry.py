"""Tests for UserRegistry."""

from __future__ import annotations

import json

import pytest
from returns.maybe import Nothing, Some

from server.user_registry import UserRegistry


@pytest.fixture
def registry_file(tmp_path):
    """Create a valid user registry JSON file."""
    data = {
        "users": {
            "alice": {
                "mcp_password": "alice-pass",
                "ug_username": "a_op",
                "ug_password": "s3c",
                "ug_office_url": "https://ug.test",
                "ug_web_url": "https://ug.test",
            },
            "bob": {
                "mcp_password": "bob-pass",
                "ug_username": "b_admin",
                "ug_password": "s3c2",
                "ug_office_url": "https://ug.test",
            },
        }
    }
    path = tmp_path / "users.json"
    path.write_text(json.dumps(data))
    return path


@pytest.fixture
def registry(registry_file):
    return UserRegistry(registry_file)


def test_load_valid_file(registry):
    """Loading a valid JSON file populates the registry."""
    match registry.get_user("alice"):
        case Some(_):
            pass
        case _:
            pytest.fail("Expected Some for alice")
    match registry.get_user("bob"):
        case Some(_):
            pass
        case _:
            pytest.fail("Expected Some for bob")


def test_verify_correct_password(registry):
    assert registry.verify("alice", "alice-pass") is True


def test_verify_incorrect_password(registry):
    assert registry.verify("alice", "wrong") is False


def test_verify_missing_user(registry):
    assert registry.verify("nonexistent", "any") is False


def test_get_user_existing(registry):
    match registry.get_user("alice"):
        case Some(entry):
            assert entry.ug_username == "a_op"
            assert entry.ug_office_url == "https://ug.test"
        case _:
            pytest.fail("Expected Some for alice")


def test_get_user_missing(registry):
    assert registry.get_user("nonexistent") == Nothing


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        UserRegistry("/nonexistent/path/users.json")
