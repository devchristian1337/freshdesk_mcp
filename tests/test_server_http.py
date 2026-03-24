"""HTTP app wiring (health, MCP path)."""

from __future__ import annotations

from starlette.testclient import TestClient

from freshdesk_mcp.server import mcp


def test_health_endpoint() -> None:
    app = mcp.streamable_http_app()
    with TestClient(app) as client:
        r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "healthy"
    assert data.get("service") == "freshdesk-mcp"


def test_mcp_route_registered() -> None:
    app = mcp.streamable_http_app()
    paths = {getattr(r, "path", None) for r in app.routes}
    assert "/health" in paths
    assert "/mcp" in paths


def test_prompt_python_names_do_not_shadow_tools() -> None:
    import freshdesk_mcp.server as srv

    assert srv.create_ticket_prompt.__name__ == "create_ticket_prompt"
    assert srv.create_reply_prompt.__name__ == "create_reply_prompt"
    assert callable(srv.create_ticket)
