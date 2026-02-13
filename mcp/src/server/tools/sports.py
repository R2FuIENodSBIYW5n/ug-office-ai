"""Sports tools — fixtures, matches, odds, tournaments, competitors, markets."""

from __future__ import annotations

from typing import Any

from fastmcp import Context, FastMCP
from returns.result import Failure, Success

from ._helpers import get_client, get_socketio, sanitize_error

PREFIX = "/1.0/sports"


def register(mcp: FastMCP) -> None:

    # --- Core lookups ---

    @mcp.tool
    async def sports_list(ctx: Context = None) -> dict | list:
        """List all sports.

        Returns API response with all available sports.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_get(sport_id: int, ctx: Context = None) -> dict | list:
        """Get a single sport by ID.

        Args:
            sport_id: Internal sport identifier.

        Returns API response with sport details.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/{sport_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_update(sport_id: int, data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Update a sport.

        Modifies sport configuration. Changes are visible to operators immediately.

        Args:
            sport_id: Internal sport identifier.
            data: Sport fields to update (e.g. name, status, settings).

        Returns API response with updated sport.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/{sport_id}", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_maps(ctx: Context = None) -> dict | list:
        """Get sport mapping data.

        Returns API response with provider-to-internal sport mappings.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/maps"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_groups(ctx: Context = None) -> dict | list:
        """Get sport groups.

        Returns API response with sport group definitions.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/groups"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Tournaments ---

    @mcp.tool
    async def sports_tournaments(sport_id: int | None = None, ctx: Context = None) -> dict | list:
        """List tournaments, optionally filtered by sport.

        Args:
            sport_id: Filter by sport identifier. If None, returns all tournaments.

        Returns API response with tournament list.
        """
        params = {}
        if sport_id is not None:
            params["sport_id"] = sport_id
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/tournaments", params=params):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_tournaments_by_ids(
        tournament_ids: list[int], ctx: Context = None
    ) -> dict | list:
        """Get tournaments by IDs.

        Args:
            tournament_ids: List of internal tournament identifiers.

        Returns API response with matching tournaments.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/tournaments", json={"ids": tournament_ids}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_tournament_get(tournament_id: int, ctx: Context = None) -> dict | list:
        """Get a single tournament.

        Args:
            tournament_id: Internal tournament identifier.

        Returns API response with tournament details.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/tournaments/{tournament_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_tournament_update(
        tournament_id: int, data: dict, ctx: Context = None
    ) -> dict | list:
        """[WRITE] Update a tournament.

        Modifies tournament configuration. Changes affect tournament display and settings.

        Args:
            tournament_id: Internal tournament identifier.
            data: Tournament fields to update (e.g. name, sport_id, status).

        Returns API response with updated tournament.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/tournaments/{tournament_id}", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_tournaments_update(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Bulk update tournaments.

        Modifies multiple tournaments in a single request. Changes are applied immediately.

        Args:
            data: Batch update payload.

                Data keys:
                  - tournaments (list[dict], required): Each dict should contain tournament_id and fields to update.

        Returns API response with update results.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/tournaments", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_tournament_priority(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Update tournament priority.

        Changes tournament display ordering. Affects how tournaments are sorted in listings.

        Args:
            data: Priority assignment payload.

                Data keys:
                  - tournament_id (int, required): Tournament to update.
                  - priority (int, required): New priority value (lower = higher priority).

        Returns API response confirming priority update.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/tournaments/priority", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_tournament_create(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Create a new tournament.

        Creates a new tournament record in the system.

        Args:
            data: Tournament definition.

                Data keys:
                  - name (str, required): Tournament name.
                  - sport_id (int, required): Sport this tournament belongs to.
                  - status (str, optional): Initial status.

        Returns API response with created tournament.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/tournament/create", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_tournament_competitors(tournament_id: int, ctx: Context = None) -> dict | list:
        """Get competitors in a tournament.

        Args:
            tournament_id: Internal tournament identifier.

        Returns API response with competitor list for the tournament.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/tournament/{tournament_id}/competitors"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_tournament_matches(tournament_id: int, ctx: Context = None) -> dict | list:
        """Get matches in a tournament.

        Args:
            tournament_id: Internal tournament identifier.

        Returns API response with match list for the tournament.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/tournament/{tournament_id}/matches"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_tournaments_today(ctx: Context = None) -> dict | list:
        """Get tournaments playing today.

        Returns API response with tournaments that have matches scheduled today.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/tournaments/today"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_tournament_map(tournament_id: int, ctx: Context = None) -> dict | list:
        """Get provider mappings for a tournament.

        Args:
            tournament_id: Internal tournament identifier.

        Returns API response with external provider mapping entries.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/tournaments/{tournament_id}/map"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_tournament_map_remove(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Remove a tournament provider mapping.

        Deletes the link between an internal tournament and an external provider ID.

        Args:
            data: Mapping to remove.

                Data keys:
                  - tournament_id (int, required): Internal tournament ID.
                  - provider (str, required): Provider name.
                  - provider_id (str, required): Provider's tournament ID.

        Returns API response confirming mapping removal.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/tournament-map/remove", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_tournament_map_assign(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Assign a tournament provider mapping.

        Creates a link between an internal tournament and an external provider ID.

        Args:
            data: Mapping to assign.

                Data keys:
                  - tournament_id (int, required): Internal tournament ID.
                  - provider (str, required): Provider name.
                  - provider_id (str, required): Provider's tournament ID.

        Returns API response confirming mapping assignment.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/tournament-map/assign", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Competitors ---

    @mcp.tool
    async def sports_competitors(sport_id: int | None = None, ctx: Context = None) -> dict | list:
        """List competitors, optionally filtered by sport.

        Args:
            sport_id: Filter by sport identifier. If None, returns all competitors.

        Returns API response with competitor list.
        """
        params = {}
        if sport_id is not None:
            params["sport_id"] = sport_id
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/competitors", params=params):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_competitors_by_ids(
        competitor_ids: list[int], ctx: Context = None
    ) -> dict | list:
        """Get competitors by IDs.

        Args:
            competitor_ids: List of internal competitor identifiers.

        Returns API response with matching competitors.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/competitors", json={"ids": competitor_ids}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_competitor_get(competitor_id: int, ctx: Context = None) -> dict | list:
        """Get a single competitor.

        Args:
            competitor_id: Internal competitor identifier.

        Returns API response with competitor details.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/competitors/{competitor_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_competitor_update(
        competitor_id: int, data: dict, ctx: Context = None
    ) -> dict | list:
        """[WRITE] Update a competitor.

        Modifies competitor configuration. Changes affect competitor display and settings.

        Args:
            competitor_id: Internal competitor identifier.
            data: Competitor fields to update (e.g. name, sport_id, status).

        Returns API response with updated competitor.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/competitors/{competitor_id}", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_competitors_update(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Bulk update competitors.

        Modifies multiple competitors in a single request. Changes are applied immediately.

        Args:
            data: Batch update payload.

                Data keys:
                  - competitors (list[dict], required): Each dict should contain competitor_id and fields to update.

        Returns API response with update results.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/competitors", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_competitor_create(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Create a competitor.

        Creates a new competitor record in the system.

        Args:
            data: Competitor definition.

                Data keys:
                  - name (str, required): Competitor name.
                  - sport_id (int, required): Sport this competitor belongs to.

        Returns API response with created competitor.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/competitor/create", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_competitor_tournaments(competitor_id: int, ctx: Context = None) -> dict | list:
        """Get tournaments for a competitor.

        Args:
            competitor_id: Internal competitor identifier.

        Returns API response with tournaments the competitor participates in.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(
                    f"{PREFIX}/competitor/tournaments", json={"competitor_id": competitor_id}
                ):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_competitor_matches(competitor_id: int, ctx: Context = None) -> dict | list:
        """Get matches for a competitor.

        Args:
            competitor_id: Internal competitor identifier.

        Returns API response with matches involving the competitor.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/competitor/{competitor_id}/matches"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_competitor_map(competitor_id: int, ctx: Context = None) -> dict | list:
        """Get provider mappings for a competitor.

        Args:
            competitor_id: Internal competitor identifier.

        Returns API response with external provider mapping entries.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/competitors/{competitor_id}/map"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_competitor_map_remove(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Remove a competitor provider mapping.

        Deletes the link between an internal competitor and an external provider ID.

        Args:
            data: Mapping to remove.

                Data keys:
                  - competitor_id (int, required): Internal competitor ID.
                  - provider (str, required): Provider name.
                  - provider_id (str, required): Provider's competitor ID.

        Returns API response confirming mapping removal.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/competitor-map/remove", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_competitor_map_assign(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Assign a competitor provider mapping.

        Creates a link between an internal competitor and an external provider ID.

        Args:
            data: Mapping to assign.

                Data keys:
                  - competitor_id (int, required): Internal competitor ID.
                  - provider (str, required): Provider name.
                  - provider_id (str, required): Provider's competitor ID.

        Returns API response confirming mapping assignment.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/competitor-map/assign", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Markets ---

    @mcp.tool
    async def sports_markets(sport_id: int | None = None, ctx: Context = None) -> dict | list:
        """List markets, optionally filtered by sport.

        Args:
            sport_id: Filter by sport identifier. If None, returns all markets.

        Returns API response with market list.
        """
        params = {}
        if sport_id is not None:
            params["sport_id"] = sport_id
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/markets", params=params):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_markets_all(ctx: Context = None) -> dict | list:
        """List all markets across all sports.

        Returns API response with every market regardless of sport.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/markets-all"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_markets_by_ids(market_ids: list[int], ctx: Context = None) -> dict | list:
        """Get markets by IDs.

        Args:
            market_ids: List of internal market identifiers.

        Returns API response with matching markets.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/markets", json={"ids": market_ids}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_market_get(market_id: int, ctx: Context = None) -> dict | list:
        """Get a single market.

        Args:
            market_id: Internal market identifier.

        Returns API response with market details.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/markets/{market_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_market_update(market_id: int, data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Update a market.

        Modifies market configuration. Changes affect market display and behavior.

        Args:
            market_id: Internal market identifier.
            data: Market fields to update (e.g. name, type_id, status).

        Returns API response with updated market.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/markets/{market_id}", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_market_outcomes(market_id: int, ctx: Context = None) -> dict | list:
        """Get outcomes for a market.

        Args:
            market_id: Internal market identifier.

        Returns API response with possible outcomes for the market.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/markets/{market_id}/outcomes"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_market_types(ctx: Context = None) -> dict | list:
        """List market types.

        Returns API response with all available market type definitions.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/markets/types"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_market_type_get(type_id: int, ctx: Context = None) -> dict | list:
        """Get a market type.

        Args:
            type_id: Internal market type identifier.

        Returns API response with market type details.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/markets/types/{type_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_market_type_update(
        type_id: int, data: dict, ctx: Context = None
    ) -> dict | list:
        """[WRITE] Update a market type.

        Modifies market type configuration. Changes affect all markets of this type.

        Args:
            type_id: Internal market type identifier.
            data: Market type fields to update (e.g. name, settings).

        Returns API response with updated market type.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/markets/types/{type_id}", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_market_cases(market_type_id: int, ctx: Context = None) -> dict | list:
        """Get market cases by type.

        Args:
            market_type_id: Internal market type identifier.

        Returns API response with case definitions for the market type.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/markets/{market_type_id}/cases"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_markets_requirement(data: dict, ctx: Context = None) -> dict | list:
        """Get markets requirement.

        Args:
            data: Filter criteria.

                Data keys:
                  - sport_id (int, optional): Filter by sport.
                  - market_ids (list[int], optional): Specific markets to check.

        Returns API response with market requirement data.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/markets-requirement", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Fixtures / Matches ---

    @mcp.tool
    async def sports_fixtures(
        sport_id: int | None = None,
        page: int = 1,
        limit: int = 50,
        ctx: Context = None,
    ) -> dict | list:
        """List fixtures with pagination.

        Args:
            sport_id: Filter by sport identifier. If None, returns all sports.
            page: Page number (1-based).
            limit: Maximum number of fixtures per page.

        Returns API response with paginated fixture list.
        """
        params: dict[str, Any] = {"page": page, "limit": limit}
        if sport_id is not None:
            params["sport_id"] = sport_id
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/fixtures", params=params):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_fixtures_post(data: dict, ctx: Context = None) -> dict | list:
        """Query fixtures with filters.

        Args:
            data: Filter criteria.

                Data keys:
                  - sport_id (int, optional): Filter by sport.
                  - date_from (str, optional): Start date YYYY-MM-DD.
                  - date_to (str, optional): End date YYYY-MM-DD.
                  - status (str, optional): e.g. 'prematch', 'live', 'ended'.
                  - tournament_id (int, optional): Filter by tournament.

        Returns API response with matching fixtures.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/fixtures", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_fixtures_incoming(ctx: Context = None) -> dict | list:
        """Get upcoming/incoming fixtures.

        Returns API response with fixtures scheduled in the near future.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/fixtures/incoming"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_fixture_tickets(match_id: int, ctx: Context = None) -> dict | list:
        """Get tickets for a fixture/match.

        Args:
            match_id: Internal match identifier.

        Returns API response with tickets placed on the fixture.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/fixtures/{match_id}/tickets"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_fixture_map_log(ctx: Context = None) -> dict | list:
        """Get fixture map log.

        Returns API response with fixture mapping change history.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/fixtures/map-log"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_fixture_market_price(
        match_id: int, market_id: int, ctx: Context = None
    ) -> dict | list:
        """Get market price for a fixture.

        Args:
            match_id: Internal match identifier.
            market_id: Internal market identifier.

        Returns API response with current price for the market on the fixture.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/fixtures/{match_id}/market/{market_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_matches_by_ids(match_ids: list[int], ctx: Context = None) -> dict | list:
        """Get matches by IDs.

        Args:
            match_ids: List of internal match identifiers.

        Returns API response with matching match records.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/matches-by-ids", json={"ids": match_ids}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_matches(data: dict, ctx: Context = None) -> dict | list:
        """Query matches with filters.

        Args:
            data: Filter criteria.

                Data keys:
                  - sport_id (int, optional): Filter by sport.
                  - tournament_id (int, optional): Filter by tournament.
                  - date_from (str, optional): Start date YYYY-MM-DD.
                  - date_to (str, optional): End date YYYY-MM-DD.
                  - status (str, optional): e.g. 'prematch', 'live', 'ended'.

        Returns API response with matching matches.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/matches", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_matches_search(
        keyword: str,
        status: str = "",
        ctx: Context = None,
    ) -> dict | list:
        """Search matches by team/tournament name.

        Fetches all matches and filters client-side by keyword.
        Use this instead of sports_matches when looking for a specific team.

        Args:
            keyword: Text to search for in competitor or tournament names (case-insensitive).
            status: Optional status filter (e.g. 'prematch', 'live', 'ended'). Filters client-side.

        Returns matching matches (max 50).
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/matches", json={}):
                    case Failure(err):
                        return err.model_dump()
                    case Success(data):
                        all_matches = (
                            data.get("data", {}).get("matches", [])
                            if isinstance(data, dict)
                            else data
                        )
                        kw = keyword.lower()
                        hits = []
                        for m in all_matches:
                            if not isinstance(m, dict):
                                continue
                            text = f"{m.get('en_competitor_1', '')} {m.get('en_competitor_2', '')} {m.get('en_tournament', '')}".lower()
                            if kw not in text:
                                continue
                            if status and m.get("status") != status:
                                continue
                            hits.append({
                                "match_id": m.get("match_id"),
                                "en_competitor_1": m.get("en_competitor_1"),
                                "en_competitor_2": m.get("en_competitor_2"),
                                "en_tournament": m.get("en_tournament"),
                                "start_time": m.get("start_time"),
                                "status": m.get("status"),
                            })
                            if len(hits) >= 50:
                                break
                        return {"matches": hits, "total_hits": len(hits)}

    @mcp.tool
    async def sports_match_get(match_id: int, ctx: Context = None) -> dict | list:
        """Get a single match by ID.

        Args:
            match_id: Internal match identifier.

        Returns API response with match details.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/matches/{match_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_update(match_id: int, data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Update a match.

        Modifies match state (status, result, etc.). Changes take effect
        immediately. For scheduling changes only, prefer sports_match_update_schedule.

        Args:
            match_id: Internal match identifier.
            data: Match fields to update (e.g. status, start_time, result).

        Returns API response with updated match.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/matches/{match_id}", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_publish(match_id: int, ctx: Context = None) -> dict | list:
        """[DESTRUCTIVE] Publish a match, making it visible to end users.

        Makes the match live and visible to bettors. Affects live trading.

        Args:
            match_id: Internal match identifier.

        Returns API response confirming publication.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/matches/{match_id}/publish", json={}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_unpublish(match_id: int, ctx: Context = None) -> dict | list:
        """[DESTRUCTIVE] Unpublish a match, hiding it from end users.

        Removes the match from public view. Affects live trading.

        Args:
            match_id: Internal match identifier.

        Returns API response confirming unpublication.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/matches/{match_id}/unpublish", json={}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_providers_result(match_id: int, ctx: Context = None) -> dict | list:
        """Get provider results for a match.

        Args:
            match_id: Internal match identifier.

        Returns API response with results reported by external providers.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/matches/{match_id}/providers-result"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_settlement_ticket_void_spec(
        match_id: int, ctx: Context = None
    ) -> dict | list:
        """Get settlement and ticket data to void by spec for a match.

        Read-only but used to prepare void operations. Review results carefully before voiding.

        Args:
            match_id: Internal match identifier.

        Returns API response with settlement and void-eligible ticket data.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                url = f"{PREFIX}/matches/{match_id}/settlement-ticket-to-void-by-spec"
                match await client.get(url):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_matches_confirmed_ticket(data: dict, ctx: Context = None) -> dict | list:
        """Get confirmed tickets for matches.

        Args:
            data: Filter criteria.

                Data keys:
                  - match_ids (list[int], optional): Match IDs to query.
                  - date_from (str, optional): Start date YYYY-MM-DD.
                  - date_to (str, optional): End date YYYY-MM-DD.

        Returns API response with confirmed ticket records.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/matches/confirmed-ticket", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_timeline(match_id: int, ctx: Context = None) -> dict | list:
        """Get match timeline.

        Args:
            match_id: Internal match identifier.

        Returns API response with chronological match events.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/matches/{match_id}/timeline"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_matches_final_result(data: dict, ctx: Context = None) -> dict | list:
        """Get final results for matches.

        Args:
            data: Filter criteria.

                Data keys:
                  - match_ids (list[int], required): Match IDs to query.

        Returns API response with final result data.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/matches/final-result", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_competitors_translate(ctx: Context = None) -> dict | list:
        """Get competitor translations for matches.

        Returns API response with translated competitor names.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/matches/competitors-translate"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_tournaments_translate(ctx: Context = None) -> dict | list:
        """Get tournament translations for matches.

        Returns API response with translated tournament names.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/matches/tournaments-translate"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_refresh_translation(
        match_id: int, ctx: Context = None
    ) -> dict | list:
        """[WRITE] Refresh translations for a match.

        Triggers a re-fetch of translations from providers. Updates displayed names.

        Args:
            match_id: Internal match identifier.

        Returns API response confirming translation refresh.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                url = f"{PREFIX}/matches/{match_id}/refresh-translation"
                match await client.post(url, json={}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Match detail endpoints ---

    @mcp.tool
    async def sports_match_markets(match_id: int, ctx: Context = None) -> dict | list:
        """Get markets for a match.

        Args:
            match_id: Internal match identifier.

        Returns API response with available markets for the match.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/match/{match_id}/markets"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_keep_alive(match_id: int, ctx: Context = None) -> dict | list:
        """Send keep-alive for a match.

        Args:
            match_id: Internal match identifier.

        Returns API response confirming keep-alive signal.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/match/{match_id}/keep-alive"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_odds(
        match_id: int,
        market_ids: list[int] | None = None,
        ctx: Context = None,
    ) -> dict | list:
        """Get current odds for a match via Socket.IO.

        Args:
            match_id: Internal match identifier.
            market_ids: Market IDs to query. Defaults to [101001, 102001, 101011, 102011]
                (FT Handicap, FT O/U, 1H Handicap, 1H O/U).

        Returns current odds data for the match.
        """
        match await get_socketio(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(mgr):
                if not mgr.connected:
                    return {"error": "socketio_disconnected", "detail": "Socket.IO not connected"}
                if market_ids is None:
                    market_ids = [101001, 102001, 101011, 102011]
                try:
                    return await mgr.get_odds(match_id, market_ids)
                except Exception as exc:
                    return sanitize_error("sports_match_odds", exc)

    @mcp.tool
    async def sports_match_update_schedule(
        match_id: int, data: dict, ctx: Context = None
    ) -> dict | list:
        """[WRITE] Update a scheduled match.

        Modifies match schedule details such as start time or venue.

        Args:
            match_id: Internal match identifier.
            data: Schedule fields to update.

                Data keys:
                  - start_time (str, optional): New start time (ISO 8601).
                  - venue (str, optional): Venue name.

                Note: Use this for scheduling changes. Use sports_match_update for general field updates (status, result).

        Returns API response with updated match schedule.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/match/{match_id}", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_update_tournaments(
        match_id: int, data: dict, ctx: Context = None
    ) -> dict | list:
        """[WRITE] Update tournaments for a match.

        Changes which tournaments a match is associated with.

        Args:
            match_id: Internal match identifier.
            data: Tournament reassignment.

                Data keys:
                  - tournament_ids (list[int], required): Tournament IDs to associate.

        Returns API response with updated tournament assignments.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/match-tournaments/{match_id}", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_update_competitors(
        match_id: int, data: dict, ctx: Context = None
    ) -> dict | list:
        """[WRITE] Update competitors for a match.

        Changes which competitors are assigned to a match (home/away).

        Args:
            match_id: Internal match identifier.
            data: Competitor reassignment.

                Data keys:
                  - competitor_ids (list[int], required): Competitor IDs.
                  - home (int, optional): Home competitor ID.
                  - away (int, optional): Away competitor ID.

        Returns API response with updated competitor assignments.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/match-competitors/{match_id}", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_close(match_id: int, ctx: Context = None) -> dict | list:
        """[DESTRUCTIVE] Close a match, preventing further updates.

        Permanently closes the match. No further odds or result changes
        are possible after this action.

        Args:
            match_id: Internal match identifier.

        Returns API response confirming match closure.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/match/{match_id}/match-close", json={}):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_order_get(match_id: int, ctx: Context = None) -> dict | list:
        """Get match display order.

        Args:
            match_id: Internal match identifier.

        Returns API response with current ordering position.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/match/{match_id}/order"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_order_update(
        match_id: int, data: dict, ctx: Context = None
    ) -> dict | list:
        """[WRITE] Update match display order.

        Changes the display position of a match in listings.

        Args:
            match_id: Internal match identifier.
            data: Ordering fields.

                Data keys:
                  - position (int, optional): Display position.
                  - sort_key (int, optional): Sort key value.

        Returns API response with updated ordering.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.put(f"{PREFIX}/match/{match_id}/order", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_odds_markets(match_id: int, ctx: Context = None) -> dict | list:
        """Get odds markets for a match.

        Note: This endpoint may return 404. Use sports_match_odds instead.

        Args:
            match_id: Internal match identifier.

        Returns API response with markets that have odds for the match.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/match/{match_id}/odds-markets"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_match_attributes_priority(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Update match attributes priority.

        Changes attribute priority ordering for match display and processing.

        Args:
            data: Priority settings.

                Data keys:
                  - match_id (int, required): Target match.
                  - priorities (dict, required): Attribute-to-priority mappings.

        Returns API response confirming priority update.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/match-attributes-priority", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Odds ---

    @mcp.tool
    async def sports_odds_refresh(match_id: int, ctx: Context = None) -> dict | list:
        """[WRITE] Refresh odds for a match.

        Triggers a re-fetch of odds from providers. May update displayed odds values.

        Args:
            match_id: Internal match identifier.

        Returns API response confirming odds refresh.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/odds/refresh/{match_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_odds_get(odds_id: int, ctx: Context = None) -> dict | list:
        """Get odds by ID.

        Args:
            odds_id: Internal odds identifier.

        Returns API response with odds details.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/odds/{odds_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_odds_outcomes(odds_id: int, ctx: Context = None) -> dict | list:
        """Get outcomes for an odds entry.

        Args:
            odds_id: Internal odds identifier.

        Returns API response with possible outcomes and their values.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/odds/{odds_id}/outcomes"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_odds_cases(odds_id: int, ctx: Context = None) -> dict | list:
        """Get cases for an odds entry.

        Args:
            odds_id: Internal odds identifier.

        Returns API response with case definitions for the odds.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/odds/{odds_id}/cases"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_odds_info(odds_id: int, ctx: Context = None) -> dict | list:
        """Get odds info.

        Args:
            odds_id: Internal odds identifier.

        Returns API response with detailed odds information.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/odds-info/{odds_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_odds_line(match_id: int, market_id: int, ctx: Context = None) -> dict | list:
        """Get odds line for a match and market.

        Note: This endpoint may return 404. Use sports_match_odds for live odds
        or sports_odds_history for historical data instead.

        Args:
            match_id: Internal match identifier.
            market_id: Internal market identifier.

        Returns API response with the odds line.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/odds-line/{match_id}/{market_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_odds_line_matches(data: dict, ctx: Context = None) -> dict | list:
        """Get odds lines for multiple matches.

        Args:
            data: Query payload.

                Data keys:
                  - match_ids (list[int], required): Matches to query.
                  - market_ids (list[int], optional): Markets to include.

        Returns API response with odds lines per match.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/odds-line/matches", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_odds_line_matches_exists(data: dict, ctx: Context = None) -> dict | list:
        """Check if matches have odds lines.

        Args:
            data: Query payload.

                Data keys:
                  - match_ids (list[int], required): Matches to check.

        Returns API response with existence flags per match.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/odds-line/matches/exists", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_odds_history_matches(data: dict, ctx: Context = None) -> dict | list:
        """Get odds history for matches.

        Args:
            data: Query payload.

                Data keys:
                  - match_ids (list[int], required): Matches to query.
                  - market_ids (list[int], optional): Filter by markets.
                  - date_from (str, optional): Start date YYYY-MM-DD.
                  - date_to (str, optional): End date YYYY-MM-DD.

        Returns API response with historical odds data.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/odds-history-matches", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_odds_history(data: dict, ctx: Context = None) -> dict | list:
        """Get odds history.

        Args:
            data: Query payload.

                Data keys:
                  - odds_id (int, required): The odds entry to query history for.
                  - date_from (str, optional): Start date YYYY-MM-DD.
                  - date_to (str, optional): End date YYYY-MM-DD.

        Returns API response with historical odds data.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/odds-history", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_odds_history_raw(data: dict, ctx: Context = None) -> dict | list:
        """Get raw (unprocessed) odds history. Use this for debugging or when you need
        provider-level detail. For normal odds history, prefer sports_odds_history.

        Args:
            data: Query payload.

                Data keys:
                  - odds_id (int, required): The odds entry to query.
                  - date_from (str, optional): Start date YYYY-MM-DD.
                  - date_to (str, optional): End date YYYY-MM-DD.

        Returns API response with unprocessed historical odds data.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/odds-history-raw", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_odds_history_raw_providers(data: dict, ctx: Context = None) -> dict | list:
        """Get raw odds history broken down by provider. Use this to compare how
        different providers reported odds. For normal odds history, prefer sports_odds_history.

        Args:
            data: Query payload.

                Data keys:
                  - odds_id (int, required): The odds entry to query.
                  - provider (str, optional): Filter to a specific provider.
                  - date_from (str, optional): Start date YYYY-MM-DD.
                  - date_to (str, optional): End date YYYY-MM-DD.

        Returns API response with unprocessed provider-specific odds history.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/odds-history-raw/providers", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Per-bet properties ---

    @mcp.tool
    async def sports_per_bet_properties(id: int, ctx: Context = None) -> dict | list:
        """Get per-bet properties.

        Args:
            id: Internal per-bet properties identifier.

        Returns API response with per-bet property configuration.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/per-bet-properties/{id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Official logs ---

    @mcp.tool
    async def sports_official_logs(match_id: int, ctx: Context = None) -> dict | list:
        """Get official match logs.

        Args:
            match_id: Internal match identifier.

        Returns API response with official log entries for the match.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.get(f"{PREFIX}/official/logs/{match_id}"):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_official_logs_providers(
        match_id: int, data: dict, ctx: Context = None
    ) -> dict | list:
        """Get official match logs by providers.

        Args:
            match_id: Internal match identifier.
            data: Provider filter.

                Data keys:
                  - providers (list[str], optional): Provider names to filter by.

        Returns API response with provider-specific official log entries.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                url = f"{PREFIX}/official/logs/{match_id}/providers"
                match await client.post(url, json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    # --- Custom match & mapping ---

    @mcp.tool
    async def sports_custom_match_create(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Create a custom match.

        Creates a new manually-defined match in the system.

        Args:
            data: Custom match definition.

                Data keys:
                  - sport_id (int, required): Sport for the match.
                  - competitor_1 (str, required): Home team name.
                  - competitor_2 (str, required): Away team name.
                  - start_time (str, required): Start time (ISO 8601).
                  - tournament_id (int, optional): Tournament to place match in.
                  - markets (list[int], optional): Market IDs to enable.

        Returns API response with created custom match.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/custom-match", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()

    @mcp.tool
    async def sports_tournament_grouping(data: dict, ctx: Context = None) -> dict | list:
        """[WRITE] Group tournaments.

        Assigns tournaments to a group, affecting how they are organized in listings.

        Args:
            data: Grouping definition.

                Data keys:
                  - tournament_ids (list[int], required): Tournaments to group.
                  - group_name (str, required): Name for the group.

        Returns API response confirming tournament grouping.
        """
        match await get_client(ctx):
            case Failure(err):
                return err.model_dump()
            case Success(client):
                match await client.post(f"{PREFIX}/tournaments/group", json=data):
                    case Success(data):
                        return data
                    case Failure(err):
                        return err.model_dump()
