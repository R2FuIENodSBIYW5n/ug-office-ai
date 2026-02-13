"""Operator tools — CRUD, config, currencies, packages."""

from __future__ import annotations

from fastmcp import Context, FastMCP
from returns.result import Failure, Success

from ._helpers import get_client

PREFIX = "/1.0/operators"


def register(mcp: FastMCP) -> None:

    @mcp.tool
    async def operator_list(data: dict | None = None, ctx: Context = None) -> dict | list:
        """List operators with optional filters.

        Args:
            data: Optional filter criteria dict (e.g. status, name).

        Returns API response with operator list.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/", json=data or {}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def operator_create(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Create a new operator.

        Adds a new operator to the system.

        Args:
            data: Operator definition.

                Data keys:
                  - name (str, required): Operator name.
                  - status (str, optional): Initial status.
                  - settings (dict, optional): Operator settings.

        Returns API response with the created operator.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/create", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def operator_get(operator_id: int, ctx: Context = None) -> dict | list:
        """Get an operator by ID.

        Args:
            operator_id: Unique identifier of the operator.

        Returns API response with operator details.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/{operator_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def operator_update(operator_id: int, data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Update an operator.

        Modifies operator settings. Changes take effect immediately.

        Args:
            operator_id: Unique identifier of the operator to update.
            data: Operator fields to update (e.g. name, status, settings).

        Returns API response with the updated operator.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/{operator_id}", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def operator_config(operator_id: int, ctx: Context = None) -> dict | list:
        """Get operator configuration.

        Args:
            operator_id: Unique identifier of the operator.

        Returns API response with operator configuration.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/{operator_id}/config"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def operator_config_update(
        operator_id: int, data: dict, ctx: Context = None
    ) -> dict | list:
        """[WRITE] Update operator configuration.

        Changes operator config. May affect bet limits, markets, and trading behavior.

        Args:
            operator_id: Unique identifier of the operator.
            data: Configuration fields to update (e.g. limits, features, integrations).

        Returns API response with the updated configuration.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/{operator_id}/config", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def operator_currencies(operator_id: int, ctx: Context = None) -> dict | list:
        """Get operator currencies.

        Args:
            operator_id: Unique identifier of the operator.

        Returns API response with the operator's currency list.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/{operator_id}/currencies"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def operator_currencies_update(
        operator_id: int, data: dict, ctx: Context = None
    ) -> dict | list:
        """[WRITE] Update operator currencies.

        Changes available currencies for the operator.

        Args:
            operator_id: Unique identifier of the operator.
            data: Currency settings to update (e.g. currency codes, exchange rates, enabled flags).

        Returns API response with the updated currency list.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/{operator_id}/currencies", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def operator_packages(operator_id: int, ctx: Context = None) -> dict | list:
        """Get operator packages.

        Args:
            operator_id: Unique identifier of the operator.

        Returns API response with the operator's package list.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/{operator_id}/package"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def operator_package_update(
        operator_id: int, data: dict, ctx: Context = None
    ) -> dict | list:
        """[WRITE] Update operator package.

        Modifies the operator's package assignment.

        Args:
            operator_id: Unique identifier of the operator.
            data: Package fields to update (e.g. package_id, features, limits).

        Returns API response with the updated package.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/{operator_id}/package", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()
