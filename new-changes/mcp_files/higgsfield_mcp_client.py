#utils/higgsfield_mcp_client.py

"""
MCP client for Higgsfield's hosted MCP server.

Replaces the old REST-based `higgsfield_client` usage. Higgsfield no
longer allows external models over the plain API-key endpoint — MCP
(or their CLI) is the supported path now.

What this module does:
  1. Opens a local browser for a one-time OAuth 2.1 (PKCE) login against
     Higgsfield's account system, the first time you ever run it.
  2. Caches the resulting tokens (and refresh token) to a JSON file on
     disk via FileTokenStorage, so every run after that reuses the cached
     token / silently refreshes it — no browser required.
  3. Exposes a small async wrapper (`HiggsfieldMCP`) for calling tools
     on the server (image generation, tool listing, etc.).

Run this file directly (`python -m utils.higgsfield_mcp_client`) once to
do the first login and print the tool list, so you can confirm the tool
name and argument names used in utils/image_generation.py actually match
what the live server exposes (these can change as Higgsfield updates
their MCP surface).
"""

import asyncio
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, parse_qs

from mcp import ClientSession
from mcp.client.auth import OAuthClientProvider, TokenStorage
from mcp.client.streamable_http import streamablehttp_client
from mcp.shared.auth import (
    OAuthClientInformationFull,
    OAuthClientMetadata,
    OAuthToken,
)

from config import HIGGSFIELD_MCP_URL, HIGGSFIELD_TOKEN_STORE_PATH

REDIRECT_HOST = "localhost"
REDIRECT_PORT = 8765
REDIRECT_URI = f"http://{REDIRECT_HOST}:{REDIRECT_PORT}/callback"


# ---------------------------------------------------------------------------
# Token storage — the SDK gives you the protocol, you own persistence.
# Without this, OAuthClientProvider only keeps tokens in memory and you'd
# get the browser prompt on every single run.
# ---------------------------------------------------------------------------
class FileTokenStorage(TokenStorage):
    """Persists OAuth tokens + DCR client info to a local JSON file."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, Any] = self._read()

    def _read(self) -> dict[str, Any]:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _write(self) -> None:
        self.path.write_text(json.dumps(self._data, indent=2))

    async def get_tokens(self) -> OAuthToken | None:
        raw = self._data.get("tokens")
        return OAuthToken.model_validate(raw) if raw else None

    async def set_tokens(self, tokens: OAuthToken) -> None:
        self._data["tokens"] = tokens.model_dump(mode="json")
        self._write()

    async def get_client_info(self) -> OAuthClientInformationFull | None:
        raw = self._data.get("client_info")
        return OAuthClientInformationFull.model_validate(raw) if raw else None

    async def set_client_info(self, client_info: OAuthClientInformationFull) -> None:
        self._data["client_info"] = client_info.model_dump(mode="json")
        self._write()


# ---------------------------------------------------------------------------
# Local callback server — catches Higgsfield's redirect
# (http://localhost:8765/callback?code=...&state=...) after login.
# ---------------------------------------------------------------------------
class _CallbackResult:
    def __init__(self):
        self.code: str | None = None
        self.state: str | None = None
        self.error: str | None = None


def _run_callback_server(result: _CallbackResult, ready_event: threading.Event) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            params = parse_qs(urlparse(self.path).query)

            result.code = params.get("code", [None])[0]
            result.state = params.get("state", [None])[0]
            result.error = params.get("error", [None])[0]

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h2>Higgsfield login complete.</h2>"
                b"<p>You can close this tab and return to the terminal.</p>"
                b"</body></html>"
            )
            ready_event.set()

        def log_message(self, *args):
            pass  # silence default request logging

    server = HTTPServer((REDIRECT_HOST, REDIRECT_PORT), Handler)
    server.timeout = 300
    server.handle_request()  # blocks for exactly one request, then returns
    server.server_close()


async def _redirect_handler(auth_url: str) -> None:
    print("\nOpening your browser to log into Higgsfield...")
    print(f"If it doesn't open automatically, visit:\n{auth_url}\n")
    await asyncio.to_thread(webbrowser.open, auth_url)


async def _callback_handler() -> tuple[str, str | None]:
    result = _CallbackResult()
    ready_event = threading.Event()

    server_thread = threading.Thread(
        target=_run_callback_server, args=(result, ready_event), daemon=True
    )
    server_thread.start()

    # Wait for the browser redirect without blocking the event loop.
    await asyncio.to_thread(ready_event.wait, 300)

    if result.error:
        raise RuntimeError(f"Higgsfield OAuth login failed: {result.error}")
    if not result.code:
        raise TimeoutError("Timed out waiting for Higgsfield OAuth login.")

    return result.code, result.state


def _build_oauth_provider() -> OAuthClientProvider:
    storage = FileTokenStorage(HIGGSFIELD_TOKEN_STORE_PATH)

    return OAuthClientProvider(
        server_url=HIGGSFIELD_MCP_URL,
        client_metadata=OAuthClientMetadata(
            client_name="Ootsav AI Marketing Agent",
            redirect_uris=[REDIRECT_URI],
            grant_types=["authorization_code", "refresh_token"],
            response_types=["code"],
        ),
        storage=storage,
        redirect_handler=_redirect_handler,
        callback_handler=_callback_handler,
    )


class HiggsfieldMCP:
    """
    Thin async wrapper around Higgsfield MCP tool calls.

    Opens a fresh session per call (simple + robust for how infrequently
    image generation happens in this app). Tokens are cached on disk via
    FileTokenStorage, so this only opens a browser the first time, or if
    the refresh token itself later expires / gets revoked.
    """

    def __init__(self):
        self._oauth = _build_oauth_provider()

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        async with streamablehttp_client(HIGGSFIELD_MCP_URL, auth=self._oauth) as (
            read,
            write,
            _,
        ):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.call_tool(tool_name, arguments)

    async def list_tools(self) -> list[str]:
        async with streamablehttp_client(HIGGSFIELD_MCP_URL, auth=self._oauth) as (
            read,
            write,
            _,
        ):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                return [t.name for t in tools.tools]


higgsfield_mcp = HiggsfieldMCP()


if __name__ == "__main__":
    # One-off check: run `python -m utils.higgsfield_mcp_client`
    # Triggers the browser login (first time only) and prints every tool
    # the server currently exposes — use this to confirm the tool name
    # and argument names used in utils/image_generation.py.
    async def _debug():
        tools = await higgsfield_mcp.list_tools()
        print("\nAvailable Higgsfield MCP tools:")
        for name in tools:
            print(f"  - {name}")

    asyncio.run(_debug())
