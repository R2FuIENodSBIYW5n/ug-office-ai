"""MCP Resources — read-only, low-volatility reference data.

Resources give clients prefetched context without the LLM needing to call a tool.
These expose stable reference data that changes infrequently.
"""

from __future__ import annotations

from fastmcp import Context, FastMCP
from returns.result import Failure, Success

from .tools._helpers import get_client


def register(mcp: FastMCP) -> None:
    """Register all MCP resources."""

    @mcp.resource("ug-office://sports")
    async def sports_resource(ctx: Context = None) -> str:
        """All available sports with IDs and names.

        Low-volatility reference data — sports rarely change.
        """
        match await get_client(ctx):
            case Failure(err):
                return f"Error: {err.detail}"
            case Success(client):
                match await client.get("/1.0/sports/"):
                    case Success(data):
                        if isinstance(data, dict) and "data" in data:
                            items = data["data"]
                        else:
                            items = data
                        lines = ["# Available Sports", ""]
                        if isinstance(items, list):
                            for s in items:
                                if isinstance(s, dict):
                                    lines.append(
                                        f"- **{s.get('name', 'Unknown')}** (id: {s.get('id', '?')})"
                                    )
                        return "\n".join(lines)
                    case Failure(err):
                        return f"Error: {err.detail}"

    @mcp.resource("ug-office://sports/groups")
    async def sport_groups_resource(ctx: Context = None) -> str:
        """Sport group definitions.

        Low-volatility reference data.
        """
        match await get_client(ctx):
            case Failure(err):
                return f"Error: {err.detail}"
            case Success(client):
                match await client.get("/1.0/sports/groups"):
                    case Success(data):
                        import json

                        return json.dumps(data, indent=2, default=str)
                    case Failure(err):
                        return f"Error: {err.detail}"

    @mcp.resource("ug-office://markets/types")
    async def market_types_resource(ctx: Context = None) -> str:
        """All market type definitions (e.g. Handicap, Over/Under, 1X2).

        Low-volatility reference data — market types rarely change.
        """
        match await get_client(ctx):
            case Failure(err):
                return f"Error: {err.detail}"
            case Success(client):
                match await client.get("/1.0/sports/markets/types"):
                    case Success(data):
                        import json

                        return json.dumps(data, indent=2, default=str)
                    case Failure(err):
                        return f"Error: {err.detail}"

    @mcp.resource("ug-office://permissions")
    async def permissions_resource(ctx: Context = None) -> str:
        """All available permissions.

        Low-volatility reference data — useful for understanding access control.
        """
        match await get_client(ctx):
            case Failure(err):
                return f"Error: {err.detail}"
            case Success(client):
                match await client.get("/1.0/permissions/"):
                    case Success(data):
                        import json

                        return json.dumps(data, indent=2, default=str)
                    case Failure(err):
                        return f"Error: {err.detail}"

    @mcp.resource("ug-office://roles")
    async def roles_resource(ctx: Context = None) -> str:
        """All available roles.

        Low-volatility reference data — useful for user management context.
        """
        match await get_client(ctx):
            case Failure(err):
                return f"Error: {err.detail}"
            case Success(client):
                match await client.get("/1.0/permissions/roles"):
                    case Success(data):
                        import json

                        return json.dumps(data, indent=2, default=str)
                    case Failure(err):
                        return f"Error: {err.detail}"

    @mcp.resource("ug-office://vendors")
    async def vendors_resource(ctx: Context = None) -> str:
        """All vendors (odds providers).

        Low-volatility reference data — vendor list rarely changes.
        """
        match await get_client(ctx):
            case Failure(err):
                return f"Error: {err.detail}"
            case Success(client):
                match await client.get("/1.0/vendor/all"):
                    case Success(data):
                        import json

                        return json.dumps(data, indent=2, default=str)
                    case Failure(err):
                        return f"Error: {err.detail}"

    @mcp.resource("ug-office://api-map")
    async def api_map_resource() -> str:
        """API domain map — overview of all available tool categories.

        Helps the LLM understand which tools are available and when to use them.
        """
        return """\
# UG Office MCP — API Domain Map

## Tool Domains

### settlement (29 tools)
Resolve, void, hold/unhold, freeze settlements for matches and outrights.
- Key tools: `settlement_resolve`, `settlement_resolve_by_result`, `settlement_hold`, `settlement_unhold`
- All resolve/hold/unhold/ignore tools are **[WRITE]** operations

### sports (88 tools)
Matches, odds, tournaments, competitors, markets — the core trading domain.
- **Read**: `sports_list`, `sports_tournaments`, `sports_matches_search`, `sports_match_odds`
- **Write**: `sports_update`, `sports_match_update`, `sports_match_publish`, `sports_match_close`
- Odds via Socket.IO: `sports_match_odds`

### tickets (20 tools)
Ticket management — search, void, pause, insurance.
- **Read**: `ticket_list`, `ticket_search`, `ticket_get`
- **Write**: `ticket_force_status`, `ticket_reset_status`, `ticket_pause_update`

### reports (7 tools)
Win/Loss, performance, turnover, odds performance reports.
- All read-only: `report_winloss`, `report_performance_vendor`, `report_odds_performance`

### operators (10 tools)
Operator CRUD, config, currencies, packages.
- **Read**: `operator_list`, `operator_get`, `operator_config`
- **Write**: `operator_create`, `operator_update`, `operator_config_update`

### members (6 tools)
Member/vendor listing.
- Mostly read-only: `member_list`, `vendor_list`, `vendor_list_all`
- **Write**: `vendor_update_reward`

### system (19 tools)
Users, permissions, roles, auth settings.
- **Read**: `user_list`, `permission_list`, `role_list`
- **Write**: `user_update`, `auth_reset_password`, `role_permission_update`

### browser (6 tools)
Playwright-based browser automation fallback.
- `browse_page`, `screenshot_page`, `extract_table`, `page_interact`
- `page_evaluate` — **[DESTRUCTIVE]** executes JavaScript (admin only)

## Common Workflows
1. **Win/Loss Report** → `report_winloss(date_from, date_to)`
2. **Find a match** → `sports_matches_search(keyword)` or `sports_tournaments_today()`
3. **Get live odds** → `sports_match_odds(match_id)`
4. **Settle a match** → `settlement_resolve_by_result(match_id)`
5. **Screenshot a page** → `screenshot_page(url)` or `screenshot_winloss_report()`
"""
