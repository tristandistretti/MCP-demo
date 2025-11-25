# MCP Agent Workflow

## Flow Diagram

```
User Request: "Get my 3 most recent emails"
        ↓
┌────────────────────────────────────────────────┐
│ 1. TOOL DISCOVERY                              │
│ test_mcp_agent.py spawns mcp_server.py         │
│ Client → "list_tools" → Server                 │
│ Server → ["get_emails", "send_email"] → Client │
└────────────────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────────┐
│ 2. AI REASONING (Ollama)                       │
│ Input: "Get my 3 most recent emails"           │
│ Ollama → {"tool": "get_emails", "count": 3}    │
└────────────────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────────┐
│ 3. TOOL EXECUTION                              │
│ test_mcp_agent.py spawns mcp_server.py         │
│ Client → "call get_emails(count=3)" → Server   │
│ Server → Microsoft Graph API                   │
│ Server → Returns email JSON → Client           │
└────────────────────────────────────────────────┘
        ↓
Result: 3 emails displayed to user
```

## Detailed Workflow

### Step 1: Tool Discovery

**Client spawns server:**
```python
# test_mcp_agent.py
server_params = StdioServerParameters(
    command="python",
    args=["mcp_server.py"]
)
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        response = await session.list_tools()
```

**Server responds:**
```python
# mcp_server.py
@mcp.tool()
async def get_emails(count: int = 3) -> str:
    """Get recent emails from inbox"""
    # Tool definition automatically registered
```

**Result:** Client knows available tools: `get_emails`, `send_email`

---

### Step 2: AI Reasoning

**Ollama decides which tool to use:**
```python
# test_mcp_agent.py
prompt = f"""You have these tools:
- get_emails: Get recent emails from inbox
- send_email: Send an email

User request: Get my 3 most recent emails

Respond with JSON: {{"tool": "tool_name", "arguments": {{...}}}}"""

response = ollama.generate(model='llama3.2', prompt=prompt)
# Ollama returns: {"tool": "get_emails", "arguments": {"count": 3}}
```

---

### Step 3: Tool Execution

**Client calls tool:**
```python
# test_mcp_agent.py
result = await session.call_tool("get_emails", {"count": 3})
```

**Server executes:**
```python
# mcp_server.py
@mcp.tool()
async def get_emails(count: int = 3) -> str:
    client = get_graph_client()
    messages = await client.me.messages.get(...)
    
    emails = [{"subject": msg.subject, "from": ..., ...} for msg in messages.value]
    return json.dumps({"count": len(emails), "emails": emails})
```

**Result:** Email data returned to client

---

## Process Flow

```
┌──────────────────┐
│ test_mcp_agent.py│
└────────┬─────────┘
         │ spawn process
         ↓
┌──────────────────┐     ┌──────────────────┐
│ mcp_server.py    │────→│ Microsoft Graph  │
│ (Process A)      │←────│ API              │
└────────┬─────────┘     └──────────────────┘
         │ returns tools
         │ terminates
         ↓
┌──────────────────┐
│ Ollama           │
│ (local AI)       │
└────────┬─────────┘
         │ decides: use get_emails
         ↓
┌──────────────────┐
│ test_mcp_agent.py│
└────────┬─────────┘
         │ spawn process again
         ↓
┌──────────────────┐     ┌──────────────────┐
│ mcp_server.py    │────→│ Microsoft Graph  │
│ (Process B)      │←────│ API              │
└────────┬─────────┘     └──────────────────┘
         │ returns emails
         │ terminates
         ↓
┌──────────────────┐
│ User sees emails │
└──────────────────┘
```

## Communication Protocol

### Request: List Tools
```
Client stdin → Server
{
  "method": "tools/list",
  "params": {}
}
```

### Response: Available Tools
```
Server stdout → Client
{
  "tools": [
    {"name": "get_emails", "description": "...", "inputSchema": {...}},
    {"name": "send_email", "description": "...", "inputSchema": {...}}
  ]
}
```

### Request: Call Tool
```
Client stdin → Server
{
  "method": "tools/call",
  "params": {
    "name": "get_emails",
    "arguments": {"count": 3}
  }
}
```

### Response: Tool Result
```
Server stdout → Client
{
  "content": [
    {
      "type": "text",
      "text": "{\"count\": 3, \"emails\": [...]}"
    }
  ]
}
```

## Key Points

1. **MCP server spawned twice**: Once for discovery, once for execution
2. **Ollama is separate**: It only decides which tool to use based on available tools
3. **Communication via stdin/stdout**: No HTTP, no network sockets
4. **Stateless**: Each server process loads auth token, executes, then terminates
5. **Token caching critical**: Makes process spawning fast (~100ms instead of 30s)