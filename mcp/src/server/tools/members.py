"""Member and vendor tools."""

from __future__ import annotations

from fastmcp import Context, FastMCP
from returns.result import Failure, Success

from ._helpers import get_client


def register(mcp: FastMCP) -> None:

    # --- Members ---

    @mcp.tool
    async def member_list(page: int = 1, limit: int = 50, ctx: Context = None) -> dict | list:
        """List members with pagination.

        Args:
            page: Page number (1-based).
            limit: Max results per page (default 50).

        Returns API response with member list and total count.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get("/1.0/member/", params={"page": page, "limit": limit}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Vendors ---

    @mcp.tool
    async def vendor_list(page: int = 1, limit: int = 50, ctx: Context = None) -> dict | list:
        """List vendors with pagination.

        Args:
            page: Page number (1-based).
            limit: Max results per page (default 50).

        Returns API response with vendor list and total count.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get("/1.0/vendor/", params={"page": page, "limit": limit}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def vendor_list_all(ctx: Context = None) -> dict | list:
        """List all vendors (no pagination).

        Returns API response with the complete vendor list.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get("/1.0/vendor/all"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def vendor_update_reward(data: dict, ctx: Context = None) -> dict | list:
        """Update vendor reward settings.

        ⚠️ DESTRUCTIVE: Changes reward/commission configuration for vendors. Confirm with user before calling.

        Args:
            data: Reward configuration.

                Data keys:
                  - vendor_id (int, required): Vendor to update.
                  - reward_type (str, optional): Type of reward.
                  - reward_value (float, optional): Reward amount or percentage.
                  - status (str, optional): Reward status.

        Returns API response confirming the update.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put("/1.0/vendor/update-reward", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Vendor Members ---

    @mcp.tool
    async def vendor_member_list(
        page: int = 1, limit: int = 50, ctx: Context = None
    ) -> dict | list:
        """List vendor members with pagination.

        Args:
            page: Page number (1-based).
            limit: Max results per page (default 50).

        Returns API response with vendor member list and total count.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(
                    "/1.0/vendor-member/", params={"page": page, "limit": limit}
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Member Tree ---

    @mcp.tool
    async def member_tree_list(page: int = 1, limit: int = 50, ctx: Context = None) -> dict | list:
        """List member tree with pagination.

        Args:
            page: Page number (1-based).
            limit: Max results per page (default 50).

        Returns API response with member tree entries and total count.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get("/1.0/member-tree/", params={"page": page, "limit": limit}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()
