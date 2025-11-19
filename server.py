#!/usr/bin/env python3
"""
Minimal MCP Server for Email Operations
Uses FastAPI with MCP wrapper
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from msgraph import GraphServiceClient
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from azure.identity import InteractiveBrowserCredential
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Email MCP Server", version="1.0.0")

# Configuration
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")

print(f"[CONFIG] CLIENT_ID: {CLIENT_ID[:10]}...")
print(f"[CONFIG] TENANT_ID: {TENANT_ID}")

# Cached credential
_credential = None

def get_graph_client():
    """Get Microsoft Graph client"""
    global _credential
    if _credential is None:
        _credential = InteractiveBrowserCredential(
            client_id=CLIENT_ID,
            tenant_id=TENANT_ID,
        )
    scopes = ['https://graph.microsoft.com/Mail.Read', 
              'https://graph.microsoft.com/Mail.Send']
    return GraphServiceClient(credentials=_credential, scopes=scopes)

# Request models
class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str

class GetEmailsRequest(BaseModel):
    count: Optional[int] = 3

# MCP Tools definition
@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": "get_emails",
                "description": "Get recent emails from inbox",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "count": {
                            "type": "number",
                            "description": "Number of emails to retrieve (default: 3)"
                        }
                    }
                }
            },
            {
                "name": "send_email",
                "description": "Send an email",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to_email": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"}
                    },
                    "required": ["to_email", "subject", "body"]
                }
            }
        ]
    }

# Route 1: Get Emails
@app.post("/get_emails")
async def get_emails(request: GetEmailsRequest):
    """Get recent emails from inbox"""
    try:
        from msgraph.generated.users.item.messages.messages_request_builder import MessagesRequestBuilder
        
        count = min(request.count or 3, 10)
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
            return {"emails": [], "count": 0}
        
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
        
        return {"emails": emails, "count": len(emails)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route 2: Send Email
@app.post("/send_email")
async def send_email(request: SendEmailRequest):
    """Send an email"""
    try:
        client = get_graph_client()
        
        message = Message()
        message.subject = request.subject
        message.body = ItemBody()
        message.body.content_type = BodyType.Text
        message.body.content = request.body
        
        to_recipient = Recipient()
        to_recipient.email_address = EmailAddress()
        to_recipient.email_address.address = request.to_email
        message.to_recipients = [to_recipient]
        
        request_body = SendMailPostRequestBody()
        request_body.message = message
        
        await client.me.send_mail.post(body=request_body)
        
        return {
            "status": "success",
            "message": f"Email sent to {request.to_email}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "name": "Email MCP Server",
        "version": "1.0.0",
        "routes": {
            "/tools": "List MCP tools",
            "/get_emails": "Get recent emails",
            "/send_email": "Send an email"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
