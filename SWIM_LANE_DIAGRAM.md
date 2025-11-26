┌────────────────────┬─────────────────────┬──────────────────────┬─────────────────┐
│  test_mcp_agent.py │    mcp_server.py    │       Ollama         │ Microsoft Graph │
│     (Client)       │      (Server)       │     (Local AI)       │      API        │
├────────────────────┼─────────────────────┼──────────────────────┼─────────────────┤
│                    │                     │                      │                 │
│   ●  Start         │                     │                      │                 │
│   │                │                     │                      │                 │
│   ↓                │                     │                      │                 │
│ Check Ollama       │                     │                      │                 │
│   │                │                     │                      │                 │
│   ↓                │                     │                      │                 │
│ Spawn Process A    │                     │                      │                 │
│   │                │                     │                      │                 │
│   ├───list_tools──→│  ● Start            │                      │                 │
│   │                │    ↓                │                      │                 │
│   │                │  Load Token         │                      │                 │
│   │                │    ↓                │                      │                 │
│   │←──[tools]──────│  Return Tools       │                      │                 │
│   │                │    ↓                │                      │                 │
│   │                │    ●  End           │                      │                 │
│   ↓                │                     │                      │                 │
│ Format Tools       │                     │                      │                 │
│   │                │                     │                      │                 │
│   ├────prompt───────────────────────── → │  ● Start             │                 │
│   │                │                     │    ↓                 │                 │
│   │                │                     │  Analyze Request     │                 │
│   │                │                     │    ↓                 │                 │
│   │                │                     │  Select Tool         │                 │
│   │                │                     │    ↓                 │                 │
│   │←────JSON──────────────────────────── │  Generate JSON       │                 │
│   │                │                     │    ↓                 │                 │
│   ↓                │                     │    ●  End            │                 │
│ Parse JSON         │                     │                      │                 │
│   │                │                     │                      │                 │
│   ↓                │                     │                      │                 │
│ Spawn Process B    │                     │                      │                 │
│   │                │                     │                      │                 │
│   ├──call_tool────→│  ● Start            │                      │                 │
│   │   get_emails(3)│    ↓                │                      │                 │
│   │                │  Load Token         │                      │                 │
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
│   ●  End           │                     │                      │                 │
│                    │                     │                      │                 │
└────────────────────┴─────────────────────┴──────────────────────┴─────────────────┘