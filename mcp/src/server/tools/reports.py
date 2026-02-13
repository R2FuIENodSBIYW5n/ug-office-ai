"""Report tools — winloss, odds-diff, total-bet, performance."""

from __future__ import annotations

from fastmcp import Context, FastMCP
from returns.result import Failure, Success

from ._helpers import get_client

PREFIX = "/1.0/reports"


def register(mcp: FastMCP) -> None:
    # --- Win/Loss ---

    def _compute_usd_total(rows: list[dict]) -> dict:
        """Sum to_usd_* fields across rows — replicates the web UI's USD Total footer."""
        total = {
            "_summary": "USD TOTAL",
            "ticket": sum(r.get("ticket", 0) for r in rows),
            "net_turnover_usd": sum(r.get("to_usd_net_turnover", 0) for r in rows),
            "stake_usd": sum(r.get("to_usd_stake", 0) for r in rows),
            "price_usd": sum(r.get("to_usd_price", 0) for r in rows),
            "payout_usd": sum(r.get("to_usd_payout", 0) for r in rows),
            "winloss_usd": sum(r.get("to_usd_winloss", 0) for r in rows),
            "net_winloss_usd": sum(r.get("to_usd_net_winloss", 0) for r in rows),
            "cashout_stake_usd": sum(r.get("to_usd_cashout_stake", 0) for r in rows),
            "cashout_usd": sum(r.get("to_usd_cashout", 0) for r in rows),
            "cashout_winloss_usd": sum(r.get("to_usd_cashout_winloss", 0) for r in rows),
        }
        net_to = total["net_turnover_usd"]
        total["margin_pct"] = round((total["net_winloss_usd"] / net_to) * 100, 2) if net_to else 0
        return total

    @mcp.tool
    async def report_winloss(
        date_from: str,
        date_to: str,
        bet_type: str = "all",
        group_by: str = "currency_id",
        include_internal: bool = False,
        include_usd_total: bool = True,
        page: int = 1,
        per_page: int = 30,
        ctx: Context = None,
    ) -> dict | list:
        """Get win/loss report with flexible filters.

        Args:
            date_from: Start date (YYYY-MM-DD).
            date_to: End date (YYYY-MM-DD).
            bet_type: "all", "single", or "parlay".
            group_by: Grouping — "currency_id" (default), "vendor_id", "group_id", "date".
            include_internal: Include internal tickets.
            include_usd_total: Append a computed USD total summary row.
            page: Page number (1-based).
            per_page: Results per page.
        """
        params = {
            "page": page,
            "per_page": per_page,
            "currency": "USD",
            "currency_mode": 1,
            "internal": 1 if include_internal else 0,
            "from": date_from,
            "to": date_to,
            "group_by": group_by,
        }
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/winloss/{bet_type}", params=params):
                    case Success(data):
                        if include_usd_total:
                            rows = data.get("data", []) if isinstance(data, dict) else data
                            return {"data": rows, "usd_total": _compute_usd_total(rows)}
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Performance ---

    @mcp.tool
    async def report_performance_vendor(ctx: Context = None) -> dict | list:
        """Get vendor performance report.

        Returns API response with performance metrics by vendor.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/performance/vendor"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Total Bet ---

    @mcp.tool
    async def report_total_bet(ctx: Context = None) -> dict | list:
        """Get total bet report.

        Returns API response with total bet summary.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/total-bet"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def report_total_bet_maodds(ctx: Context = None) -> dict | list:
        """Get total bet maodds report.

        Returns API response with total bet data at MA odds level.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/total-bet-maodds"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Category Turnover ---

    @mcp.tool
    async def report_category_turnover(ctx: Context = None) -> dict | list:
        """Get category turnover report.

        Returns API response with turnover data grouped by category.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/category-turnover"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Odds Performance ---

    @mcp.tool
    async def report_odds_performance(ctx: Context = None) -> dict | list:
        """Search odds performance.

        Returns API response with odds performance records.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/odds-performance"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def report_odds_performance_by_match(match_id: int, ctx: Context = None) -> dict | list:
        """Get odds performance for a specific match.

        Args:
            match_id: Numeric identifier of the match to query.

        Returns API response with odds performance data for the match.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/odds-performance/{match_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()
