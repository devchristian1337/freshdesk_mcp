"""
Manual integration script against a real Freshdesk account.

Set FRESHDESK_DOMAIN and FRESHDESK_API_KEY, then uncomment and run the desired
`asyncio.run(...)` at the bottom. Each tool requires a FastMCP Context; this
script builds a minimal mock so calls use environment-based config.
"""

from __future__ import annotations

import asyncio
import os
from unittest.mock import MagicMock

from mcp.server.fastmcp import Context

# Example imports — adjust to the tools you need:
# from freshdesk_mcp.server import get_ticket, update_ticket, get_ticket_fields


def _stdio_context() -> Context:
    if not os.getenv("FRESHDESK_API_KEY") or not os.getenv("FRESHDESK_DOMAIN"):
        raise SystemExit("Set FRESHDESK_API_KEY and FRESHDESK_DOMAIN")
    ctx = MagicMock(spec=Context)
    rc = MagicMock()
    rc.request = None
    ctx.request_context = rc
    return ctx


if __name__ == "__main__":
    _ctx = _stdio_context()
    # asyncio.run(get_ticket_fields(_ctx))
    print("Edit scripts/manual_fd_mcp.py and uncomment calls to run manual checks.")
