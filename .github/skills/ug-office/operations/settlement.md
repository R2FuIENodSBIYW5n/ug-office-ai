# Settlement Operations

Manage bet settlement — resolving outcomes, holds, freezes, and recovery.

## Settlement lifecycle

```
Match ends → Result confirmed → Settlement resolved → Payouts processed
                                      ↓
                                 [Hold] → Review → [Unhold] → Payouts
                                      ↓
                                  [Freeze] (problematic tickets)
```

## Step 1 — Check settlement status

| User says | Tool to use |
|-----------|-------------|
| "Settlement for match X" | `settlement_history(match_id=<id>)` |
| "Incomplete settlements" | `settlement_incomplete_all()` |
| "Held settlements" | `settlement_hold_list()` |
| "Frozen tickets" | `settlement_freeze_tickets()` |
| "Settlement stats" | `settlement_match_stats(match_ids=[<ids>])` |

## Step 2 — Resolve settlements

All resolve tools are **destructive** — they trigger payouts. Always confirm with the user.

| Tool | When to use |
|------|-------------|
| `settlement_resolve_by_result(match_id)` | Standard: resolve all bets using the match's final result |
| `settlement_resolve(odds_id, outcome)` | Manual: resolve a single odds entry with a specific outcome |
| `settlement_resolve_by_incomplete_result(match_id)` | Partial: settle using incomplete results (use with caution) |
| `settlement_resolve_by_outright(outright_id)` | Outrights: settle outright/futures bets |
| `settlement_resolve_number_game(match_id)` | Number games: settle number game bets |

Outcome values for manual resolve: `"win"`, `"lose"`, `"void"`, `"half-win"`, `"half-lose"`

## Step 3 — Manage holds

Holds pause settlement processing for review. Use when results are disputed or need verification.

| Tool | Purpose | Safety |
|------|---------|--------|
| `settlement_hold(settlement_ids)` | Put settlements on hold | ⚠️ Blocks payouts |
| `settlement_unhold(settlement_ids)` | Release from hold | ⚠️ Triggers payouts |
| `settlement_hold_list()` | View held settlements | Read-only |
| `settlement_hold_details(settlement_id)` | Inspect a held settlement | Read-only |
| `settlement_task_hold_list()` | View held settlement tasks | Read-only |
| `settlement_unhold_task(task_id)` | Release a held task | ⚠️ Triggers processing |
| `settlement_ignore_task(task_id)` | Ignore a task (skip it) | ⚠️ Task won't be processed |

## Step 4 — Recovery & troubleshooting

| Tool | Purpose | Safety |
|------|---------|--------|
| `settlement_recovery_missing(match_id)` | Re-create missing settlements | ⚠️ May trigger payouts |
| `settlement_try_settle_ticket(ticket_id)` | Retry settling a specific ticket | ⚠️ May trigger payout |
| `settlement_check()` | System health check | Read-only |

## Other tools

| Tool | Purpose |
|------|---------|
| `settlement_list(page, limit)` | Paginated settlement list |
| `settlement_by_odds_ids(odds_ids)` | Look up by odds IDs |
| `settlement_by_outright(outright_id)` | Look up by outright event |
| `settlement_change_list(page, limit)` | Settlement change records |
| `settlement_change_log()` | Full change log |
| `settlement_notification_list(page, limit)` | Notification records |
| `settlement_notification_schedule(notification_id)` | Schedule a notification |
| `settlement_notification_cancel(notification_id)` | Cancel a notification |
| `settlement_notification_rollback(notification_id)` | ⚠️ Rollback a notification (reverses payouts) |

## Example workflows

### "Settle match #123"

1. `settlement_match_stats(match_ids=[123])` — check current settlement state
2. Confirm with user: "Match #123 has X unsettled bets. Resolve using final result?"
3. `settlement_resolve_by_result(match_id=123)`
4. `settlement_history(match_id=123)` — verify settlements processed

### "Hold settlement for disputed match"

1. `settlement_history(match_id=<id>)` — find settlement IDs
2. `settlement_hold(settlement_ids=[<ids>])` — place on hold
3. Inform user: "X settlements placed on hold. Review and unhold when ready."

### "Check incomplete settlements"

1. `settlement_incomplete_all()` — list all incomplete
2. Present: match name, sport, number of unsettled bets
3. For each, suggest `settlement_resolve_by_result` if result is available

### "Recover missing settlements for match"

1. Confirm with user: "This will re-create missing settlement records and may trigger payouts. Proceed?"
2. `settlement_recovery_missing(match_id=<id>)`
3. `settlement_match_stats(match_ids=[<id>])` — verify recovery
