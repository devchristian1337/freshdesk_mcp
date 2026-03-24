import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from starlette.testclient import TestClient

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from freshdesk_mcp import server


def make_response(method: str, url: str, status_code: int, json_data=None, headers=None) -> httpx.Response:
    request = httpx.Request(method, url)
    return httpx.Response(status_code, json=json_data, headers=headers, request=request)


def make_context(query_params=None):
    request = SimpleNamespace(query_params=query_params or {})
    return SimpleNamespace(request_context=SimpleNamespace(request=request))


class DummyAsyncClient:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        response = self.responses["get"]
        return response(url, **kwargs) if callable(response) else response


class TestParseHeaderFunction(unittest.TestCase):
    def test_parse_link_header(self):
        header = '<https://example.com?page=2>; rel="next", <https://example.com?page=1>; rel="prev"'
        result = server.parse_link_header(header)
        self.assertEqual(result.get("next"), 2)
        self.assertEqual(result.get("prev"), 1)

    def test_parse_link_header_empty(self):
        result = server.parse_link_header("")
        self.assertEqual(result, {"next": None, "prev": None})

    def test_parse_link_header_invalid_format(self):
        result = server.parse_link_header("invalid format")
        self.assertEqual(result, {"next": None, "prev": None})


class TestRuntimeConfig(unittest.TestCase):
    def test_auto_transport_defaults_to_stdio_without_railway_signals(self):
        with patch.dict(os.environ, {}, clear=True):
            runtime = server.resolve_runtime_config()

        self.assertEqual(runtime.transport, "stdio")
        self.assertEqual(runtime.host, "127.0.0.1")

    def test_auto_transport_switches_to_streamable_http_with_port(self):
        with patch.dict(os.environ, {"PORT": "9090"}, clear=True):
            runtime = server.resolve_runtime_config()

        self.assertEqual(runtime.transport, "streamable-http")
        self.assertEqual(runtime.host, "0.0.0.0")
        self.assertEqual(runtime.port, 9090)
        self.assertEqual(runtime.path, "/mcp")

    def test_explicit_transport_overrides_auto_detection(self):
        with patch.dict(os.environ, {"PORT": "9090", "MCP_TRANSPORT": "stdio"}, clear=True):
            runtime = server.resolve_runtime_config()

        self.assertEqual(runtime.transport, "stdio")

    def test_http_runtime_disables_access_logs(self):
        runtime = server.RuntimeConfig(
            transport="streamable-http",
            host="0.0.0.0",
            port=8080,
            path="/mcp",
        )

        with patch("freshdesk_mcp.server.mcp.streamable_http_app", return_value="app"), patch(
            "uvicorn.Config"
        ) as config_cls, patch("uvicorn.Server") as server_cls:
            server.run_runtime(server.mcp, runtime)

        self.assertFalse(config_cls.call_args.kwargs["access_log"])
        server_cls.return_value.run.assert_called_once()


class TestFreshdeskConfig(unittest.TestCase):
    def test_query_params_override_env_fallback(self):
        ctx = make_context(
            {
                "freshdeskDomain": "query.example.freshdesk.com",
                "freshdeskApiKey": "query-key",
            }
        )
        with patch.dict(
            os.environ,
            {"FRESHDESK_DOMAIN": "env.example.freshdesk.com", "FRESHDESK_API_KEY": "env-key"},
            clear=True,
        ), patch("freshdesk_mcp.server.mcp.get_context", return_value=ctx):
            config = server.resolve_freshdesk_config()

        self.assertEqual(config.domain, "query.example.freshdesk.com")
        self.assertEqual(config.api_key, "query-key")

    def test_env_fallback_is_used_without_request_context(self):
        with patch.dict(
            os.environ,
            {"FRESHDESK_DOMAIN": "env.example.freshdesk.com", "FRESHDESK_API_KEY": "env-key"},
            clear=True,
        ), patch("freshdesk_mcp.server.mcp.get_context", side_effect=ValueError):
            config = server.resolve_freshdesk_config()

        self.assertEqual(config.domain, "env.example.freshdesk.com")
        self.assertEqual(config.api_key, "env-key")

    def test_builders_use_resolved_config(self):
        ctx = make_context(
            {
                "freshdeskDomain": "query.example.freshdesk.com",
                "freshdeskApiKey": "query-key",
            }
        )
        with patch("freshdesk_mcp.server.mcp.get_context", return_value=ctx):
            base_url = server.build_freshdesk_base_url()
            full_url = server.build_freshdesk_url("/tickets")
            headers = server.build_freshdesk_headers(content_type="application/json")

        self.assertEqual(base_url, "https://query.example.freshdesk.com/api/v2")
        self.assertEqual(full_url, "https://query.example.freshdesk.com/api/v2/tickets")
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Content-Type"], "application/json")


