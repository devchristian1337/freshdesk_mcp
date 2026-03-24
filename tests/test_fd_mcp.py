import inspect
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import httpx

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

    async def put(self, url, **kwargs):
        self.calls.append(("put", url, kwargs))
        response = self.responses["put"]
        return response(url, **kwargs) if callable(response) else response

    async def delete(self, url, **kwargs):
        self.calls.append(("delete", url, kwargs))
        response = self.responses["delete"]
        return response(url, **kwargs) if callable(response) else response


class TestTicketFunctions(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ctx = make_context(
            {
                "freshdeskDomain": "query.example.freshdesk.com",
                "freshdeskApiKey": "query-key",
            }
        )

    def test_create_ticket_symbol_is_the_tool(self):
        self.assertTrue(inspect.iscoroutinefunction(server.create_ticket))

    async def test_delete_ticket_handles_204_response(self):
        client = DummyAsyncClient(
            {"delete": lambda url, **kwargs: make_response("DELETE", url, 204)}
        )

        with patch("freshdesk_mcp.server.mcp.get_context", return_value=self.ctx), patch(
            "freshdesk_mcp.server.httpx.AsyncClient", return_value=client
        ):
            result = await server.delete_ticket(123)

        self.assertEqual(result, {"success": True, "message": "Ticket deleted successfully"})
        self.assertEqual(
            client.calls[0][1],
            "https://query.example.freshdesk.com/api/v2/tickets/123",
        )

    async def test_update_ticket_keeps_input_immutable(self):
        payload = {"status": 5, "custom_fields": {"cf_environment": "DEV"}}
        client = DummyAsyncClient(
            {
                "put": lambda url, **kwargs: make_response(
                    "PUT",
                    url,
                    200,
                    json_data={"id": 123, "status": 5, "custom_fields": {"cf_environment": "DEV"}},
                )
            }
        )

        with patch("freshdesk_mcp.server.mcp.get_context", return_value=self.ctx), patch(
            "freshdesk_mcp.server.httpx.AsyncClient", return_value=client
        ):
            result = await server.update_ticket(123, payload)

        self.assertTrue(result["success"])
        self.assertEqual(
            client.calls[0][2]["json"],
            {"status": 5, "custom_fields": {"cf_environment": "DEV"}},
        )
        self.assertEqual(payload, {"status": 5, "custom_fields": {"cf_environment": "DEV"}})

    async def test_update_ticket_conversation_returns_structured_error(self):
        client = DummyAsyncClient(
            {
                "put": lambda url, **kwargs: make_response(
                    "PUT",
                    url,
                    400,
                    json_data={"error": "bad request"},
                )
            }
        )

        with patch("freshdesk_mcp.server.mcp.get_context", return_value=self.ctx), patch(
            "freshdesk_mcp.server.httpx.AsyncClient", return_value=client
        ):
            result = await server.update_ticket_conversation(99, "reply")

        self.assertFalse(result["success"])
        self.assertIn("Failed to update conversation", result["error"])
        self.assertEqual(result["details"], {"error": "bad request"})

    async def test_read_only_still_blocks_ticket_write_operations(self):
        original = server.FRESHDESK_TICKETS_READ_ONLY
        server.FRESHDESK_TICKETS_READ_ONLY = True
        try:
            result = await server.update_ticket(123, {"status": 5})
        finally:
            server.FRESHDESK_TICKETS_READ_ONLY = original

        self.assertEqual(
            result,
            {"error": "Operation blocked: FRESHDESK_TICKETS_READ_ONLY mode is active"},
        )
