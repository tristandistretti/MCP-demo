#!/usr/bin/env python3
"""
One-time authentication script to cache tokens in a file
Run this before starting the MCP server
"""

from azure.identity import DeviceCodeCredential, TokenCachePersistenceOptions
from dotenv import load_dotenv
import os
import json
import pickle
from pathlib import Path

load_dotenv()

CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")

# Token cache file location
TOKEN_CACHE_FILE = Path.home() / ".email_mcp_token_cache.bin"

def authenticate():
    """Perform device code authentication and save the token to a file"""
    print("Starting authentication...")
    print("You will need to sign in via your browser.")
    print()
    
    # Check if we already have a valid token
    if TOKEN_CACHE_FILE.exists():
        try:
            with open(TOKEN_CACHE_FILE, 'rb') as f:
                token_data = pickle.load(f)
            
            import time
            if token_data['expires_on'] > time.time():
                remaining = int((token_data['expires_on'] - time.time()) / 60)
                print(f"✓ Valid token already exists. Expires in {remaining} minutes.")
                print("No need to authenticate again!")
                return
        except Exception as e:
            print(f"⚠️  Could not read existing token: {e}")
            print("Will authenticate again...")
    
    credential = DeviceCodeCredential(
        client_id=CLIENT_ID,
        tenant_id=TENANT_ID
    )
    
    scopes = [
        'https://graph.microsoft.com/Mail.Read',
        'https://graph.microsoft.com/Mail.Send'
    ]
    
    print("Acquiring token...")
    token = credential.get_token(*scopes)
    
    # Save token and credential info
    token_data = {
        'access_token': token.token,
        'expires_on': token.expires_on,
        'client_id': CLIENT_ID,
        'tenant_id': TENANT_ID
    }
    
    with open(TOKEN_CACHE_FILE, 'wb') as f:
        pickle.dump(token_data, f)
    
    print()
    print("✓ Authentication successful!")
    print(f"✓ Token saved to: {TOKEN_CACHE_FILE}")
    print()
    print("You can now start your MCP server. The token will be valid for about 1 hour.")
    print("When it expires, run this script again to refresh.")
    
    return token

def check_token():
    """Check if a valid token exists"""
    if not TOKEN_CACHE_FILE.exists():
        print("❌ No token found. Please authenticate first.")
        return False
    
    try:
        with open(TOKEN_CACHE_FILE, 'rb') as f:
            token_data = pickle.load(f)
        
        import time
        if token_data['expires_on'] > time.time():
            remaining = int((token_data['expires_on'] - time.time()) / 60)
            print(f"✓ Valid token found. Expires in {remaining} minutes.")
            return True
        else:
            print("⚠️  Token expired. Please authenticate again.")
            return False
    except Exception as e:
        print(f"❌ Error reading token: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_token()
    else:
        try:
            authenticate()
        except Exception as e:
            print(f"Authentication failed: {e}")
            import traceback
            traceback.print_exc()