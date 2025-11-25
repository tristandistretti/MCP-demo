#!/usr/bin/env python3
"""
Test MCP Email Server with Ollama using stdio transport
Communicates with the MCP server via stdin/stdout
"""

import asyncio
import json
import subprocess
import sys
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
import ollama


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


async def get_mcp_tools():
    """Get available tools from MCP server via stdio"""
    try:
        # Create stdio parameters that spawns the mcp_server.py process
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"]
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                response = await session.list_tools()
                return response.tools
    except Exception as e:
        print(f"✗ Error getting tools: {e}")
        import traceback
        traceback.print_exc()
        return []


def format_tools_for_ollama(tools):
    """Format MCP tools for Ollama prompt"""
    tools_description = "\n".join([
        f"- {tool.name}: {tool.description}"
        for tool in tools
    ])
    return tools_description


def call_ollama_with_tools(prompt, tools_description):
    """Call Ollama with available tools"""
    try:
        # Create prompt with tools
        full_prompt = f"""You are an AI assistant with access to these MCP tools:

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
    
    except Exception as e:
        print(f"\n✗ Error calling Ollama: {e}")
        print("\nMake sure Ollama is running: ollama serve")
        return None


async def call_mcp_tool(tool_name, arguments):
    """Call a tool through the MCP server via stdio"""
    try:
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"]
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                response = await session.call_tool(tool_name, arguments)
                
                # Extract content from response
                if response.content:
                    content = response.content[0]
                    if hasattr(content, 'text'):
                        return content.text
                    else:
                        return str(content)
                return str(response)
    
    except Exception as e:
        return f"Error calling tool: {str(e)}"


async def main():
    print("=" * 70)
    print("Testing MCP Email Server with Ollama (Stdio Transport)")
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
    
    # Get tools
    print("Getting available MCP tools...")
    print("-" * 70)
    tools = await get_mcp_tools()
    
    if not tools:
        print("✗ No tools found from MCP server")
        sys.exit(1)
    
    for tool in tools:
        print(f"  • {tool.name}: {tool.description}")
    
    print()
    
    # Test with Ollama
    print("Testing with Ollama Agent...")
    print("-" * 70)
    
    user_request = "Get my 3 most recent emails"
    print(f"User: {user_request}")
    
    tools_description = format_tools_for_ollama(tools)
    llm_response = call_ollama_with_tools(user_request, tools_description)
    
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
        
        result = await call_mcp_tool(tool_call['tool'], tool_call['arguments'])
        
        print(f"\n[Result]:")
        print(result)
        
    except json.JSONDecodeError:
        print("\n⚠️  Ollama didn't return valid JSON")
        print("This is normal - local models aren't always perfect at following formats")
    
    print()
    print("=" * 70)
    print("Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
