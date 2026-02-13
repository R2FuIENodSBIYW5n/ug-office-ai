"""MCP Prompts — reusable workflow templates for common operations.

Prompts help LLMs navigate the 185-tool surface by providing structured
templates for the most common back-office workflows.
"""

from __future__ import annotations

from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register all MCP prompt templates."""

    @mcp.prompt()
    async def daily_settlement(sport: str = "all") -> str:
        """Guide for resolving today's completed matches.

        Walks through finding finished matches, checking results, and
        triggering settlement resolution.
        """
        sport_filter = (
            ""
            if sport == "all"
            else f"\nFilter results to sport: **{sport}**."
        )

        return f"""\
You are helping resolve today's settlements for UG Office.{sport_filter}

Follow these steps:

1. **Find today's tournaments**: Call `sports_tournaments_today()` to see what's playing today.

2. **Check each tournament for completed matches**: For each tournament, call
   `sports_tournament_matches(tournament_id)` and look for matches with status "ended".

3. **Verify match results**: For each ended match, call
   `sports_match_providers_result(match_id)` to confirm provider results are available.

4. **Check incomplete settlements**: Call `settlement_incomplete_all()` to see
   what still needs resolving.

5. **Resolve settlements**: For each match with confirmed results, call
   `settlement_resolve_by_result(match_id)`.

6. **Verify**: After resolving, call `settlement_incomplete_all()` again to
   confirm the count decreased.

**Important**: Settlement resolution is a [WRITE] operation that affects payouts.
Always verify match results from multiple providers before resolving.
"""

    @mcp.prompt()
    async def winloss_analysis(
        date_from: str = "",
        date_to: str = "",
        breakdown: str = "currency",
    ) -> str:
        """Template for generating P&L / Win-Loss reports.

        Provides a structured approach to querying and analyzing win/loss data
        across different dimensions.
        """
        date_hint = ""
        if date_from and date_to:
            date_hint = f"\nDate range: **{date_from}** to **{date_to}**."
        elif date_from:
            date_hint = f"\nStart date: **{date_from}** (use today as end date)."
        else:
            date_hint = "\nUse today's date for both date_from and date_to unless told otherwise."

        group_map = {
            "currency": "currency_id",
            "vendor": "vendor_id",
            "group": "group_id",
            "date": "date",
        }
        group_by = group_map.get(breakdown, "currency_id")

        return f"""\
You are generating a Win/Loss analysis report for UG Office.{date_hint}

Follow these steps:

1. **Get the overview**: Call `report_winloss(date_from, date_to, group_by="{group_by}")`.
   This returns rows grouped by {breakdown} with a computed USD total.

2. **Key metrics to highlight**:
   - **Net Turnover (USD)**: Total wagered amount
   - **Net Win/Loss (USD)**: Company profit/loss
   - **Margin %**: Net Win/Loss as percentage of Net Turnover
   - **Ticket Count**: Volume of bets

3. **Compare bet types** (if relevant): Run separate queries with
   `bet_type="single"` and `bet_type="parlay"` to compare singles vs parlays.

4. **Drill down by vendor**: If grouped by currency, optionally run
   `report_winloss(..., group_by="vendor_id")` for vendor-level breakdown.

5. **Present results**: Format as a clear summary table showing the key metrics.
   Highlight any unusual margins (< 0% means loss, > 10% is high margin).
"""

    @mcp.prompt()
    async def odds_check(team: str = "", match_id: str = "") -> str:
        """Template for checking and comparing odds lines.

        Guides through finding a match and retrieving current odds.
        """
        search_hint = ""
        if match_id:
            search_hint = f"\nMatch ID is known: **{match_id}**. Skip to step 2."
        elif team:
            search_hint = f"\nSearch for team: **{team}**."

        return f"""\
You are checking odds for a match on UG Office.{search_hint}

Follow these steps:

1. **Find the match**:
   - If you have a team name: `sports_matches_search(keyword="{team or '<team name>'}")`
   - If looking at today's games: `sports_tournaments_today()` → `sports_tournament_matches(tournament_id)`
   - If looking at upcoming: `sports_fixtures_incoming()`

2. **Get current odds**: Call `sports_match_odds(match_id)`.
   Default markets: FT Handicap (101001), FT O/U (102001), 1H Handicap (101011), 1H O/U (102011).

3. **Get specific market odds**: For other markets, first call
   `sports_match_odds_markets(match_id)` to see available markets, then
   `sports_match_odds(match_id, market_ids=[...])`.

4. **Check odds history**: Call `sports_odds_history(data={{"match_id": <id>, "market_id": <id>}})`
   to see how odds have moved.

5. **Present results**: Show odds in a clear format:
   - Handicap: Home/Away line and price
   - Over/Under: Line and Over/Under prices
   - Include odds movement direction if history was checked.
"""

    @mcp.prompt()
    async def match_search(keyword: str = "") -> str:
        """Template for finding and inspecting a specific match.

        Combines search, match details, odds, and settlement status.
        """
        return f"""\
You are finding and inspecting a match on UG Office.
{"Search for: **" + keyword + "**" if keyword else "Ask the user what match they're looking for."}

Follow these steps:

1. **Search**: Call `sports_matches_search(keyword="{keyword or '<keyword>'}")`.
   This returns match_id, teams, tournament, start_time, and status.

2. **Get full details**: Call `sports_match_get(match_id)` for complete match info.

3. **Based on match status**:
   - **prematch**: Show odds with `sports_match_odds(match_id)`
   - **live**: Show odds + timeline with `sports_match_timeline(match_id)`
   - **ended**: Show final result with `sports_matches_final_result(data={{"match_ids": [match_id]}})`
     and settlement status with `settlement_match_stats(match_ids=[match_id])`

4. **Optional extras**:
   - Tickets on this match: `sports_fixture_tickets(match_id)`
   - Provider results: `sports_match_providers_result(match_id)`
"""
