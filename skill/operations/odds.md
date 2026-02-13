# Odds Queries

Query current match odds, markets, and odds history using MCP tools (no browser needed).

## How odds work

- **Live/current odds** are served via Socket.IO. The `sports_match_odds` tool uses Socket.IO internally.
- **Odds history** is served via REST and works normally.
- Key market IDs: 101001 (FT Handicap), 102001 (FT Over/Under), 101011 (1H Handicap), 102011 (1H Over/Under)

## Step 1 — Find the match

Choose the right tool based on what the user provides:

| User says | Tool to use |
|-----------|-------------|
| Team name (e.g., "Arsenal") | `sports_matches_search(keyword="Arsenal")` |
| "Today's matches" | `sports_tournaments_today()` → `sports_tournament_matches(tournament_id)` |
| Specific match ID | Skip to Step 2 |
| "Upcoming matches" | `sports_fixtures_incoming()` |

## Step 2 — Get odds

```
sports_match_odds(match_id=<id>)
```

Optionally specify markets: `sports_match_odds(match_id=<id>, market_ids=[101001, 102001])`

## Step 3 — Present odds to the user

Format as: **Tournament > Match (time, home vs away) > Markets**

For each market show:
- Market name (Handicap, Over/Under)
- Line/spread value
- Prices for each outcome

## Available tools

### Finding matches

| Tool | Args | Returns |
|------|------|---------|
| `sports_matches_search(keyword, status)` | `keyword: str`, `status: str` (optional) | **Best for finding a team** — max 50 results |
| `sports_tournaments_today()` | — | Tournaments with matches today |
| `sports_fixtures_incoming()` | — | All upcoming fixtures |
| `sports_tournament_matches(tournament_id)` | `tournament_id: int` | Matches in a tournament |
| `sports_match_get(match_id)` | `match_id: int` | Single match details |
| `sports_matches_by_ids(match_ids)` | `match_ids: list[int]` | Batch match lookup |

### Getting odds (live via Socket.IO)

| Tool | Status |
|------|--------|
| `sports_match_odds(match_id, market_ids)` | **Working** — primary tool for live odds |

### Known broken tools (do NOT use)

These tools return 404 errors and should not be called:

- `sports_match_odds_markets(match_id)` — use `sports_match_odds` instead
- `sports_odds_line(match_id, market_id)` — use `sports_match_odds` for live odds or `sports_odds_history` for historical data

### Odds history (REST, working)

| Tool | Args |
|------|------|
| `sports_odds_history(data)` | `data: {odds_id (required), date_from, date_to}` |
| `sports_odds_history_matches(data)` | `data: {match_ids (required), market_ids, date_from, date_to}` |
| `sports_odds_history_raw(data)` | Same as above — returns unprocessed data (for debugging) |
| `sports_odds_history_raw_providers(data)` | Same + `provider` filter — compare provider-level odds |

### Reference data

| Tool | Args |
|------|------|
| `sports_list()` | All sports (get sport IDs) |
| `sports_markets(sport_id)` | Markets for a sport |
| `sports_tournaments(sport_id)` | Tournaments for a sport |

## Example workflows

### "What are today's soccer odds?"

1. `sports_tournaments_today()` — get tournament list
2. Filter for soccer (verify sport_id with `sports_list()` if needed)
3. `sports_tournament_matches(tournament_id)` for relevant tournaments
4. `sports_match_odds(match_id)` for matches of interest
5. Present: tournament > match (time, home vs away) > Handicap, O/U lines

### "Show odds for Team A vs Team B"

1. `sports_matches_search(keyword="Team A")` — find match
2. Pick the relevant match from results
3. `sports_match_odds(match_id)` — get current odds
4. Present odds by market with line and prices

### "How have odds moved for this match?"

1. Get match_id (from prior search)
2. `sports_odds_history({"match_id": <id>})` — get history
3. Present as a timeline of odds changes

## Notes

- Odds expressions: malay (default), decimal, hongkong, indo
- Large fixture lists may hit token limits — filter by tournament first
- Socket.IO connects at startup using the same JWT credentials as REST
