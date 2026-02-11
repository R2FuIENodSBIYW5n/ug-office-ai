# Win/Loss Report

Prereq: Follow session management steps in `skill/ugoffice.md` first.

**Page**: `/reports/winloss/all`

## Page layout

- **View mode selector** (combobox): `(c1) Currency > Vendor > Group > Date` is the default
- **Tabs**: All, Single, Parlay
- **Date range**: textbox with format `YYYY-MM-DD - YYYY-MM-DD`
- **Checkbox**: "Include internal ticket"
- **Table columns**: Currency | Ticket | Net Turnover | Margin | winloss | Regular (Turnover, Net Stake, Payout, Winloss) | Cashout (Turnover, Net Stake, Cashout, Winloss) | Updated at
- **Footer row**: "USD Total" — all currencies converted to USD

## How to get data

1. `playwright-cli goto https://www.ugoffice.com/reports/winloss/all`
2. `playwright-cli snapshot` to read the full table including all rows and the USD Total footer
3. Parse the data from the snapshot to answer the user's question

## Drill-down

Clicking a currency row (e.g., the "THB" cell) navigates to the vendor breakdown for that currency. The breadcrumb shows the path (e.g., "All currencies > THB"). To go deeper, click a vendor row to see groups, then a group row to see dates.

To drill down: `playwright-cli click <ref>` on the cell in the first column (Currency/Vendor/Group name) of the desired row.

## Changing date range

To query a different date range, `playwright-cli fill <date-picker-ref> 'YYYY-MM-DD - YYYY-MM-DD'`, then snapshot again for the updated table.

## Reading values from the snapshot

The snapshot renders the table as rows with cells. Each row looks like:
```
row "THB 1236 922,363.50 -11.17% 102,992.32 ..."
  - cell "THB"
  - cell "1236"
  - cell "922,363.50"
  - cell "-11.17%"
  - cell "102,992.32"
  ...
```

The footer row contains USD-converted totals:
```
row "USD Total 4332 146,549.99 -9.54% 13,978.85 ..."
```

## Column mapping (left to right)

1. Currency (or Vendor/Group/Date at deeper levels)
2. Ticket count
3. Net Turnover
4. Margin %
5. Win/Loss (overall, positive = company profit)
6. Regular Turnover
7. Regular Net Stake
8. Regular Payout
9. Regular Winloss
10. Cashout Turnover
11. Cashout Net Stake
12. Cashout amount
13. Cashout Winloss
14. Updated at
