"""Extended OAuth token models with per-user identity."""

from __future__ import annotations

from mcp.server.auth.provider import AccessToken, AuthorizationCode, RefreshToken
from pydantic import ConfigDict


class UGAuthorizationCode(AuthorizationCode):
    model_config = ConfigDict(frozen=True)
    user_id: str


class UGAccessToken(AccessToken):
    model_config = ConfigDict(frozen=True)
    user_id: str


class UGRefreshToken(RefreshToken):
    model_config = ConfigDict(frozen=True)
    user_id: str
