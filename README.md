# MCP Email Server

An MCP (Model Context Protocol) server that provides AI models with access to Microsoft Outlook emails via Microsoft Graph API.

## Overview

This project implements email access for AI models in two ways:
- **FastAPI Server** (`server.py`) - HTTP/REST endpoint for testing with Ollama
- **MCP Server** (`mcp_server.py`) - Official MCP protocol implementation for Claude Desktop and other MCP clients

## Architecture

```
AI Model → MCP Server → Microsoft Graph API → Outlook
```

Both implementations wrap the same Microsoft Graph API calls and expose them as discoverable tools that AI models can use.

## Features

- **get_emails** - Retrieve recent emails from inbox
- **send_email** - Send email to recipients
- OAuth2 device code authentication with token caching

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure Azure App:**
   - Create an Azure AD app registration
   - Add API permissions: `Mail.Read`, `Mail.Send` (Delegated)
   - Copy Client ID and Tenant ID

3. **Set environment variables:**
```bash
# .env file
AZURE_CLIENT_ID=your-client-id
AZURE_TENANT_ID=your-tenant-id
```

4. **Authenticate:**
```bash
python authenticate.py
```
Follow the device code flow. Token is cached in `~/.email_mcp_token_cache.bin`

## Usage

### Testing with FastAPI + Ollama

```bash
# Start HTTP server
python server.py

# Run Ollama test
python test_ollama.py
```

### Using with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python mcp_server.py
```

Navigate to the web interface to:
- View available tools
- Test tool execution
- Inspect request/response flow

### Using with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

## Files

- `authenticate.py` - One-time authentication script
- `server.py` - FastAPI HTTP server
- `mcp_server.py` - MCP protocol server
- `test_ollama.py` - Ollama integration test

## Authentication

The project uses OAuth2 device code flow:
1. Run `authenticate.py` once to get a token
2. Token is cached and reused by both servers
3. Re-authenticate when token expires (typically 1 hour)

Check token status:
```bash
python authenticate.py check
```

## How It Works

1. **Tool Definition**: Both servers expose the same tools with schemas describing parameters
2. **AI Discovery**: AI models query available tools and their schemas
3. **Tool Execution**: AI generates proper tool calls, server executes against Microsoft Graph API
4. **Response**: Real email data returned to AI model