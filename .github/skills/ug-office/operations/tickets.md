# Ticket Operations

Search, inspect, and manage betting tickets using MCP tools.

## Step 1 — Find tickets

Choose the right approach based on what the user needs:

| User says | Tool to use |
|-----------|-------------|
| "Find ticket #123" | `ticket_get(ticket_id=123)` |
| "Search tickets for today" | `ticket_search(data={"date_from": "<today>", "date_to": "<today>"})` |
| "Tickets for match X" | `ticket_search(data={"match_id": <id>})` |
| "Member's tickets" | `ticket_search(data={"member_id": <id>})` |
| "Recent tickets" | `ticket_list(page=1, limit=50)` |
| "Tickets on this match" | `sports_fixture_tickets(match_id=<id>)` |

## Step 2 — Inspect ticket details

For a single ticket: `ticket_get(ticket_id=<id>)`

Additional detail tools:
- `ticket_status_history(data={"ticket_id": <id>})` — chronological status changes
- `ticket_query_nt(data={"ticket_id": <id>})` — notification/transaction records
- `ticket_query_insurance(data={"ticket_id": <id>})` — insurance details

## Step 3 — Present results

1. Show ticket ID, member, match, status, stake, and potential payout
2. For search results, summarize count and key fields
3. Format currency with 2 decimals and commas

## Available tools

### Searching & listing

| Tool | Purpose |
|------|---------|
| `ticket_list(page, limit)` | Paginated list of all tickets |
| `ticket_search(data)` | Search with filters (date, member, match, status, sport) |
| `ticket_get(ticket_id)` | Single ticket by ID |
| `ticket_outrights(data)` | Outright/futures tickets |
| `ticket_cashout()` | Tickets eligible for cashout |

### Status management

| Tool | Purpose | Safety |
|------|---------|--------|
| `ticket_force_status(data)` | Override ticket status | ⚠️ Destructive — confirm first |
| `ticket_reset_status(data)` | Revert to default status | ⚠️ Destructive — confirm first |
| `ticket_confirmation(data)` | Confirm a pending ticket | ⚠️ Destructive — triggers acceptance |
| `ticket_trigger_reject_event(match_id)` | Reject pending tickets for match | ⚠️ Destructive — confirm first |

### Ticket history & metadata

| Tool | Purpose |
|------|---------|
| `ticket_status_history(data)` | Status change timeline |
| `ticket_query_nt(data)` | Notification/transaction records |
| `ticket_notification_history()` | Global notification history |
| `ticket_calculate_totals()` | Aggregate ticket totals |

### Insurance

| Tool | Purpose |
|------|---------|
| `ticket_query_insurance(data)` | Query insurance for tickets |
| `ticket_request_insurance(data)` | Request insurance on a ticket |

### Pause controls

| Tool | Purpose |
|------|---------|
| `ticket_pause_global()` | Check global pause status |
| `ticket_pause_sports()` | Pause status by sport |
| `ticket_pause_by_match(match_id)` | Pause status for a match |
| `ticket_pause_update(data)` | Enable/disable ticket pause |

## When to use force_status vs reset_status

- **`ticket_force_status`**: Override to a *specific* status (e.g., force a ticket to "void" or "settled")
- **`ticket_reset_status`**: Revert to the ticket's *natural/default* status (undo a forced status)

## Example workflows

### "Show today's tickets"

1. `ticket_search(data={"date_from": "<today>", "date_to": "<today>"})`
2. Present ticket count, total stake, and status breakdown

### "Void ticket #456"

1. `ticket_get(ticket_id=456)` — confirm ticket exists and current status
2. Confirm with user: "Ticket #456 is currently [status]. Void it?"
3. `ticket_force_status(data={"ticket_id": 456, "status": "void"})`

### "Pause betting on match #789"

1. `ticket_pause_by_match(match_id=789)` — check current state
2. `ticket_pause_update(data={"enabled": true, "match_id": 789})`
