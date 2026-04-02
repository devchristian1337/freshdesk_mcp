# Freshdesk MCP Server

[![smithery badge](https://smithery.ai/badge/@effytech/freshdesk_mcp)](https://smithery.ai/server/@effytech/freshdesk_mcp)
[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/effytech/freshdesk_mcp)](https://archestra.ai/mcp-catalog/effytech__freshdesk_mcp)

An MCP server that integrates with Freshdesk, enabling AI models to manage tickets, contacts, companies, knowledge base articles, canned responses, and more.

## Features

- **59 Tools** across tickets, agents, contacts, companies, groups, canned responses, solutions, and field management
- **2 Prompts** (`create_ticket`, `create_reply`) to guide AI models through Freshdesk payloads
- **MCP ToolAnnotations** on every tool for safe AI-driven automation
- **Multi-tenant HTTP**: one deployment serves many Freshdesk accounts via per-connection query string credentials
- **Read-only mode** via `FRESHDESK_TICKETS_READ_ONLY`
- **Full conversation pagination**: `get_ticket_conversation` fetches all pages transparently

## Quick Start

### Prerequisites

- Python 3.10+
- Freshdesk API key (from **Profile Settings > API Key** in Freshdesk)
- [`uv`](https://docs.astral.sh/uv/) (`pip install uv` or `brew install uv`)

### Install via Smithery

```bash
npx -y @smithery/cli install @effytech/freshdesk_mcp --client claude
```

### Manual configuration

Add to your MCP client config (Claude Desktop `claude_desktop_config.json`, Cursor `.cursor/mcp.json`, etc.):

```json
{
  "mcpServers": {
    "freshdesk-mcp": {
      "command": "uvx",
      "args": ["freshdesk-mcp"],
      "env": {
        "FRESHDESK_API_KEY": "<YOUR_API_KEY>",
        "FRESHDESK_DOMAIN": "yourcompany.freshdesk.com",
        "FRESHDESK_TICKETS_READ_ONLY": "false"
      }
    }
  }
}
```

## Transport Modes

| Mode | When to use | Config |
|------|-------------|--------|
| **stdio** (default) | Claude Desktop, Cursor, local clients | Set `FRESHDESK_*` env vars |
| **Streamable HTTP** | Claude.ai, Railway, remote clients | `MCP_TRANSPORT=http`, MCP at `/mcp`, health at `/health` |

### Remote deployment (Railway)

1. Deploy with the root `Dockerfile`
2. Set `MCP_TRANSPORT=http` and `FASTMCP_STATELESS_HTTP=true` (do **not** set `PORT`, Railway injects it)
3. Health check path: `/health`
4. Connect from Claude.ai at: `https://<host>/mcp?freshdesk_domain=<tenant>.freshdesk.com&freshdesk_api_key=<KEY>`

> **Security**: API key in query string can appear in logs and browser history. Prefer env-based auth where possible.

## Tools

59 tools organized by module:

| Module | Tools | Operations |
|--------|-------|------------|
| Tickets | 17 | CRUD, search, conversations (auto-paginated), replies, notes, summaries, fields |
| Agents | 5 | List, view, create, update, search |
| Contacts | 5 | List, view, search, update, field properties |
| Contact Fields | 4 | List, view, create, update |
| Companies | 5 | List, view, search, find by name, fields |
| Groups | 4 | List, view, create, update |
| Canned Responses | 7 | Folders + responses: list, view, create, update |
| Solutions / KB | 12 | Categories, folders, articles: list, view, create, update |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `MCP_TRANSPORT` | `stdio` (default) or `http` |
| `PORT` | HTTP listen port (auto-set by Railway) |
| `FASTMCP_STATELESS_HTTP` | `true` recommended for Railway |
| `FRESHDESK_DOMAIN` | Freshdesk host (stdio / fallback) |
| `FRESHDESK_API_KEY` | API key (stdio / fallback) |
| `FRESHDESK_TICKETS_READ_ONLY` | Block ticket mutations when `true` |

## Testing

```bash
pip install -e ".[dev]"
pytest -q
```

## Troubleshooting

- **Auth errors**: verify API key and domain; for HTTP mode check URL-encoding of query params
- **404 on `/`**: expected — MCP lives at `/mcp`, health at `/health`
- **Railway unhealthy**: confirm the process binds `0.0.0.0:$PORT` and `/health` returns 200

## License

MIT License. See [LICENSE](LICENSE).
