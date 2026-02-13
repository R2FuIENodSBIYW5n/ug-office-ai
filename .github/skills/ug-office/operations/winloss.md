# Win/Loss Report

Use the `report_winloss` MCP tool to query win/loss data. It calls the UG Office API directly and computes the USD Total client-side.

## Step 1 — Determine parameters from the user's question

| Param | Required | Default | Description |
|-------|----------|---------|-------------|
| `date_from` | Yes | — | Start date `YYYY-MM-DD` |
| `date_to` | Yes | — | End date `YYYY-MM-DD` |
| `bet_type` | No | `"all"` | `"all"`, `"single"`, or `"parlay"` |
| `group_by` | No | `"currency_id"` | `"currency_id"`, `"vendor_id"`, `"group_id"`, `"date"` |
| `include_internal` | No | `false` | Include internal tickets |
| `page` | No | `1` | Page number (1-based) |
| `per_page` | No | `30` | Results per page |

Mapping user intent to parameters:
- "today's winloss" → `date_from=<today>`, `date_to=<today>`
- "by vendor" / "which vendor" → `group_by="vendor_id"`
- "by date" / "trend" / "this week" → `group_by="date"`
- "single bets" → `bet_type="single"`
- "parlay" → `bet_type="parlay"`

## Step 2 — Call the MCP tool

```
report_winloss(date_from="YYYY-MM-DD", date_to="YYYY-MM-DD", ...)
```

## Step 3 — Read the response

The response contains:

```json
{
  "data": [ ...rows... ],
  "usd_total": {
    "_summary": "USD TOTAL",
    "ticket": 4332,
    "net_turnover_usd": 146549.99,
    "net_winloss_usd": 13978.85,
    "margin_pct": -9.54,
    "stake_usd": ...,
    "payout_usd": ...,
    "winloss_usd": ...,
    "cashout_stake_usd": ...,
    "cashout_usd": ...,
    "cashout_winloss_usd": ...
  }
}
```

Key row fields:
- `ticket` — ticket count
- `net_turnover` / `to_usd_net_turnover` — net turnover (local / USD)
- `winloss` / `to_usd_winloss` — win/loss (positive = company profit)
- `net_winloss` / `to_usd_net_winloss` — net win/loss
- `payout` / `to_usd_payout` — payout
- `stake` / `to_usd_stake` — stake

## Step 4 — Present results to the user

1. **Lead with the USD total headline**: Net W/L, Margin %, Tickets, Net Turnover
2. **Then show the breakdown** (per-currency/vendor/group/date rows)
3. Format currency values with commas and 2 decimals (e.g., $13,978.85)
4. Format margin as percentage (e.g., -9.54%)
5. Positive `net_winloss` = company profit, negative = company loss

## Example workflows

### "What's today's winloss?"

1. `report_winloss(date_from="<today>", date_to="<today>")`
2. Report `usd_total.net_winloss_usd` and `usd_total.margin_pct` as headline
3. List per-currency breakdown from `data` rows

### "Winloss by vendor for this week"

1. `report_winloss(date_from="<monday>", date_to="<today>", group_by="vendor_id")`
2. Sort rows by `to_usd_net_winloss` to find best/worst vendors

### "Single bet vs parlay comparison"

1. Call twice with `bet_type="single"` and `bet_type="parlay"`
2. Compare `usd_total` from each response side-by-side

### "Winloss trend over the past week"

1. `report_winloss(date_from="<7 days ago>", date_to="<today>", group_by="date")`
2. Present as day-by-day breakdown

### Drill-down across dimensions

Change `group_by` to navigate: `currency_id` → `vendor_id` → `group_id` → `date`
