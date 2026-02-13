"""Ticket tools — search, status, void, pause."""

from __future__ import annotations

from fastmcp import Context, FastMCP
from returns.result import Failure, Success

from ._helpers import get_client

PREFIX = "/1.0/ticket"


def register(mcp: FastMCP) -> None:

    @mcp.tool
    async def ticket_list(page: int = 1, limit: int = 50, ctx: Context = None) -> dict | list:
        """List tickets with pagination.

        Args:
            page: Page number, 1-based (default 1).
            limit: Max results per page (default 50).

        Returns API response with ticket list and total count.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/", params={"page": page, "limit": limit}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_search(data: dict, ctx: Context = None) -> dict | list:
        """Search tickets with filters.

        Args:
            data: Search filters.

                Data keys:
                  - date_from (str, optional): Start date YYYY-MM-DD.
                  - date_to (str, optional): End date YYYY-MM-DD.
                  - member_id (int, optional): Filter by member.
                  - match_id (int, optional): Filter by match.
                  - status (str, optional): Ticket status filter.
                  - sport_id (int, optional): Filter by sport.
                  - page (int, optional): Page number.
                  - limit (int, optional): Results per page.

        Returns API response with matching tickets.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_get(ticket_id: int, ctx: Context = None) -> dict | list:
        """Get a single ticket by ID.

        Args:
            ticket_id: Unique identifier of the ticket.

        Returns API response with full ticket details.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/{ticket_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_force_status(data: dict, ctx: Context = None) -> dict | list:
        """Force a ticket status change.

        ⚠️ DESTRUCTIVE: Overrides the normal ticket lifecycle. Confirm with user before calling.
        Use ticket_reset_status to revert a ticket to its default state instead.

        Args:
            data: Status change payload.

                Data keys:
                  - ticket_id (int, required): Ticket to update.
                  - status (str, required): Target status to force.

        Returns API response confirming the status update.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/force-status", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_query_nt(data: dict, ctx: Context = None) -> dict | list:
        """Query ticket notification/transaction data.

        Args:
            data: Query parameters.

                Data keys:
                  - ticket_id (int, optional): Filter by ticket.
                  - date_from (str, optional): Start date YYYY-MM-DD.
                  - date_to (str, optional): End date YYYY-MM-DD.

        Returns API response with notification/transaction records.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/query-nt", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_reset_status(data: dict, ctx: Context = None) -> dict | list:
        """Reset ticket status to its default state.

        ⚠️ DESTRUCTIVE: Resets the ticket's status. Use this to undo a forced status change.
        For forcing to a specific status, use ticket_force_status instead.

        Args:
            data: Reset payload.

                Data keys:
                  - ticket_id (int, required): Ticket to reset.

        Returns API response confirming the status reset.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/reset-status", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_request(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Submit a new ticket request.

        Creates a pending ticket. Must be confirmed separately.

        Args:
            data: Ticket request payload.

                Data keys:
                  - member_id (int, required): Member placing the bet.
                  - match_id (int, required): Match to bet on.
                  - selections (list[dict], required): Bet selections.
                  - stake (float, required): Bet amount.

        Returns API response with the created ticket or validation result.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/request", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_confirmation(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Confirm a ticket.

        Accepts the ticket, committing the wager. Affects member balance.

        Args:
            data: Confirmation payload.

                Data keys:
                  - ticket_id (int, required): Ticket to confirm.

        Returns API response confirming the ticket acceptance.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/confirmation", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_outrights(data: dict, ctx: Context = None) -> dict | list:
        """Get outright tickets.

        Args:
            data: Query filters.

                Data keys:
                  - date_from (str, optional): Start date YYYY-MM-DD.
                  - date_to (str, optional): End date YYYY-MM-DD.
                  - status (str, optional): Filter by status.

        Returns API response with outright ticket records.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/outrights", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_status_history(data: dict, ctx: Context = None) -> dict | list:
        """Get ticket status history.

        Args:
            data: Query payload.

                Data keys:
                  - ticket_id (int, required): Ticket to get history for.

        Returns API response with chronological status changes.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/status-history", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_notification_history(ctx: Context = None) -> dict | list:
        """Get ticket notification history.

        Returns API response with notification history records.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/notification/history"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_query_insurance(data: dict, ctx: Context = None) -> dict | list:
        """Query ticket insurance data.

        Args:
            data: Query filters.

                Data keys:
                  - ticket_id (int, optional): Filter by ticket.
                  - member_id (int, optional): Filter by member.

        Returns API response with insurance details for matching tickets.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/query-insurance", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_request_insurance(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Request ticket insurance.

        Adds insurance to a ticket, affecting payout calculations.

        Args:
            data: Insurance request payload.

                Data keys:
                  - ticket_id (int, required): Ticket to insure.

        Returns API response confirming the insurance request.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/request-insurance", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_cashout(ctx: Context = None) -> dict | list:
        """Get cashout tickets.

        Returns API response with tickets eligible for cashout.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/cashout"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_trigger_reject_event(match_id: int, ctx: Context = None) -> dict | list:
        """Trigger a reject event for a specific match.

        ⚠️ DESTRUCTIVE: Rejects pending tickets for this match. Confirm with user before calling.

        Args:
            match_id: Unique identifier of the match.

        Returns API response confirming the reject event was triggered.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/trigger-reject-event/{match_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_calculate_totals(ctx: Context = None) -> dict | list:
        """Calculate total tickets.

        Returns API response with aggregated ticket totals.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/calcula-total-tickets"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Pause ---

    @mcp.tool
    async def ticket_pause_global(ctx: Context = None) -> dict | list:
        """Get global ticket pause status.

        Returns API response with the current global pause state.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/pause/global"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_pause_sports(ctx: Context = None) -> dict | list:
        """Get ticket pause status by sports.

        Returns API response with pause state for each sport.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/pause/sports"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_pause_by_match(match_id: int, ctx: Context = None) -> dict | list:
        """Get ticket pause status for a specific match.

        Args:
            match_id: Unique identifier of the match.

        Returns API response with the pause state for the match.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/pause/{match_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def ticket_pause_update(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Update ticket pause settings.

        Pauses or unpauses ticket acceptance. Affects live trading.

        Args:
            data: Pause configuration.

                Data keys:
                  - enabled (bool, required): Whether to enable or disable pause.
                  - sport_id (int, optional): Pause for a specific sport.
                  - match_id (int, optional): Pause for a specific match.

        Returns API response confirming the pause settings update.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/pause", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()
