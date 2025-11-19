#!/usr/bin/env python3
"""
Test MCP Email Server with Ollama (Free Local LLM)
"""

import requests
import json
import subprocess
import sys

def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Ollama is installed")
            return True
        else:
            print("✗ Ollama not found")
            return False
    except FileNotFoundError:
        print("✗ Ollama not installed")
        print("\nInstall with: curl -fsSL https://ollama.com/install.sh | sh")
        return False

def check_model():
    """Check if a model is available"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'llama' in result.stdout.lower() or 'mistral' in result.stdout.lower():
            print("✓ Model available")
            return True
        else:
            print("✗ No model found")
            print("\nDownload a model with: ollama pull llama3.2")
            return False
    except:
        return False

def check_server():
    """Check if FastAPI server is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            print("✓ MCP server is running")
            return True
        else:
            print("✗ MCP server not responding")
            return False
    except:
        print("✗ MCP server not running")
        print("\nStart with: python server.py")
        return False

def get_tools():
    """Get available tools from MCP server"""
    try:
        response = requests.get("http://localhost:8000/tools")
        tools = response.json()["tools"]
        print(f"✓ Found {len(tools)} tools")
        return tools
    except Exception as e:
        print(f"✗ Error getting tools: {e}")
        return []

def call_ollama(prompt, tools):
    """Call Ollama with tools"""
    try:
        import ollama
        
        # Format tools for Ollama
        tools_description = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in tools
        ])
        
        # Create prompt with tools
        full_prompt = f"""You are an AI assistant with access to these tools:

{tools_description}

When the user asks you to do something, respond with ONLY a JSON object in this format:
{{"tool": "tool_name", "arguments": {{"param": "value"}}}}

User request: {prompt}

Your response (JSON only):"""
        
        print(f"\n[Ollama] Thinking...")
        response = ollama.generate(
            model='llama3.2',
            prompt=full_prompt
        )
        
        return response['response']
    
    except ImportError:
        print("\n✗ Ollama Python package not installed")
        print("Install with: pip install ollama")
        return None
    except Exception as e:
        print(f"\n✗ Error calling Ollama: {e}")
        print("\nMake sure Ollama is running: ollama serve")
        return None

def execute_tool(tool_name, arguments):
    """Execute a tool via the MCP server"""
    try:
        response = requests.post(
            f"http://localhost:8000/{tool_name}",
            json=arguments,
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    print("=" * 60)
    print("Testing MCP Email Server with Ollama")
    print("=" * 60)
    print()
    
    # Check prerequisites
    print("Checking prerequisites...")
    print("-" * 60)
    
    if not check_ollama():
        sys.exit(1)
    
    if not check_model():
        sys.exit(1)
    
    if not check_server():
        sys.exit(1)
    
    print()
    
    # Get tools
    print("Getting available tools...")
    print("-" * 60)
    tools = get_tools()
    
    if not tools:
        sys.exit(1)
    
    for tool in tools:
        print(f"  • {tool['name']}: {tool['description']}")
    
    print()
    
    # Test with Ollama
    print("Testing with Ollama...")
    print("-" * 60)
    
    user_request = "Get my 3 most recent emails"
    print(f"User: {user_request}")
    
    llm_response = call_ollama(user_request, tools)
    
    if not llm_response:
        sys.exit(1)
    
    print(f"\n[Ollama Response]:\n{llm_response}")
    
    # Try to parse and execute
    try:
        # Extract JSON from response
        llm_response = llm_response.strip()
        if llm_response.startswith('```'):
            # Remove markdown code blocks
            llm_response = llm_response.split('```')[1]
            if llm_response.startswith('json'):
                llm_response = llm_response[4:]
        
        tool_call = json.loads(llm_response)
        
        print(f"\n[Executing Tool]: {tool_call['tool']}")
        print(f"[Arguments]: {tool_call['arguments']}")
        
        result = execute_tool(tool_call['tool'], tool_call['arguments'])
        
        print(f"\n[Result]:")
        print(json.dumps(result, indent=2))
        
    except json.JSONDecodeError:
        print("\n⚠️  Ollama didn't return valid JSON")
        print("This is normal - local models aren't always perfect at following formats")
        print("\nYou can manually test the tools:")
        print(f"  curl -X POST http://localhost:8000/get_emails \\")
        print(f"    -H 'Content-Type: application/json' \\")
        print(f"    -d '{{\"count\": 3}}'")
    
    print()
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
