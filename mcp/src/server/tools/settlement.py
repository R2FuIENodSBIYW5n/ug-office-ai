"""Settlement tools — resolve, void, hold/unhold, freeze."""

from __future__ import annotations

from typing import Any

from fastmcp import Context, FastMCP
from returns.result import Failure, Success

from ._helpers import get_client

PREFIX = "/1.0/settlement"


def register(mcp: FastMCP) -> None:

    @mcp.tool
    async def settlement_list(
        page: int = 1,
        limit: int = 50,
        ctx: Context = None,
    ) -> dict | list:
        """List settlements with pagination.

        Args:
            page: Page number (1-based).
            limit: Max results per page (default 50).

        Returns API response with settlement list and total count.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}", params={"page": page, "limit": limit}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_incomplete_all(ctx: Context = None) -> dict | list:
        """List all incomplete settlements across all sports.

        Returns API response with incomplete settlement entries.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/incomplete-all"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_by_odds_ids(odds_ids: list[int], ctx: Context = None) -> dict | list:
        """Get settlements for specific odds IDs.

        Args:
            odds_ids: List of odds identifiers to look up.

        Returns API response with matching settlement records.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/by-odds-ids", json={"odds_ids": odds_ids}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_resolve(odds_id: int, outcome: str, ctx: Context = None) -> dict | list:
        """Resolve a settlement by odds ID and outcome.

        ⚠️ DESTRUCTIVE: Settles bets and triggers payouts. This cannot be easily undone. Confirm with user before calling.

        Args:
            odds_id: The odds identifier to resolve.
            outcome: Settlement outcome (e.g. "win", "lose", "void", "half-win").

        Returns API response with the resolution result.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/resolve",
                    json={"odds_id": odds_id, "outcome": outcome},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_resolve_by_result(match_id: int, ctx: Context = None) -> dict | list:
        """Resolve settlements using the match result.

        ⚠️ DESTRUCTIVE: Bulk-settles all bets for the match based on its final result. Confirm with user before calling.

        Args:
            match_id: The match whose final result drives settlement.

        Returns API response with resolution outcomes for affected settlements.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/resolve/by-result", json={"match_id": match_id}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_resolve_by_incomplete_result(
        match_id: int,
        ctx: Context = None,
    ) -> dict | list:
        """Resolve settlements using incomplete match result.

        ⚠️ DESTRUCTIVE: Settles bets using partial results. Use with caution — confirm with user before calling.

        Args:
            match_id: The match whose partial/incomplete result drives settlement.

        Returns API response with resolution outcomes for affected settlements.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/resolve/by-incomplete-result", json={"match_id": match_id}
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_resolve_by_outright(outright_id: int, ctx: Context = None) -> dict | list:
        """Resolve settlements for an outright event.

        ⚠️ DESTRUCTIVE: Settles outright bets and triggers payouts. Confirm with user before calling.

        Args:
            outright_id: The outright event identifier to resolve.

        Returns API response with the resolution result.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/resolve/by-outright-result/{outright_id}",
                    json={},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_resolve_number_game(match_id: int, ctx: Context = None) -> dict | list:
        """Resolve number game settlements.

        ⚠️ DESTRUCTIVE: Settles number game bets. Confirm with user before calling.

        Args:
            match_id: The number-game match to settle.

        Returns API response with the resolution result.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/resolve/number-game",
                    json={"match_id": match_id},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_by_outright(outright_id: int, ctx: Context = None) -> dict | list:
        """Get settlements for an outright event.

        Args:
            outright_id: The outright event identifier.

        Returns API response with settlement records for the outright.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/by-outright",
                    json={"outright_id": outright_id},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_match_stats(match_ids: list[int], ctx: Context = None) -> dict | list:
        """Get settlement statistics for matches.

        Args:
            match_ids: List of match identifiers to retrieve stats for.

        Returns API response with per-match settlement statistics.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/match-stats", json={"match_ids": match_ids}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_history(
        match_id: int | None = None,
        page: int = 1,
        limit: int = 50,
        ctx: Context = None,
    ) -> dict | list:
        """Get settlement history, optionally filtered by match.

        Args:
            match_id: Filter history to a specific match (None for all).
            page: Page number (1-based).
            limit: Max results per page (default 50).

        Returns API response with paginated settlement history records.
        """
        body: dict[str, Any] = {"page": page, "limit": limit}
        if match_id is not None:
            body["match_id"] = match_id
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/settlement-history", json=body):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_hold_list(
        page: int = 1,
        limit: int = 50,
        ctx: Context = None,
    ) -> dict | list:
        """List settlements currently on hold.

        Args:
            page: Page number (1-based).
            limit: Max results per page (default 50).

        Returns API response with held settlements and total count.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/settlement-hold",
                    json={"page": page, "limit": limit},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_task_hold_list(
        page: int = 1,
        limit: int = 50,
        ctx: Context = None,
    ) -> dict | list:
        """List settlement tasks currently on hold.

        Args:
            page: Page number (1-based).
            limit: Max results per page (default 50).

        Returns API response with held settlement tasks and total count.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/settlement-task-hold", json={"page": page, "limit": limit}
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_hold(
        settlement_ids: list[int],
        ctx: Context = None,
    ) -> dict | list:
        """Put settlements on hold.

        ⚠️ CAUTION: Prevents settlement processing. Settlements must be manually unheld later.

        Args:
            settlement_ids: List of settlement identifiers to hold.

        Returns API response confirming the hold operation.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/settlement-hold/hold",
                    json={"settlement_ids": settlement_ids},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_unhold(
        settlement_ids: list[int],
        ctx: Context = None,
    ) -> dict | list:
        """Release settlements from hold.

        ⚠️ CAUTION: Releases held settlements for processing. Payouts may be triggered. Confirm with user before calling.

        Args:
            settlement_ids: List of settlement identifiers to release.

        Returns API response confirming the unhold operation.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/settlement-hold/unhold",
                    json={"settlement_ids": settlement_ids},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_hold_details(
        settlement_id: int,
        ctx: Context = None,
    ) -> dict | list:
        """Get details of a held settlement.

        Args:
            settlement_id: The held settlement to inspect.

        Returns API response with detailed hold information.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/settlement-hold/details",
                    json={"settlement_id": settlement_id},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_check(ctx: Context = None) -> dict | list:
        """Run settlement health check.

        Returns API response with settlement system health status.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/check"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_try_settle_ticket(
        ticket_id: int,
        ctx: Context = None,
    ) -> dict | list:
        """[DESTRUCTIVE] Attempt to settle a specific ticket.

        Forces settlement processing on an individual ticket. May trigger
        payouts that cannot be reversed automatically.

        Side effects: May finalise the ticket outcome and adjust the member balance.

        Args:
            ticket_id: The ticket identifier to attempt settlement on.

        Returns API response with the settlement attempt result.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/try-settle-ticket",
                    json={"ticket_id": ticket_id},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_recovery_missing(
        match_id: int,
        ctx: Context = None,
    ) -> dict | list:
        """Recover missing settlement for a match.

        ⚠️ DESTRUCTIVE: Re-creates missing settlement records and may trigger payouts. Confirm with user before calling.

        Args:
            match_id: The match whose missing settlements should be recovered.

        Returns API response with recovery result.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/recovery-missing-settlement", json={"match_id": match_id}
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_unhold_task(task_id: int, ctx: Context = None) -> dict | list:
        """[WRITE] Unhold a settlement task.

        Releases a held settlement task so it can be processed. Reverses a previous hold.

        Side effects: Re-enables processing for the specified settlement task.

        Args:
            task_id: The settlement task identifier to release from hold.

        Returns API response confirming the task was unheld.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(
                    f"{PREFIX}/unhold-settlement-task",
                    json={"task_id": task_id},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_ignore_task(task_id: int, ctx: Context = None) -> dict | list:
        """Ignore a settlement task.

        ⚠️ CAUTION: Marks a settlement task as ignored — it will not be processed. Confirm with user before calling.

        Args:
            task_id: The settlement task identifier to mark as ignored.

        Returns API response confirming the task was ignored.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(
                    f"{PREFIX}/ignore-settlement-task",
                    json={"task_id": task_id},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Freeze sub-routes ---

    @mcp.tool
    async def settlement_freeze_tickets(
        page: int = 1,
        limit: int = 50,
        ctx: Context = None,
    ) -> dict | list:
        """List frozen settlement tickets.

        Args:
            page: Page number (1-based).
            limit: Max results per page (default 50).

        Returns API response with frozen tickets and total count.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/freeze/tickets",
                    json={"page": page, "limit": limit},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_freeze_members(
        page: int = 1,
        limit: int = 50,
        ctx: Context = None,
    ) -> dict | list:
        """List frozen settlement members.

        Args:
            page: Page number (1-based).
            limit: Max results per page (default 50).

        Returns API response with frozen members and total count.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/freeze/members",
                    json={"page": page, "limit": limit},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Settlement change sub-routes ---

    @mcp.tool
    async def settlement_change_list(
        page: int = 1,
        limit: int = 50,
        ctx: Context = None,
    ) -> dict | list:
        """List settlement changes.

        Args:
            page: Page number (1-based).
            limit: Max results per page (default 50).

        Returns API response with settlement change records and total count.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/settlement-change",
                    json={"page": page, "limit": limit},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_change_log(ctx: Context = None) -> dict | list:
        """Get settlement change log.

        Returns API response with the full change log.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/settlement-change/log"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Settlement notification sub-routes ---

    @mcp.tool
    async def settlement_notification_list(
        page: int = 1,
        limit: int = 50,
        ctx: Context = None,
    ) -> dict | list:
        """List settlement notifications.

        Args:
            page: Page number (1-based).
            limit: Max results per page (default 50).

        Returns API response with notification records and total count.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/settlement-notification", json={"page": page, "limit": limit}
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_notification_schedule(
        notification_id: int,
        ctx: Context = None,
    ) -> dict | list:
        """[WRITE] Schedule a settlement notification.

        Queues a notification for delivery. Can be cancelled with settlement_notification_cancel.

        Side effects: Enqueues the notification for future delivery.

        Args:
            notification_id: The notification identifier to schedule.

        Returns API response confirming the notification was scheduled.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/settlement-notification/schedule",
                    json={"notification_id": notification_id},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_notification_cancel(
        notification_id: int,
        ctx: Context = None,
    ) -> dict | list:
        """[WRITE] Cancel a settlement notification.

        Cancels a previously scheduled notification. Can be re-scheduled with settlement_notification_schedule.

        Side effects: Removes the notification from the delivery queue.

        Args:
            notification_id: The notification identifier to cancel.

        Returns API response confirming the notification was cancelled.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/settlement-notification/cancel",
                    json={"notification_id": notification_id},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def settlement_notification_rollback(
        notification_id: int,
        ctx: Context = None,
    ) -> dict | list:
        """Rollback a settlement notification.

        ⚠️ DESTRUCTIVE: Reverses a settlement notification. This may reverse payouts. Confirm with user before calling.

        Args:
            notification_id: The notification identifier to roll back.

        Returns API response confirming the notification was rolled back.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/settlement-notification/rollback",
                    json={"notification_id": notification_id},
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()
