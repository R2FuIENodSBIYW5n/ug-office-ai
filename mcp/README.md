# UG Office MCP

FastMCP server that bridges Claude and other MCP clients to the **UG Office** sportsbook back-office API.

## Features

- **188 tools** across 8 domains — settlement, sports, tickets, reports, operators, members, system, browser
- **Browser automation** — Playwright-powered tools for navigating, screenshotting, and extracting data from the UG Office SPA
- **SSE and stdio transports** — run as a networked service or pipe directly into Claude Desktop
- **OAuth 2.1 authentication** (SSE mode) with per-user sessions and dynamic client registration
- **Auto-auth** in stdio mode via environment credentials
- **Docker-ready** with multi-stage build, healthcheck, and GitHub Actions CI/CD
- **API discovery crawler** (optional) — Playwright-based SPA walker that maps every back-office endpoint

## Quick Start

**Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/) (recommended)

```bash
# Clone and install
git clone <repo-url> && cd ug-office-mcp
uv sync
uv run playwright install --with-deps chromium

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run (stdio)
uv run ug-office-mcp

# Run (SSE)
MCP_TRANSPORT=sse uv run ug-office-mcp
```

### Claude Desktop (stdio)

Add to your Claude Desktop MCP config:

```json
{
  "mcpServers": {
    "ug-office": {
      "command": "uv",
      "args": ["run", "ug-office-mcp"],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "UG_OFFICE_URL": "https://your-ug-office-url.com",
        "UG_USERNAME": "your_username",
        "UG_PASSWORD": "your_password",
        "UG_WEB_URL": "https://your-ug-office-url.com"
      }
    }
  }
}
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `MCP_TRANSPORT` | `stdio` | Transport mode: `stdio` or `sse` |
| `MCP_HOST` | `0.0.0.0` | Bind address (SSE only) |
| `MCP_PORT` | `8000` | Listen port (SSE only) |
| `OAUTH_ISSUER_URL` | `http://localhost:8000` | OAuth issuer URL (SSE only) |
| `USER_REGISTRY_PATH` | `data/user_registry.json` | Path to user registry file (SSE only) |
| `UG_OFFICE_URL` | `https://www.ugoffice.com` | UG Office API base URL |
| `UG_USERNAME` | — | API username (stdio only) |
| `UG_PASSWORD` | — | API password (stdio only) |
| `UG_WEB_URL` | `https://www.ugoffice.com` | SPA URL for Playwright browser tools |
| `LOG_LEVEL` | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR |
| `OAUTH_ACCESS_TOKEN_TTL` | `3600` | Access token lifetime in seconds (SSE only) |
| `OAUTH_REFRESH_TOKEN_TTL` | `86400` | Refresh token lifetime in seconds (SSE only) |
| `OAUTH_AUTH_CODE_TTL` | `300` | Authorization code lifetime in seconds (SSE only) |

## Docker

### docker-compose (recommended)

```bash
cp .env.example .env
# Edit .env with your credentials

# For SSE/OAuth mode, set up the user registry:
cp data/user_registry.example.json data/user_registry.json
# Edit data/user_registry.json with real credentials

docker compose up -d
```

The server listens on port **8000** by default. The Docker image includes Playwright Chromium for browser tools.

### Standalone

```bash
docker build -t ug-office-mcp .
docker run -p 8000:8000 --env-file .env ug-office-mcp
```

## Tool Modules

| Module | Tools | Description |
|---|---|---|
| **settlement** | ~29 | Resolve, void, hold/unhold, freeze, recovery, notifications |
| **sports** | ~80 | Fixtures, matches, odds, tournaments, competitors, markets |
| **tickets** | ~20 | Search, status, void, pause, cashout, insurance |
| **reports** | ~18 | Win/loss, odds difference, total bet, performance |
| **operators** | 10 | CRUD, config, currencies, packages |
| **members** | 6 | Members, vendors, vendor rewards, member tree |
| **system** | ~18 | Users, permissions, roles, auth settings |
| **browser** | 7 | Navigate, screenshot, extract tables, interact, evaluate JS |

### Browser Tools

The browser module uses Playwright to automate an authenticated Chromium session against the UG Office SPA:

- **browse_page** — Navigate to a page and return its text content
- **screenshot_page** — Take a full-page PNG screenshot (returned as base64)
- **extract_table** — Extract HTML table data as structured JSON
- **page_interact** — Perform a sequence of click/fill/wait actions
- **screenshot_winloss_report** — Screenshot the Win/Loss report with optional date filters
- **page_evaluate** — Execute JavaScript in the browser context (trusted operators only)

## Architecture

```
┌──────────────────────────────┐
│  Claude / MCP Client         │
└──────────┬───────────────────┘
           │ stdio or SSE
┌──────────▼───────────────────┐
│  FastMCP Server (main.py)    │
│  ├─ OAuth provider (SSE)     │
│  ├─ Rate limiter + CSRF      │
│  └─ Tool router              │
├──────────────────────────────┤
│  Tool Modules (8 domains)    │
│  settlement │ sports │ ...   │
├──────────────────────────────┤
│  OfficeClient    BrowserStore│
│  (httpx/JWT)     (Playwright)│
└──────────┬───────────────────┘
           │ HTTPS
┌──────────▼───────────────────┐
│  UG Office Back-Office API   │
└──────────────────────────────┘
```

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest tests/ -v

# Lint and format
uv run ruff check .
uv run ruff format .
```

## API Discovery

An optional Playwright-based crawler can walk the UG Office SPA and map every API endpoint:

```bash
uv sync --extra discovery
uv run python -m discovery.crawler
```

This generates an API map used to inform tool development.

## CI/CD

GitHub Actions workflows:
- **ci.yml** — Runs lint (ruff) and tests on every push/PR to `main`
- **docker-publish.yml** — Builds and pushes Docker images to `ghcr.io` on pushes to `main` and version tags (`v*`)

## Troubleshooting

**Browser tools fail with "Failed to launch Chromium"**
- Run `uv run playwright install --with-deps chromium` to install the browser binary and system dependencies.

**Discovery crawler hangs indefinitely**
- This was caused by `wait_until="networkidle"` on UG Office's SPA (persistent WebSocket connections never go idle). Fixed in the codebase — ensure you're on the latest version.

**OAuth login returns 429 Too Many Requests**
- The server rate-limits login attempts to 5 per IP per minute. Wait 60 seconds and try again.

**Docker build fails on Playwright**
- The Dockerfile installs Playwright Chromium automatically. If the base image changes, ensure `playwright install --with-deps chromium` is run as root before switching to the `mcp` user.
