# Freshdesk MCP Server
[![smithery badge](https://smithery.ai/badge/@effytech/freshdesk_mcp)](https://smithery.ai/server/@effytech/freshdesk_mcp)

[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/effytech/freshdesk_mcp)](https://archestra.ai/mcp-catalog/effytech__freshdesk_mcp)

An MCP server implementation that integrates with Freshdesk, enabling AI models to interact with Freshdesk modules and perform various support operations.

## Features

- **59 Tools** covering tickets, agents, contacts, companies, groups, canned responses, solution articles, and field management
- **MCP ToolAnnotations** on every tool (read-only, destructive, idempotent hints) for safe AI-driven automation
- **2 Prompts** (`create_ticket`, `create_reply`) to guide AI models through Freshdesk payloads
- **Multi-tenant HTTP**: One Railway deploy can serve many Freshdesk accounts when credentials are passed per connection (query string); optional env-based config for local stdio
- **Read-only mode**: Block all ticket write operations via `FRESHDESK_TICKETS_READ_ONLY`

## Transport: local stdio vs remote HTTP

| Mode | When to use | How |
|------|-------------|-----|
| **stdio** (default) | Claude Desktop, local MCP clients | `MCP_TRANSPORT=stdio` or unset; set `FRESHDESK_*` env vars |
| **Streamable HTTP** | [Claude.ai](https://claude.ai) remote MCP, Railway, any HTTP MCP client | `MCP_TRANSPORT=http` (alias for streamable HTTP), listen on `PORT`, MCP at `/mcp` |

Public endpoints (HTTP mode):

- `GET /health` — JSON `{"status":"healthy","service":"freshdesk-mcp"}` (use for Railway health checks)
- `/mcp` — MCP streamable HTTP endpoint (per [FastMCP / MCP HTTP deployment](https://gofastmcp.com/deployment/http))

Recommended for Railway: `FASTMCP_STATELESS_HTTP=true` (default in the provided `Dockerfile`) so each request is stateless and you do not rely on sticky sessions.

## Remote MCP on Railway and Claude.ai

1. Deploy this repo to Railway using the root `Dockerfile` (Python 3.11 slim, `CMD ["freshdesk-mcp"]`).
2. Set **only** generic env on the service (do **not** put tenant Freshdesk secrets in Railway):

   - `MCP_TRANSPORT=http`
   - `FASTMCP_STATELESS_HTTP=true`
   - Do **not** set `PORT` (Railway injects it).
   - Do **not** set `FRESHDESK_DOMAIN` / `FRESHDESK_API_KEY` if you want per-user tenants via URL.

3. Health check path in Railway: `/health`.
4. In Claude.ai (or another remote MCP client), set the **connection URL** to:

   ```text
   https://<your-railway-host>/mcp?freshdesk_domain=<tenant>.freshdesk.com&freshdesk_api_key=<API_KEY>
   ```

   Use proper URL-encoding for the key and any special characters (e.g. `encodeURIComponent` in JavaScript).

### Query string parameters (HTTP / multi-tenant)

| Parameter | Required | Description |
|-----------|----------|-------------|
| `freshdesk_domain` | Yes | Helpdesk host, e.g. `company.freshdesk.com`, or a full `https://company.freshdesk.com` URL (host is normalized) |
| `freshdesk_api_key` | Yes | Freshdesk API key |
| `freshdesk_tickets_read_only` | No | `true` / `1` / `yes` to block mutating ticket operations for that connection; defaults from env `FRESHDESK_TICKETS_READ_ONLY` when omitted |

For **local stdio**, you can keep using `FRESHDESK_DOMAIN`, `FRESHDESK_API_KEY`, and `FRESHDESK_TICKETS_READ_ONLY` only; query params are not available without an HTTP request.

### Security warning (API key in query string)

Putting the API key in the query string is **convenient** for clients that only accept a single URL, but it is **weaker** than headers or a secret store: the key can appear in reverse-proxy access logs, browser or client history, and referrer metadata. This project implements it because it is a common requirement for remote MCP URLs; prefer env-based or header-based auth where your client supports it.

## Components

### Tools

The server provides **59 tools** across 10 Freshdesk modules. All tools include [MCP ToolAnnotations](https://modelcontextprotocol.io/specification/2025-03-26/server/tools#annotations) (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) so that AI clients can reason about safety before execution.

#### Tickets (17 tools)

| Tool | Type | Description |
|------|------|-------------|
| `get_tickets` | read | List tickets (paginated) |
| `get_ticket` | read | Get a single ticket by ID |
| `search_tickets` | read | Search tickets by query string |
| `create_ticket` | write | Create a new ticket (subject, description, priority, status, source, email/requester_id, custom_fields, additional_fields) |
| `update_ticket` | write | Update ticket fields |
| `delete_ticket` | destructive | Delete a ticket |
| `get_ticket_conversation` | read | Get all conversations for a ticket |
| `create_ticket_reply` | write | Reply to a ticket |
| `create_ticket_note` | write | Add a private note to a ticket |
| `update_ticket_conversation` | write | Update a conversation entry |
| `view_ticket_summary` | read | Get ticket summary |
| `update_ticket_summary` | write | Update ticket summary |
| `delete_ticket_summary` | destructive | Delete ticket summary |
| `get_ticket_fields` | read | List all ticket fields |
| `create_ticket_field` | write | Create a custom ticket field |
| `view_ticket_field` | read | Get a single ticket field |
| `update_ticket_field` | write | Update a ticket field |

#### Agents (5 tools)

| Tool | Type | Description |
|------|------|-------------|
| `get_agents` | read | List agents (paginated) |
| `view_agent` | read | Get a single agent by ID |
| `create_agent` | write | Create a new agent |
| `update_agent` | write | Update agent fields |
| `search_agents` | read | Search agents by query |

#### Contacts (5 tools)

| Tool | Type | Description |
|------|------|-------------|
| `list_contacts` | read | List contacts (paginated) |
| `get_contact` | read | Get a single contact by ID |
| `search_contacts` | read | Search contacts by query |
| `update_contact` | write | Update contact fields |
| `get_field_properties` | read | Get properties of a specific field by name (inspects ticket, contact and company fields) |

#### Contact Fields (4 tools)

| Tool | Type | Description |
|------|------|-------------|
| `list_contact_fields` | read | List all contact fields |
| `view_contact_field` | read | Get a single contact field |
| `create_contact_field` | write | Create a custom contact field |
| `update_contact_field` | write | Update a contact field |

#### Companies (5 tools)

| Tool | Type | Description |
|------|------|-------------|
| `list_companies` | read | List companies (paginated) |
| `view_company` | read | Get a single company by ID |
| `search_companies` | read | Search companies by query |
| `find_company_by_name` | read | Find a company by exact name |
| `list_company_fields` | read | List all company fields |

#### Groups (4 tools)

| Tool | Type | Description |
|------|------|-------------|
| `list_groups` | read | List groups (paginated) |
| `view_group` | read | Get a single group by ID |
| `create_group` | write | Create a new group |
| `update_group` | write | Update group fields |

#### Canned Responses (7 tools)

| Tool | Type | Description |
|------|------|-------------|
| `list_canned_response_folders` | read | List all canned response folders |
| `list_canned_responses` | read | List canned responses in a folder |
| `view_canned_response` | read | Get a single canned response |
| `create_canned_response` | write | Create a canned response |
| `update_canned_response` | write | Update a canned response |
| `create_canned_response_folder` | write | Create a canned response folder |
| `update_canned_response_folder` | write | Update a canned response folder |

#### Solutions / Knowledge Base (12 tools)

| Tool | Type | Description |
|------|------|-------------|
| `list_solution_categories` | read | List all solution categories |
| `view_solution_category` | read | Get a single solution category |
| `create_solution_category` | write | Create a solution category |
| `update_solution_category` | write | Update a solution category |
| `list_solution_folders` | read | List folders in a category |
| `view_solution_category_folder` | read | Get a single solution folder |
| `create_solution_category_folder` | write | Create a folder in a category |
| `update_solution_category_folder` | write | Update a solution folder |
| `list_solution_articles` | read | List articles in a folder |
| `view_solution_article` | read | Get a single solution article |
| `create_solution_article` | write | Create a solution article |
| `update_solution_article` | write | Update a solution article |

### Prompts

The server also exposes two MCP prompts to help AI models compose Freshdesk payloads:

| Prompt | Purpose |
|--------|---------|
| `create_ticket` | Provides a payload template and field reference for ticket creation |
| `create_reply` | Provides HTML formatting guidelines and context for ticket replies |

## Getting Started

### Installing via Smithery

To install freshdesk_mcp for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@effytech/freshdesk_mcp):

```bash
npx -y @smithery/cli install @effytech/freshdesk_mcp --client claude
```

### Prerequisites

- A Freshdesk account (sign up at [freshdesk.com](https://freshdesk.com))
- Freshdesk API key
- `uvx` installed (`pip install uv` or `brew install uv`)

### Configuration

1. Generate your Freshdesk API key from the Freshdesk admin panel
2. Set up your domain and authentication details

### Usage with Claude Desktop

1. Install Claude Desktop if you haven't already
2. Add the following configuration to your `claude_desktop_config.json`:

```json
"mcpServers": {
  "freshdesk-mcp": {
    "command": "uvx",
    "args": [
        "freshdesk-mcp"
    ],
    "env": {
      "FRESHDESK_API_KEY": "<YOUR_FRESHDESK_API_KEY>",
      "FRESHDESK_DOMAIN": "<YOUR_FRESHDESK_DOMAIN>",
      "FRESHDESK_TICKETS_READ_ONLY": "false"
    }
  }
}
```

**Important Notes**:
- Replace `YOUR_FRESHDESK_API_KEY` with your actual Freshdesk API key
- Replace `YOUR_FRESHDESK_DOMAIN` with your Freshdesk domain (e.g., `yourcompany.freshdesk.com`)
- Set `FRESHDESK_TICKETS_READ_ONLY` to `true` to block all ticket write operations (create, update, delete, reply, note). Accepts `true`, `1`, or `yes`. Defaults to `false`

### Environment reference

| Variable | Used in | Purpose |
|----------|---------|---------|
| `MCP_TRANSPORT` | Process | `stdio` (default) or `http` / `streamable-http` for HTTP |
| `PORT` | HTTP | Listen port (Railway sets automatically) |
| `MCP_HTTP_HOST` | HTTP | Bind address (default `0.0.0.0` when using HTTP in `main`) |
| `FASTMCP_PORT` | HTTP | Fallback if `PORT` unset (default `8000`) |
| `FASTMCP_STATELESS_HTTP` | HTTP | `true` recommended for Railway |
| `FRESHDESK_DOMAIN` | stdio / fallback | Freshdesk host when query params are absent |
| `FRESHDESK_API_KEY` | stdio / fallback | API key when query params are absent |
| `FRESHDESK_TICKETS_READ_ONLY` | Both | Default read-only flag when not overridden in query |

## Example Operations

Once configured, you can ask Claude to perform operations like:

- "Create a new ticket with subject 'Payment Issue for customer A101' and description as 'Reaching out for a payment issue in the last month for customer A101', where customer email is a101@acme.com and set priority to high"
- "Update the status of ticket #12345 to 'Resolved'"
- "List all high-priority tickets assigned to the agent John Doe"
- "List previous tickets of customer A101 in last 30 days"
- "Show me all canned response folders and list the responses in the Sales folder"
- "Create a new knowledge base article about password reset in the FAQ category"
- "List all groups and show me the members of the Support group"
- "What custom fields are available on tickets?"


## Testing

```bash
pip install -e ".[dev]"
pytest -q
```

Local HTTP smoke test:

```bash
export FRESHDESK_API_KEY=...
export FRESHDESK_DOMAIN=yourcompany.freshdesk.com
export MCP_TRANSPORT=http
export PORT=8000
freshdesk-mcp
```

On Windows (CMD), replace `export` with `set`.

Then open `http://127.0.0.1:8000/health` (or the printed port).

Manual calls against a real account can be adapted in `scripts/manual_fd_mcp.py`.

## Troubleshooting

- Verify your Freshdesk API key and domain are correct (for HTTP: check **URL-encoded** query params).
- **404 on `/`** is normal; MCP lives at **`/mcp`**, health at **`/health`**.
- If Railway reports unhealthy: confirm the process binds `0.0.0.0:$PORT` and `/health` returns 200.
- If Claude.ai cannot connect: require HTTPS on the public URL and path `/mcp`.
- Ensure proper network connectivity to Freshdesk servers and respect API rate limits.
- For local installs, verify `uvx` / `freshdesk-mcp` is on your PATH if you use those launchers.

## License

This MCP server is licensed under the MIT License. See the LICENSE file in the project repository for full details.
