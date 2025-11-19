# Setup Ollama for Testing

## Step 1: Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Or download from: https://ollama.com/download

## Step 2: Download a Model

```bash
# Recommended: Llama 3.2 (small, fast)
ollama pull llama3.2

# Or other options:
# ollama pull llama2        # Older but stable
# ollama pull mistral       # Good alternative
# ollama pull phi           # Very small/fast
```

## Step 3: Verify Installation

```bash
# Check Ollama is running
ollama list

# Test the model
ollama run llama3.2
>>> Hello!
>>> /bye
```

## Step 4: Install Python Package

```bash
pip install ollama
```

## Step 5: Run Test

```bash
# Make sure your MCP server is running
python server.py

# In another terminal, run test
python test_ollama.py
```

## What the Test Does:

1. ✓ Checks Ollama is installed
2. ✓ Checks a model is available
3. ✓ Checks your MCP server is running
4. ✓ Gets available tools from your server
5. ✓ Asks Ollama to use the tools
6. ✓ Executes the tool if Ollama responds correctly

## Expected Output:

```
============================================================
Testing MCP Email Server with Ollama
============================================================

Checking prerequisites...
------------------------------------------------------------
✓ Ollama is installed
✓ Model available
✓ MCP server is running

Getting available tools...
------------------------------------------------------------
✓ Found 2 tools
  • get_emails: Get recent emails from inbox
  • send_email: Send an email

Testing with Ollama...
------------------------------------------------------------
User: Get my 3 most recent emails

[Ollama] Thinking...

[Ollama Response]:
{"tool": "get_emails", "arguments": {"count": 3}}

[Executing Tool]: get_emails
[Arguments]: {'count': 3}

[Result]:
{
  "emails": [...],
  "count": 3
}
```

## Troubleshooting:

### "Ollama not found"
Install Ollama first: https://ollama.com/download

### "No model found"
Download a model: `ollama pull llama3.2`

### "MCP server not running"
Start it: `python server.py`

### "Ollama didn't return valid JSON"
This is normal - local models aren't perfect. You can still test manually:
```bash
curl -X POST http://localhost:8000/get_emails \
  -H "Content-Type: application/json" \
  -d '{"count": 3}'
```
