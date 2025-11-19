#!/usr/bin/env python3
"""
MCP Server for Email Operations using FastMCP
"""

from mcp.server.fastmcp import FastMCP
from msgraph import GraphServiceClient
from msgraph.generated.users.item.messages.messages_request_builder import MessagesRequestBuilder
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress
from azure.identity import DeviceCodeCredential
from azure.core.credentials import AccessToken
import os
from dotenv import load_dotenv
import sys
import pickle
from pathlib import Path
import time

load_dotenv()

# Configuration
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")

# Token cache file location
TOKEN_CACHE_FILE = Path.home() / ".email_mcp_token_cache.bin"

# Logging to stderr (stdout is for MCP protocol)
def log(msg):
    print(msg, file=sys.stderr, flush=True)

log(f"[MCP] Starting Email MCP Server")
log(f"[CONFIG] CLIENT_ID: {CLIENT_ID[:10]}...")
log(f"[CONFIG] TENANT_ID: {TENANT_ID}")

# Create FastMCP server
mcp = FastMCP("Email Server")

# Custom credential class that uses our cached token
class CachedTokenCredential:
    """Credential that uses a token from file cache"""
    
    def __init__(self, token_file):
        self.token_file = token_file
        self._load_token()
    
    def _load_token(self):
        """Load token from file"""
        if not self.token_file.exists():
            raise Exception(f"Token file not found: {self.token_file}. Run authenticate.py first.")
        
        with open(self.token_file, 'rb') as f:
            self.token_data = pickle.load(f)
        
        # Check if expired
        if self.token_data['expires_on'] <= time.time():
            raise Exception("Token expired. Run authenticate.py again.")
    
    def get_token(self, *scopes, **kwargs):
        """Return the cached token"""
        # Reload token in case it was refreshed
        self._load_token()
        
        return AccessToken(
            token=self.token_data['access_token'],
            expires_on=int(self.token_data['expires_on'])
        )

# Cached credential and client
_credential = None
_graph_client = None

def initialize_auth():
    """Initialize authentication using cached token from file"""
    global _credential, _graph_client
    
    log("[MCP] Initializing authentication from cached token...")
    
    try:
        _credential = CachedTokenCredential(TOKEN_CACHE_FILE)
        
        scopes = [
            'https://graph.microsoft.com/Mail.Read',
            'https://graph.microsoft.com/Mail.Send'
        ]
        
        _graph_client = GraphServiceClient(credentials=_credential, scopes=scopes)
        
        log("[MCP] ✓ Authentication initialized (using cached token)")
    except Exception as e:
        log(f"[ERROR] Authentication failed: {e}")
        log("[ERROR] Please run: python3 authenticate.py")
        raise

def get_graph_client():
    """Get Microsoft Graph client"""
    if _graph_client is None:
        raise Exception("Graph client not initialized. Server startup may have failed.")
    return _graph_client

@mcp.tool()
async def get_emails(count: int = 3) -> str:
    """
    Get recent emails from inbox
    
    Args:
        count: Number of emails to retrieve (default: 3, max: 10)
    
    Returns:
        JSON string with emails and count
    """
    try:
        import json
        
        count = min(count, 10)
        client = get_graph_client()
        
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            top=count,
            orderby=["receivedDateTime DESC"],
            select=["subject", "from", "receivedDateTime", "bodyPreview"]
        )
        
        request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )
        
        messages = await client.me.messages.get(request_configuration=request_config)
        
        if not messages or not messages.value:
            return json.dumps({"emails": [], "count": 0})
        
        emails = []
        for msg in messages.value:
            from_email = None
            if hasattr(msg, 'from_property') and msg.from_property:
                if hasattr(msg.from_property, 'email_address') and msg.from_property.email_address:
                    from_email = msg.from_property.email_address.address
            
            emails.append({
                "subject": msg.subject or "No subject",
                "from": from_email or "Unknown",
                "received": str(msg.received_date_time) if hasattr(msg, 'received_date_time') else "Unknown",
                "preview": msg.body_preview or ""
            })
        
        result = {
            "count": len(emails),
            "emails": emails
        }
        
        return json.dumps(result, indent=2)
    
    except Exception as e:
        import json
        log(f"[ERROR] get_emails failed: {str(e)}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def send_email(to_email: str, subject: str, body: str) -> str:
    """
    Send an email to a recipient
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        body: Email body content
    
    Returns:
        Success or error message
    """
    try:
        import json
        
        client = get_graph_client()
        
        message = Message()
        message.subject = subject
        message.body = ItemBody()
        message.body.content_type = BodyType.Text
        message.body.content = body
        
        to_recipient = Recipient()
        to_recipient.email_address = EmailAddress()
        to_recipient.email_address.address = to_email
        message.to_recipients = [to_recipient]
        
        request_body = SendMailPostRequestBody()
        request_body.message = message
        
        await client.me.send_mail.post(body=request_body)
        
        return json.dumps({
            "status": "success",
            "message": f"Email sent to {to_email}"
        })
    
    except Exception as e:
        import json
        log(f"[ERROR] send_email failed: {str(e)}")
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    try:
        initialize_auth()
        log("[MCP] Server ready")
        mcp.run()
    except Exception as e:
        log(f"[FATAL] Server startup failed: {str(e)}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)