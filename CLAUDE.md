# UG Office AI

This project enables AI-assisted access to the UG Office Admin back office portal (https://www.ugoffice.com), a sports betting operations platform.

When the user asks questions about operational data (winloss, tickets, turnover, margins, currencies, vendors, etc.), read the relevant guide from `skill/` and use `playwright-cli` via Bash to interact with the portal in the browser, extract data, and answer.

## Skill guides

- `skill/ugoffice.md` — Portal access, playwright-cli commands, session management & login. **Read this first.**
- `skill/operations/winloss.md` — Win/Loss report (questions about winloss, turnover, margins, payout, currency P&L)
