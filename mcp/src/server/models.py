"""Shared result types for functional error handling."""

from __future__ import annotations

from pydantic import BaseModel


class APIError(BaseModel, frozen=True):
    """Typed error model replacing untyped error dicts."""

    error: str
    detail: str


class APIResponse(BaseModel, frozen=True):
    """Typed success wrapper for API responses."""

    data: dict | list
