"""Tests for SessionStore."""

from __future__ import annotations

import pytest
from returns.result import Failure, Success

from server.session_store import SessionStore
from server.user_registry import UserRegistry


@pytest.fixture
def registry(tmp_path):
    """Create a UserRegistry backed by a temporary JSON file."""
    path = tmp_path / "users.json"
    path.write_text(
        '{"users": {"alice": {'
        '"mcp_password": "pass", "ug_username": "a_op", '
        '"ug_password": "s3c", "ug_office_url": "https://ug.test"}}}'
    )
    return UserRegistry(path)


@pytest.fixture
def store(registry):
    return SessionStore(registry)


async def test_get_client_returns_same_instance(store):
    """Double-check locking: calling get_client twice returns the same client."""
    result1 = await store.get_client("alice")
    result2 = await store.get_client("alice")
    match (result1, result2):
        case (Success(c1), Success(c2)):
            assert c1 is c2
        case _:
            pytest.fail("Expected two Success results")


async def test_get_client_unknown_user_returns_failure(store):
    """Unknown user returns Failure."""
    result = await store.get_client("nonexistent")
    match result:
        case Failure(err):
            assert "Unknown user" in err.detail
        case _:
            pytest.fail("Expected Failure")


async def test_close_all_clears_clients(store):
    """close_all() closes all clients and empties the cache."""
    await store.get_client("alice")
    assert len(store._clients) == 1
    await store.close_all()
    assert len(store._clients) == 0
