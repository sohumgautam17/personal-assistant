from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import Response
import os
import httpx
from dotenv import load_dotenv
from twilio.twiml import MessagingResponse
import logging
from typing import Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SMS Agent Stack", version="1.0.0")

# Configuration
HYPERTMODE_API_KEY = os.getenv("HYPERTMODE_API_KEY")
HYPERTMODE_BASE_URL = os.getenv("HYPERTMODE_BASE_URL", "https://api.hypertmode.com")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

class HypermodeClient:
    def __init__(self, api_key: Optional[str], base_url: str):
        if not api_key:
            raise ValueError("HYPERTMODE_API_KEY is required")
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_response(self, message: str, user_phone: str) -> str:
        """Generate response using Hypermode API"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful SMS assistant. Keep responses concise and friendly. You can help with weather, general questions, and basic tasks."
                        },
                        {
                            "role": "user", 
                            "content": f"User ({user_phone}) asks: {message}"
                        }
                    ],
                    "model": "gpt-4",
                    "max_tokens": 150,
                    "temperature": 0.7
                }
                
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Hypermode API error: {response.status_code} - {response.text}")
                    return "Sorry, I'm having trouble processing your request right now."
                    
        except Exception as e:
            logger.error(f"Error calling Hypermode API: {e}")
            return "Sorry, I'm experiencing technical difficulties. Please try again later."

# Initialize Hypermode client
try:
    hypermode_client = HypermodeClient(HYPERTMODE_API_KEY, HYPERTMODE_BASE_URL)
except ValueError as e:
    logger.error(f"Failed to initialize Hypermode client: {e}")
    hypermode_client = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "SMS Agent Stack is running!", "status": "healthy"}

@app.post("/sms")
async def receive_sms(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(...)
):
    """
    Handle incoming SMS from Twilio webhook
    """
    logger.info(f"Received SMS from {From}: {Body}")
    
    try:
        if not hypermode_client:
            twiml = MessagingResponse()
            twiml.message("Sorry, the AI assistant is not properly configured. Please contact support.")
            return Response(
                content=str(twiml),
                media_type="application/xml"
            )
        
        # Generate response using Hypermode
        agent_response = await hypermode_client.generate_response(Body, From)
        
        # Create TwiML response
        twiml = MessagingResponse()
        twiml.message(agent_response)
        
        logger.info(f"Sending response to {From}: {agent_response}")
        
        return Response(
            content=str(twiml),
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Error processing SMS: {e}")
        twiml = MessagingResponse()
        twiml.message("Sorry, I encountered an error. Please try again.")
        return Response(
            content=str(twiml),
            media_type="application/xml"
        )

@app.post("/respond")
async def send_outbound_sms(
    to: str,
    message: str
):
    """
    Optional endpoint to send outbound SMS messages
    Requires Twilio credentials to be configured
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        raise HTTPException(status_code=500, detail="Twilio credentials not configured")
    
    try:
        from twilio.rest import Client
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        twilio_message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to
        )
        
        logger.info(f"Sent outbound SMS to {to}: {message}")
        return {"status": "sent", "message_sid": twilio_message.sid}
        
    except Exception as e:
        logger.error(f"Error sending outbound SMS: {e}")
        raise HTTPException(status_code=500, detail="Failed to send SMS")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 