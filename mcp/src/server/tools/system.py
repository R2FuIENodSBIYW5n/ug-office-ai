"""System tools — users, permissions, roles, logs."""

from __future__ import annotations

from fastmcp import Context, FastMCP
from returns.result import Failure, Success

from ._helpers import get_client


def register(mcp: FastMCP) -> None:

    # --- Users ---

    @mcp.tool
    async def user_list(page: int = 1, limit: int = 50, ctx: Context = None) -> dict | list:
        """List users with pagination.

        Args:
            page: Page number (1-based).
            limit: Max results per page (default 50).

        Returns API response with user list and total count.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get("/1.0/users/", params={"page": page, "limit": limit}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def user_all(ctx: Context = None) -> dict | list:
        """List all users without pagination.

        Returns API response with the complete user list.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get("/1.0/users/all"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def user_list_by_ids(user_ids: list[int], ctx: Context = None) -> dict | list:
        """Get multiple users by their IDs.

        Args:
            user_ids: List of user IDs to retrieve.

        Returns API response with matching users.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post("/1.0/users/", json={"ids": user_ids}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def user_get(user_id: int, ctx: Context = None) -> dict | list:
        """Get a single user by ID.

        Args:
            user_id: The user's unique identifier.

        Returns API response with user details.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"/1.0/users/{user_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def user_update(user_id: int, data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Update a user's profile fields.

        Modifies user account data.

        Args:
            user_id: The user's unique identifier.
            data: Fields to update (e.g. name, email, status, role_id).

        Returns API response with the updated user.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"/1.0/users/{user_id}", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Permissions ---

    @mcp.tool
    async def permission_list(ctx: Context = None) -> dict | list:
        """List all available permissions.

        Returns API response with the full permissions list.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get("/1.0/permissions/"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def permission_refresh(ctx: Context = None) -> dict | list:
        """Refresh the server-side permissions cache.

        ⚠️ CAUTION: Refreshes the permissions cache for all users. This is a server-wide operation.

        Returns API response confirming the cache was refreshed.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get("/1.0/permissions/refresh"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def permission_create(data: dict, ctx: Context = None) -> dict | list:
        """Create a new permission entry.

        Args:
            data: Permission definition.

                Data keys:
                  - name (str, required): Permission name.
                  - description (str, optional): Human-readable description.
                  - resource (str, required): Resource this permission controls.
                  - action (str, required): Allowed action (e.g. read, write, delete).

        Returns API response with the created permission.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post("/1.0/permissions/", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def permission_update(data: dict, ctx: Context = None) -> dict | list:
        """Update an existing permission.

        Args:
            data: Permission fields to update.

                Data keys:
                  - id (int, required): Permission ID to update.
                  - name (str, optional): New name.
                  - description (str, optional): New description.
                  - resource (str, optional): New resource.
                  - action (str, optional): New action.

        Returns API response with the updated permission.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put("/1.0/permissions/", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Roles ---

    @mcp.tool
    async def role_list(ctx: Context = None) -> dict | list:
        """List all available roles.

        Returns API response with the full roles list.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get("/1.0/permissions/roles"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def role_create(data: dict, ctx: Context = None) -> dict | list:
        """Create a new role.

        Args:
            data: Role definition.

                Data keys:
                  - name (str, required): Role name.
                  - description (str, optional): Role description.

        Returns API response with the created role.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post("/1.0/permissions/roles", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def role_permission_list(role_id: int, ctx: Context = None) -> dict | list:
        """Get the permissions assigned to a role.

        Args:
            role_id: The role's unique identifier.

        Returns API response with the role's permission list.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"/1.0/permissions/roles/{role_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def role_permission_update(role_id: int, data: dict, ctx: Context = None) -> dict | list:
        """Update the permissions assigned to a role.

        Args:
            role_id: The role's unique identifier.
            data: Permission assignments.

                Data keys:
                  - permission_ids (list[int], required): Permissions to assign to this role.

        Returns API response with the updated role permissions.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"/1.0/permissions/roles/{role_id}", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def user_permission_list(user_id: int, ctx: Context = None) -> dict | list:
        """Get the permissions assigned to a user.

        Args:
            user_id: The user's unique identifier.

        Returns API response with the user's permission list.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"/1.0/permissions/users/{user_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def user_permission_update(user_id: int, data: dict, ctx: Context = None) -> dict | list:
        """Update the permissions assigned to a user.

        Args:
            user_id: The user's unique identifier.
            data: Permission assignments.

                Data keys:
                  - permission_ids (list[int], required): Permissions to assign to this user.

        Returns API response with the updated user permissions.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"/1.0/permissions/users/{user_id}", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Auth ---

    @mcp.tool
    async def auth_change_password(
        current_password: str, new_password: str, ctx: Context = None
    ) -> dict | list:
        """Change the current authenticated user's password.

        Args:
            current_password: The user's existing password.
            new_password: The desired new password.

        Returns API response confirming the password was changed.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(
                    "/1.0/auth/change-password",
                    json={"current_password": current_password, "new_password": new_password},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def auth_reset_password(user_id: int, password: str, ctx: Context = None) -> dict | list:
        """Reset a user's password as an administrator.

        ⚠️ DESTRUCTIVE: Resets another user's password without their consent. Confirm with user before calling.

        Args:
            user_id: The target user's unique identifier.
            password: The new password to set.

        Returns API response confirming the password was reset.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(
                    "/1.0/auth/reset-password",
                    json={"user_id": user_id, "password": password},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def auth_settings(ctx: Context = None) -> dict | list:
        """Get the current authenticated user's settings.

        Returns API response with user settings.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get("/1.0/auth/setting"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def auth_settings_update(data: dict, ctx: Context = None) -> dict | list:
        """Update the current authenticated user's settings.

        Args:
            data: Settings to update.

                Data keys:
                  - language (str, optional): Preferred language code.
                  - timezone (str, optional): Timezone identifier.
                  - notifications (dict, optional): Notification preferences.

        Returns API response with the updated settings.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put("/1.0/auth/setting", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()
