---
name: ug-office
description: UG Office sportsbook back-office operations — win/loss reports, odds queries, turnover, margins, P&L. Use when the user asks about winloss, turnover, margins, profit/loss, odds, lines, handicap, over/under, or any sports betting operational data.
---

# UG Office

Interact with the UG Office Admin back office (https://www.ugoffice.com) to answer operational questions about sports betting data.

## Prerequisites

This skill requires the **ug-office MCP server** to be running. The MCP server provides the tools (API calls), and this skill provides the knowledge (how to use them effectively).

Install the MCP server by adding it to your AI tool's config:

```json
{
  "mcpServers": {
    "ug-office": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ug-office-ai/mcp", "ug-office-mcp"],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "UG_OFFICE_URL": "https://www.ugoffice.com",
        "UG_USERNAME": "YOUR_USERNAME",
        "UG_PASSWORD": "YOUR_PASSWORD"
      }
    }
  }
}
```

See `claude_desktop_config.example.json` in the project root for a full example.

## MCP tools (preferred)

Use MCP tools for structured data. Read the relevant operation guide for step-by-step instructions:

| Topic | Guide | When to use |
|-------|-------|-------------|
| Win/Loss | [operations/winloss.md](operations/winloss.md) | Winloss, turnover, margins, payout, currency/vendor/date P&L |
| Odds | [operations/odds.md](operations/odds.md) | Current odds, odds history, match search, markets |
| Tickets | [operations/tickets.md](operations/tickets.md) | Ticket search, status, void, pause, insurance, cashout |
| Settlement | [operations/settlement.md](operations/settlement.md) | Resolve, hold/unhold, freeze, recovery, settlement history |

### Other domains (use MCP tools directly)

These domains have MCP tools available but no detailed guide yet. Use the tool docstrings for parameter info.

| Domain | Key tools | When to use |
|--------|-----------|-------------|
| Operators | `operator_list`, `operator_get`, `operator_config`, `operator_update` | Operator CRUD, config, currencies, packages |
| Members | `member_list`, `vendor_list`, `member_tree_list` | Member/vendor lookups, vendor rewards |
| System | `user_list`, `role_list`, `permission_list`, `auth_settings` | User management, roles, permissions, auth |
| Reports | `report_winloss`, `report_total_bet`, `report_odds_performance` | Win/loss, total bet, odds performance reports |

## Browser fallback

When MCP tools fail or a visual screenshot is needed, use playwright-cli. See [browser.md](browser.md) for session management and login instructions.
