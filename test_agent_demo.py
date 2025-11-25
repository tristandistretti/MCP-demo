#!/usr/bin/env python3
"""
Simple demo of MCP + Ollama agent without authentication requirements
"""

import asyncio
import json
import subprocess
import sys
import ollama


def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Ollama is installed")
            return True
    except:
        pass
    print("✗ Ollama not found or not running")
    return False


def check_model():
    """Check if a model is available"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'llama' in result.stdout.lower() or 'mistral' in result.stdout.lower():
            print("✓ Model available")
            return True
    except:
        pass
    print("✗ No model found")
    return False


def main():
    print("=" * 70)
    print("MCP + Ollama Agent Demo (Simulated)")
    print("=" * 70)
    print()
    
    # Check prerequisites
    print("Checking prerequisites...")
    print("-" * 70)
    
    if not check_ollama():
        sys.exit(1)
    
    if not check_model():
        sys.exit(1)
    
    print()
    
    # Simulate available tools
    print("Available MCP Tools:")
    print("-" * 70)
    tools = [
        {"name": "get_emails", "description": "Get recent emails from inbox"},
        {"name": "send_email", "description": "Send an email to a recipient"}
    ]
    
    for tool in tools:
        print(f"  • {tool['name']}: {tool['description']}")
    
    print()
    
    # Test with Ollama
    print("Testing with Ollama Agent...")
    print("-" * 70)
    
    user_request = "Get my 3 most recent emails"
    print(f"User: {user_request}")
    
    tools_description = "\n".join([
        f"- {tool['name']}: {tool['description']}"
        for tool in tools
    ])
    
    try:
        full_prompt = f"""You are an AI assistant with access to these MCP tools:

{tools_description}

When the user asks you to do something, respond with ONLY a JSON object in this format:
{{"tool": "tool_name", "arguments": {{"param": "value"}}}}

User request: {user_request}

Your response (JSON only):"""
        
        print(f"\n[Ollama] Thinking...")
        response = ollama.generate(
            model='llama3.2',
            prompt=full_prompt
        )
        
        llm_response = response['response']
        print(f"\n[Ollama Response]:\n{llm_response}")
        
        # Try to parse
        llm_response = llm_response.strip()
        if llm_response.startswith('```'):
            llm_response = llm_response.split('```')[1]
            if llm_response.startswith('json'):
                llm_response = llm_response[4:]
        
        tool_call = json.loads(llm_response)
        
        print(f"\n[Ollama chose Tool]: {tool_call['tool']}")
        print(f"[Arguments]: {json.dumps(tool_call['arguments'], indent=2)}")
        print(f"\n✅ Agent successfully decided which tool to use!")
        print(f"   In a real scenario, would now call MCP server with these arguments")
        
    except json.JSONDecodeError as e:
        print(f"\n⚠️  Could not parse JSON: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    
    print()
    print("=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