class TestCompanyFunctions(unittest.IsolatedAsyncioTestCase):
    async def test_list_companies_parses_pagination(self):
        client = DummyAsyncClient(
            {
                "get": lambda url, **kwargs: make_response(
                    "GET",
                    url,
                    200,
                    json_data=[{"id": 1, "name": "Acme"}],
                    headers={
                        "Link": '<https://example.freshdesk.com/api/v2/companies?page=2>; rel="next"'
                    },
                )
            }
        )
        ctx = make_context(
            {
                "freshdeskDomain": "query.example.freshdesk.com",
                "freshdeskApiKey": "query-key",
            }
        )

        with patch("freshdesk_mcp.server.mcp.get_context", return_value=ctx), patch(
            "freshdesk_mcp.server.httpx.AsyncClient", return_value=client
        ):
            result = await server.list_companies(page=1, per_page=10)

        self.assertEqual(result["companies"][0]["name"], "Acme")
        self.assertEqual(result["pagination"]["current_page"], 1)
        self.assertEqual(result["pagination"]["next_page"], 2)
        self.assertEqual(result["pagination"]["per_page"], 10)
        self.assertEqual(
            client.calls[0][1],
            "https://query.example.freshdesk.com/api/v2/companies",
        )

    async def test_search_companies_uses_name_query_param(self):
        client = DummyAsyncClient(
            {
                "get": lambda url, **kwargs: make_response(
                    "GET",
                    url,
                    200,
                    json_data={"companies": [{"id": 33, "name": "Acme Inc."}]},
                )
            }
        )
        ctx = make_context(
            {
                "freshdeskDomain": "query.example.freshdesk.com",
                "freshdeskApiKey": "query-key",
            }
        )

        with patch("freshdesk_mcp.server.mcp.get_context", return_value=ctx), patch(
            "freshdesk_mcp.server.httpx.AsyncClient", return_value=client
        ):
            result = await server.search_companies("Acme")

        self.assertEqual(result["companies"][0]["id"], 33)
        self.assertEqual(client.calls[0][2]["params"], {"name": "Acme"})

    async def test_missing_domain_returns_structured_error_without_leaking_api_key(self):
        ctx = make_context({"freshdeskApiKey": "super-secret-key"})

        with patch.dict(os.environ, {}, clear=True), patch("freshdesk_mcp.server.mcp.get_context", return_value=ctx):
            result = await server.list_companies(page=1, per_page=10)

        self.assertEqual(result["domain_status"], "missing")
        self.assertNotIn("super-secret-key", str(result))


class TestHttpApp(unittest.TestCase):
    def test_healthcheck_endpoint_is_available(self):
        with patch.dict(os.environ, {"PORT": "8080"}, clear=True):
            runtime = server.configure_runtime(server.mcp)
            app = server.mcp.streamable_http_app()

        routes = [getattr(route, "path", None) for route in app.routes]
        self.assertIn(runtime.path, routes)

        with TestClient(app) as client:
            response = client.get("/healthz")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
