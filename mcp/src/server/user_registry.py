"""User registry — maps MCP users to UG Office credentials."""

from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel
from returns.maybe import Maybe, Nothing, Some


class UserEntry(BaseModel, frozen=True):
    mcp_password: str
    ug_username: str
    ug_password: str
    ug_office_url: str
    ug_web_url: str = "https://www.ugoffice.com"


class UserRegistry:
    """Loads and queries the user registry JSON file."""

    def __init__(self, path: str | Path | None = None) -> None:
        if path is None:
            path = os.getenv("USER_REGISTRY_PATH", "data/user_registry.json")
        self._path = Path(path)
        self._users: dict[str, UserEntry] = {}
        self._load()

    def _load(self) -> None:
        data = json.loads(self._path.read_text())
        for name, entry in data.get("users", {}).items():
            self._users[name] = UserEntry(**entry)

    def get_user(self, mcp_username: str) -> Maybe[UserEntry]:
        user = self._users.get(mcp_username)
        return Some(user) if user is not None else Nothing

    def verify(self, username: str, password: str) -> bool:
        match self.get_user(username):
            case Some(user):
                return user.mcp_password == password
            case _:
                return False
