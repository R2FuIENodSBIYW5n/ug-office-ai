# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir .

# Stage 2: Runtime
FROM python:3.11-slim

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY pyproject.toml .
COPY src/server/ src/server/

RUN pip install --no-cache-dir --no-deps .

# Install Playwright Chromium + system deps (requires root)
RUN pip install --no-cache-dir playwright && playwright install --with-deps chromium

RUN useradd --create-home --uid 1000 mcp
USER mcp

ENV MCP_TRANSPORT=sse \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:8000/health', timeout=3); exit(0 if r.status_code == 200 else 1)"

ENTRYPOINT ["ug-office-mcp"]
