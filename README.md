# Freshdesk MCP Server
[![smithery badge](https://smithery.ai/badge/@effytech/freshdesk_mcp)](https://smithery.ai/server/@effytech/freshdesk_mcp)

[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/effytech/freshdesk_mcp)](https://archestra.ai/mcp-catalog/effytech__freshdesk_mcp)

An MCP server implementation that integrates with Freshdesk, enabling AI models to interact with Freshdesk modules and perform various support operations.

## Features

- **Freshdesk Integration**: Seamless interaction with Freshdesk API endpoints
- **AI Model Support**: Enables AI models to perform support operations through Freshdesk
- **Automated Ticket Management**: Handle ticket creation, updates, and responses
- **Multi-tenant HTTP**: One Railway deploy can serve many Freshdesk accounts when credentials are passed per connection (query string); optional env-based config for local stdio

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

The server offers several tools for Freshdesk operations:

- `create_ticket`: Create new support tickets
  - **Inputs**:
    - `subject` (string, required): Ticket subject
    - `description` (string, required): Ticket description
    - `source` (number, required): Ticket source code
    - `priority` (number, required): Ticket priority level
    - `status` (number, required): Ticket status code
    - `email` (string, optional): Email of the requester
    - `requester_id` (number, optional): ID of the requester
    - `custom_fields` (object, optional): Custom fields to set on the ticket
    - `additional_fields` (object, optional): Additional top-level fields

- `update_ticket`: Update existing tickets
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket to update
    - `ticket_fields` (object, required): Fields to update

- `delete_ticket`: Delete a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket to delete

- `search_tickets`: Search for tickets based on criteria
  - **Inputs**:
    - `query` (string, required): Search query string

- `get_ticket_fields`: Get all ticket fields
  - **Inputs**:
    - None

- `get_tickets`: Get all tickets
  - **Inputs**:
    - `page` (number, optional): Page number to fetch
    - `per_page` (number, optional): Number of tickets per page

- `get_ticket`: Get a single ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket to get

- `get_ticket_conversation`: Get conversation for a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket

- `create_ticket_reply`: Reply to a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket
    - `body` (string, required): Content of the reply

- `create_ticket_note`: Add a note to a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket
    - `body` (string, required): Content of the note

- `update_ticket_conversation`: Update a conversation
  - **Inputs**:
    - `conversation_id` (number, required): ID of the conversation
    - `body` (string, required): Updated content

- `view_ticket_summary`: Get the summary of a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket

- `update_ticket_summary`: Update the summary of a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket
    - `body` (string, required): New summary content

- `delete_ticket_summary`: Delete the summary of a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket

- `get_agents`: Get all agents
  - **Inputs**:
    - `page` (number, optional): Page number
    - `per_page` (number, optional): Number of agents per page

- `view_agent`: Get a single agent
  - **Inputs**:
    - `agent_id` (number, required): ID of the agent

- `create_agent`: Create a new agent
  - **Inputs**:
    - `agent_fields` (object, required): Agent details

- `update_agent`: Update an agent
  - **Inputs**:
    - `agent_id` (number, required): ID of the agent
    - `agent_fields` (object, required): Fields to update

- `search_agents`: Search for agents
  - **Inputs**:
    - `query` (string, required): Search query

- `list_contacts`: Get all contacts
  - **Inputs**:
    - `page` (number, optional): Page number
    - `per_page` (number, optional): Contacts per page

- `get_contact`: Get a single contact
  - **Inputs**:
    - `contact_id` (number, required): ID of the contact

- `search_contacts`: Search for contacts
  - **Inputs**:
    - `query` (string, required): Search query

- `update_contact`: Update a contact
  - **Inputs**:
    - `contact_id` (number, required): ID of the contact
    - `contact_fields` (object, required): Fields to update

- `list_companies`: Get all companies
  - **Inputs**:
    - `page` (number, optional): Page number
    - `per_page` (number, optional): Companies per page

- `view_company`: Get a single company
  - **Inputs**:
    - `company_id` (number, required): ID of the company

- `search_companies`: Search for companies
  - **Inputs**:
    - `query` (string, required): Search query

- `find_company_by_name`: Find a company by name
  - **Inputs**:
    - `name` (string, required): Company name

- `list_company_fields`: Get all company fields
  - **Inputs**:
    - None

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


## Testing

```bash
pip install -e ".[dev]"
pytest -q
```

Local HTTP smoke test:

```bash
set FRESHDESK_API_KEY=...
set FRESHDESK_DOMAIN=yourcompany.freshdesk.com
set MCP_TRANSPORT=http
set PORT=8000
freshdesk-mcp
```

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
