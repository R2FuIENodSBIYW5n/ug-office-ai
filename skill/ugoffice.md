# UG Office Portal — Browser Interaction Guide

Instructions for accessing the UG Office Admin back office portal (https://www.ugoffice.com) via `playwright-cli`.

All browser interactions use Bash with `playwright-cli`. Key commands:

| Command | Description |
|---------|-------------|
| `playwright-cli open <url>` | Open browser and navigate to URL |
| `playwright-cli goto <url>` | Navigate current page to URL |
| `playwright-cli snapshot` | Text snapshot (a11y tree) — returns element `ref` IDs |
| `playwright-cli screenshot` | Screenshot of the current page |
| `playwright-cli click <ref>` | Click an element by ref |
| `playwright-cli fill <ref> <text>` | Fill a form field by ref |
| `playwright-cli select <ref> <val>` | Select a dropdown option |
| `playwright-cli eval <js>` | Evaluate JavaScript in the page |
| `playwright-cli state-load <file>` | Load saved auth state (cookies + localStorage) |
| `playwright-cli state-save <file>` | Save current auth state |
| `playwright-cli tab-list` | List open tabs |
| `playwright-cli tab-select <index>` | Switch to a tab |

Use `-s=<name>` for named sessions (e.g., `playwright-cli -s=ug open https://www.ugoffice.com`).

## Portal Access

- **URL**: https://www.ugoffice.com
- **Credentials**: Read `UG_USER` and `UG_PASS` from `.env` in the project root
- **Auth**: JWT-based, stored in `localStorage` as `jwt_token`
- **Saved auth state**: `ug-auth.json` (cookies + localStorage snapshot)

## Session Management

Before accessing any data, ensure a logged-in browser session exists.

### Step 1 — Open browser with saved state

Try loading the saved auth state, then navigate to the portal:
```bash
playwright-cli open https://www.ugoffice.com/ --state=ug-auth.json
```

### Step 2 — Check if logged in

Take a snapshot to see the current page:
```bash
playwright-cli snapshot
```
- If the snapshot shows the sidebar with menu items (Reports, Operation, etc.) → logged in, continue.
- If the snapshot shows the login form (textbox "Username", "Password", button "Login") → need to login.

### Step 3 — Login (only if not logged in)

1. Read `.env` to get `UG_USER` and `UG_PASS`
2. `playwright-cli snapshot` to get the login form element refs
3. `playwright-cli fill <username-ref> '<UG_USER>'`
4. `playwright-cli fill <password-ref> '<UG_PASS>'`
5. `playwright-cli click <login-button-ref>`
6. `playwright-cli snapshot` to confirm dashboard loaded
7. `playwright-cli state-save ug-auth.json` to cache the session for next time

## Operations

Each operation has its own file under `skill/operations/`. Read the relevant file based on the user's question.

| Topic | File | When to read |
|-------|------|-------------|
| Win/Loss | `skill/operations/winloss.md` | Questions about winloss, turnover, margins, payout, currency P&L |
