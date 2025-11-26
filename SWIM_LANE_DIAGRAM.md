┌────────────────────┬─────────────────────┬──────────────────────┬─────────────────┐
│  test_mcp_agent.py │    mcp_server.py    │       Ollama         │ Microsoft Graph │
│     (Client)       │      (Server)       │     (Local AI)       │      API        │
├────────────────────┼─────────────────────┼──────────────────────┼─────────────────┤
│                    │                     │                      │                 │
│   ●  Start         │                     │                      │                 │
│   │                │                     │                      │                 │
│   ↓                │                     │                      │                 │
│ Check Ollama       │                     │                      │                 │
│ & Model            │                     │                      │                 │
│   │                │                     │                      │                 │
│   ↓                │                     │                      │                 │
│ Start mcpserver.py │  ● Start            │                      │                 │
│ via stdio (once)   │    ↓                │                      │                 │
│ and open           │  Initialize Session │                      │                 │
│ ClientSession      │    ↓                │                      │                 │
│   │                │                     │                      │                 │
│   ├─list_tools────→│  list_tools         │                      │                 │
│   │                │    ↓                │                      │                 │
│   │←──[tools]──────│  Return Tools       │                      │                 │
│   │                │                     │                      │                 │
│   ↓                │                     │                      │                 │
│ Format Tools       │                     │                      │                 │
│ for Ollama prompt  │                     │                      │                 │
│   │                │                     │                      │                 │
│   ├────prompt───────────────────────── → │  ● Start             │                 │
│   │   (tools desc) │                     │    ↓                 │                 │
│   │                │                     │  Analyze Request     │                 │
│   │                │                     │    ↓                 │                 │
│   │                │                     │  Select Tool         │                 │
│   │                │                     │    ↓                 │                 │
│   │←────JSON──────────────────────────── │  Generate JSON       │                 │
│   │ (tool+args)    │                     │    ↓                 │                 │
│   ↓                │                     │    ●  End            │                 │
│ Parse JSON         │                     │                      │                 │
│ (tool, arguments)  │                     │                      │                 │
│   │                │                     │                      │                 │
│   ├─call_tool─────→│  ● Start            │                      │                 │
│   │  get_emails(3) │    ↓                │                      │                 │
│   │  (same         │  Use existing       │                      │                 │
│   │  Session)      │  Session            │                      │                 │
│   │                │    ↓                │                      │                 │
│   │                │  Execute Function   │                      │                 │
│   │                │    ↓                │                      │                 │
│   │                │    ├───────────────────────────────────── →│  Fetch Emails   │
│   │                │    │                │                      │       ↓         │
│   │                │    │ ← ────────────────────────────────────│  Return Data    │
│   │                │    ↓                │                      │                 │
│   │                │  Format JSON        │                      │                 │
│   │                │    ↓                │                      │                 │
│   │←──[emails]─────│  Return Result      │                      │                 │
│   │                │    ↓                │                      │                 │
│   │                │    ●  End           │                      │                 │
│   ↓                │                     │                      │                 │
│ Display Results    │                     │                      │                 │
│   │                │                     │                      │                 │
│   ↓                │                     │                      │                 │
│ Close Session &    │  ● End              │                      │                 │
│ stdio client       │                     │                      │                 │
│   ↓                │                     │                      │                 │
│   ●  End           │                     │                      │                 │
│                    │                     │                      │                 │
└────────────────────┴─────────────────────┴──────────────────────┴─────────────────┘
