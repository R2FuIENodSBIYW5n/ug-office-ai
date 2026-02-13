# Contributing

## Development Setup

```bash
# Clone and install
git clone <repo-url> && cd ug-office-mcp
uv sync --extra dev
uv run playwright install --with-deps chromium

# Configure
cp .env.example .env
# Edit .env with your UG Office credentials
```

## Running Tests

```bash
uv run pytest tests/ -v
```

Tests use `respx` for HTTP mocking and `unittest.mock` for Playwright. No real network calls or browser sessions are needed.

## Code Style

The project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
uv run ruff check .       # Lint
uv run ruff format .      # Format
```

Configuration is in `pyproject.toml` — line length 100, Python 3.11 target, E/W/F/I rules.

A pre-commit config is provided:

```bash
pip install pre-commit
pre-commit install
```

## Adding a New Tool Module

1. Create `src/server/tools/your_module.py`
2. Follow the `register(mcp: FastMCP)` pattern:

```python
from fastmcp import Context, FastMCP
from ._helpers import get_client

def register(mcp: FastMCP) -> None:
    @mcp.tool
    async def your_tool_name(param: str, ctx: Context = None):
        """Tool description shown to the MCP client."""
        client = await get_client(ctx)
        return await client.get(f"/1.0/your/endpoint?param={param}")
```

3. Import and register in `src/server/main.py`:

```python
from .tools import your_module
your_module.register(mcp)
```

4. Add the module to `src/server/tools/__init__.py` imports and `__all__`.

5. Write tests in `tests/test_your_module.py`.

## Project Structure

```
src/server/
├── main.py              # Server entrypoint, OAuth login routes
├── client.py            # OfficeClient (httpx + JWT auth)
├── auth.py              # AuthManager (JWT lifecycle)
├── browser_store.py     # BrowserStore (Playwright contexts)
├── oauth_provider.py    # OAuth 2.1 provider
├── oauth_models.py      # Extended token models
├── session_store.py     # Per-user OfficeClient cache
├── user_registry.py     # MCP user → UG Office credential mapping
└── tools/
    ├── _helpers.py      # get_client(), get_browser_context()
    ├── browser.py       # Playwright browser tools
    ├── settlement.py    # Settlement tools
    ├── sports.py        # Sports tools
    └── ...
```
