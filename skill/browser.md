# Browser Fallback — Session Management

Use playwright-cli via Bash when MCP tools are unavailable or a visual screenshot is needed.

## Commands

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

Use `-s=<name>` for named sessions (e.g., `playwright-cli -s=ug open https://www.ugoffice.com`).

## Portal access

- **URL**: https://www.ugoffice.com
- **Credentials**: Read `UG_USER` and `UG_PASS` from `.env` in the project root
- **Auth**: JWT-based, stored in `localStorage` as `jwt_token`
- **Saved auth state**: `ug-auth.json` (cookies + localStorage snapshot)

## Login flow

### Step 1 — Open browser with saved state

```bash
playwright-cli open https://www.ugoffice.com/ --state=ug-auth.json
```

### Step 2 — Check if logged in

```bash
playwright-cli snapshot
```
- Sidebar with menu items (Reports, Operation, etc.) → logged in, continue.
- Login form (Username, Password, Login button) → need to login.

### Step 3 — Login (only if not logged in)

1. Read `.env` to get `UG_USER` and `UG_PASS`
2. `playwright-cli snapshot` to get the login form element refs
3. `playwright-cli fill <username-ref> '<UG_USER>'`
4. `playwright-cli fill <password-ref> '<UG_PASS>'`
5. `playwright-cli click <login-button-ref>`
6. `playwright-cli snapshot` to confirm dashboard loaded
7. `playwright-cli state-save ug-auth.json` to cache the session for next time
