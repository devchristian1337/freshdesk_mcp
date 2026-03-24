# Freshdesk MCP Server
[![smithery badge](https://smithery.ai/badge/@effytech/freshdesk_mcp)](https://smithery.ai/server/@effytech/freshdesk_mcp)

[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/effytech/freshdesk_mcp)](https://archestra.ai/mcp-catalog/effytech__freshdesk_mcp)

An MCP server implementation that integrates with Freshdesk, enabling AI models to interact with Freshdesk modules and perform various support operations.

## Features

- **Freshdesk Integration**: Seamless interaction with Freshdesk API endpoints
- **AI Model Support**: Enables AI models to perform support operations through Freshdesk
- **Automated Ticket Management**: Handle ticket creation, updates, and responses

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

## Deploy on Railway

This project now supports automatic startup on Railway using MCP Streamable HTTP.

### Runtime behavior

- If `PORT` or Railway environment variables are present, the server starts in `streamable-http`
- Otherwise it keeps the existing local behavior and starts in `stdio`

### Required variables

For Railway you only need the deployment/runtime variables:

- `MCP_TRANSPORT` (optional): `auto`, `stdio`, `streamable-http`, or `sse`. Defaults to `auto`
- `MCP_HOST` (optional): defaults to `0.0.0.0` for HTTP transports
- `MCP_PORT` (optional): fallback port when `PORT` is not provided
- `MCP_PATH` (optional): defaults to `/mcp`
- `FRESHDESK_TICKETS_READ_ONLY` (optional): `true` to block ticket write operations

### Claude connector URL

You can now pass Freshdesk credentials in the connector URL instead of storing them in Railway:

```text
https://<your-railway-domain>/mcp?freshdeskDomain=yourcompany.freshdesk.com&freshdeskApiKey=<YOUR_FRESHDESK_API_KEY>
```

The server resolves credentials in this order:

1. `freshdeskDomain` and `freshdeskApiKey` from the connector URL
2. `FRESHDESK_DOMAIN` and `FRESHDESK_API_KEY` from environment variables as a local fallback

### Healthcheck

The service exposes:

```text
GET /healthz
```

### Security warning

Passing `freshdeskApiKey` in the query string is supported for compatibility with the connector workflow you requested, but it is not recommended.

Query-string secrets can be exposed through:

- connector configuration history
- browser history
- infrastructure logs
- reverse proxies and monitoring tools

Prefer environment variables or a dedicated authentication flow whenever possible.

## Example Operations

Once configured, you can ask Claude to perform operations like:

- "Create a new ticket with subject 'Payment Issue for customer A101' and description as 'Reaching out for a payment issue in the last month for customer A101', where customer email is a101@acme.com and set priority to high"
- "Update the status of ticket #12345 to 'Resolved'"
- "List all high-priority tickets assigned to the agent John Doe"
- "List previous tickets of customer A101 in last 30 days"


## Testing

For testing purposes, you can start the server manually:

```bash
freshdesk-mcp
```

To test the Railway-compatible HTTP mode locally:

```bash
PORT=8080 MCP_TRANSPORT=streamable-http freshdesk-mcp
```

Then check:

```text
http://127.0.0.1:8080/healthz
```

## Troubleshooting

- Verify your Freshdesk API key and domain are correct
- Ensure proper network connectivity to Freshdesk servers
- Check API rate limits and quotas
- Verify the `uvx` command is available in your PATH

## License

This MCP server is licensed under the MIT License. See the LICENSE file in the project repository for full details.
