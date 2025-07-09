from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import Response
import os
import httpx
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
import logging
from typing import Optional
# RAG imports - only import when actually needed to avoid circular import issues
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
# from llama_index.embeddings.openai import OpenAIEmbedding  
# from llama_index.llms.openai import OpenAI
import asyncio

# Load environment variables
load_dotenv()

# Set OpenRouter API key if not already set (for easy integration)
if not os.getenv("OPENROUTER_API_KEY"):
    os.environ["OPENROUTER_API_KEY"] = "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"
    os.environ["OPENROUTER_BASE_URL"] = "https://openrouter.ai/api/v1"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SMS Agent Stack with RAG", version="1.0.0")

# Configuration
HYPERTMODE_API_KEY = os.getenv("HYPERTMODE_API_KEY")
HYPERTMODE_BASE_URL = os.getenv("HYPERTMODE_BASE_URL", "https://api.hypertmode.com")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# RAG Configuration
class RAGManager:
    """Manages document loading and querying with SimpleRAG (OpenRouter-based)"""
    
    def __init__(self, data_dir: str = "data/"):
        self.data_dir = data_dir
        self.rag = None
        self._initialize_rag()
    
    def _initialize_rag(self):
        """Initialize RAG system using SimpleRAG with OpenRouter"""
        try:
            # Check if we have OpenRouter API key (prefer over OpenAI)
            if OPENROUTER_API_KEY:
                logger.info("Using OpenRouter for RAG functionality")
                from simple_rag import SimpleRAG
                self.rag = SimpleRAG(OPENROUTER_API_KEY, OPENROUTER_BASE_URL)
                return
            
            # Fallback to basic functionality if no API keys
            else:
                logger.warning("No OpenRouter API key found - RAG features will be disabled")
                self.rag = None
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG: {e}")
            self.rag = None
    
    async def query_documents(self, query: str) -> Optional[str]:
        """Query the document index for relevant information"""
        if not self.rag:
            return None
        
        try:
            response = await self.rag.query(query)
            return response
        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            return None
    
    def get_status(self) -> dict:
        """Get RAG system status"""
        if self.rag:
            status = self.rag.get_status()
            status["provider"] = "OpenRouter (SimpleRAG)"
            return status
        else:
            return {
                "initialized": False,
                "provider": "None",
                "using_openrouter": bool(OPENROUTER_API_KEY),
                "data_directory": os.path.exists(self.data_dir)
            }
    
    def reload_documents(self):
        """Reload documents and reinitialize the index"""
        if self.rag:
            return self.rag.reload_documents()
        else:
            self._initialize_rag()
            return "RAG reinitialized" if self.rag else "Failed to initialize RAG"

class HypermodeClient:
    def __init__(self, api_key: Optional[str], base_url: str, rag_manager: Optional[RAGManager] = None):
        if not api_key:
            raise ValueError("HYPERTMODE_API_KEY is required")
        self.api_key = api_key
        self.base_url = base_url
        self.rag_manager = rag_manager
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Default model configuration
        self.default_model = "gpt-4"
        self.default_max_tokens = 200
        self.default_temperature = 0.7
        
        # Available models for different use cases
        self.models = {
            "fast": "gpt-3.5-turbo",
            "balanced": "gpt-4",
            "premium": "gpt-4",
            "smart": "gpt-4-turbo"
        }
    
    def _get_model_for_query(self, message: str) -> str:
        """Select appropriate model based on query complexity"""
        # Simple heuristic: longer messages or complex queries use better models
        if len(message) > 100 or any(keyword in message.lower() for keyword in 
                                   ['explain', 'analyze', 'complex', 'detailed', 'how does', 'why']):
            return self.models["premium"]
        elif len(message) > 50:
            return self.models["balanced"]
        else:
            return self.models["fast"]
    
    async def generate_response(self, message: str, user_phone: str, model: Optional[str] = None, 
                              use_streaming: bool = False) -> str:
        """Generate response using Hypermode API with RAG enhancement"""
        try:
            # First, try to get relevant information from documents
            context = ""
            if self.rag_manager:
                rag_response = await self.rag_manager.query_documents(message)
                if rag_response:
                    context = f"\n\nRelevant information from knowledge base:\n{rag_response}"
                    logger.info(f"RAG context found for query: {message[:50]}...")
            
            # Select model if not provided
            selected_model = model or self._get_model_for_query(message)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                system_content = """You are a helpful and intelligent SMS assistant. Keep responses concise but informative, 
                ideally under 160 characters for SMS compatibility. You can help with weather, general questions, calculations, 
                definitions, and basic tasks. If provided with relevant information from a knowledge base, incorporate it 
                naturally and accurately into your response. Be friendly and professional."""
                
                user_content = f"User ({user_phone}) asks: {message}{context}"
                
                payload = {
                    "messages": [
                        {
                            "role": "system",
                            "content": system_content
                        },
                        {
                            "role": "user", 
                            "content": user_content
                        }
                    ],
                    "model": selected_model,
                    "max_tokens": self.default_max_tokens,
                    "temperature": self.default_temperature,
                    "stream": use_streaming,
                    "presence_penalty": 0.1,  # Reduce repetition
                    "frequency_penalty": 0.1   # Encourage variety
                }
                
                # Try multiple endpoints (Hypermode API variations)
                endpoints = [
                    f"{self.base_url}/chat/completions",
                    f"{self.base_url}/api/v1/chat/completions"
                ]
                
                last_error = None
                for endpoint in endpoints:
                    try:
                        logger.info(f"Trying Hypermode endpoint: {endpoint}")
                        
                        response = await client.post(
                            endpoint,
                            headers=self.headers,
                            json=payload,
                            timeout=30.0
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Handle different response formats
                            if "choices" in data and len(data["choices"]) > 0:
                                content = data["choices"][0]["message"]["content"]
                                logger.info(f"Hypermode response received: {content[:50]}...")
                                return content
                            else:
                                logger.warning(f"Unexpected response format from {endpoint}")
                                continue
                                
                        elif response.status_code == 401:
                            logger.error("Hypermode API authentication failed - check API key")
                            return "Sorry, there's an authentication issue with the AI service."
                            
                        elif response.status_code == 429:
                            logger.warning("Hypermode API rate limit reached")
                            return "Sorry, the AI service is currently busy. Please try again in a moment."
                            
                        elif response.status_code == 500:
                            logger.error(f"Hypermode API server error: {response.text}")
                            last_error = "Server error"
                            continue
                            
                        else:
                            logger.warning(f"Hypermode API error {response.status_code} from {endpoint}: {response.text}")
                            last_error = f"HTTP {response.status_code}"
                            continue
                            
                    except httpx.TimeoutException:
                        logger.warning(f"Timeout calling {endpoint}")
                        last_error = "Timeout"
                        continue
                    except httpx.ConnectError:
                        logger.warning(f"Connection error to {endpoint}")
                        last_error = "Connection error"
                        continue
                    except Exception as e:
                        logger.warning(f"Error calling {endpoint}: {e}")
                        last_error = str(e)
                        continue
                
                # If all endpoints failed
                logger.error(f"All Hypermode endpoints failed. Last error: {last_error}")
                return "Sorry, I'm having trouble connecting to the AI service right now. Please try again later."
                    
        except Exception as e:
            logger.error(f"Unexpected error in Hypermode client: {e}")
            return "Sorry, I'm experiencing technical difficulties. Please try again later."
    
    async def generate_streaming_response(self, message: str, user_phone: str, model: Optional[str] = None):
        """Generate streaming response for real-time applications"""
        # This would be used for web interfaces or real-time chat
        # For SMS, we still need complete responses
        return await self.generate_response(message, user_phone, model, use_streaming=False)
    
    async def test_connection(self) -> dict:
        """Test Hypermode API connection and return status"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                test_payload = {
                    "messages": [{"role": "user", "content": "Hello"}],
                    "model": self.models["fast"],
                    "max_tokens": 10
                }
                
                endpoints = [
                    f"{self.base_url}/chat/completions",
                    f"{self.base_url}/api/v1/chat/completions"
                ]
                
                for endpoint in endpoints:
                    try:
                        response = await client.post(
                            endpoint,
                            headers=self.headers,
                            json=test_payload,
                            timeout=10.0
                        )
                        
                        if response.status_code == 200:
                            return {
                                "status": "connected",
                                "endpoint": endpoint,
                                "model": self.models["fast"]
                            }
                        elif response.status_code == 401:
                            return {
                                "status": "authentication_failed",
                                "endpoint": endpoint,
                                "error": "Invalid API key"
                            }
                    except Exception:
                        continue
                
                return {
                    "status": "connection_failed",
                    "error": "All endpoints unreachable"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Initialize RAG Manager
rag_manager = RAGManager()

# Initialize Hypermode client with RAG
try:
    hypermode_client = HypermodeClient(HYPERTMODE_API_KEY, HYPERTMODE_BASE_URL, rag_manager)
except ValueError as e:
    logger.error(f"Failed to initialize Hypermode client: {e}")
    hypermode_client = None

@app.get("/")
async def root():
    """Health check endpoint"""
    rag_status = "enabled" if rag_manager.rag else "disabled"
    hypermode_status = "configured" if hypermode_client else "not_configured"
    
    return {
        "message": "SMS Agent Stack with RAG and Hypermode is running!", 
        "status": "healthy",
        "services": {
            "rag": rag_status,
            "hypermode": hypermode_status,
            "twilio": "configured" if all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]) else "not_configured"
        },
        "endpoints": {
            "sms_webhook": "/sms",
            "rag_status": "/rag/status",
            "rag_reload": "/rag/reload",
            "hypermode_status": "/hypermode/status",
            "hypermode_models": "/hypermode/models",
            "hypermode_test": "/hypermode/test"
        }
    }

@app.get("/rag/status")
async def rag_status():
    """Check RAG system status"""
    return rag_manager.get_status()

@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check environment variables"""
    return {
        "OPENROUTER_API_KEY": bool(OPENROUTER_API_KEY),
        "OPENROUTER_API_KEY_LENGTH": len(OPENROUTER_API_KEY) if OPENROUTER_API_KEY else 0,
        "OPENROUTER_BASE_URL": OPENROUTER_BASE_URL,
        "OPENAI_API_KEY": bool(OPENAI_API_KEY),
        "data_directory_exists": os.path.exists("data"),
        "data_files": os.listdir("data") if os.path.exists("data") else []
    }

@app.post("/rag/reload")
async def reload_rag():
    """Reload RAG system with updated documents"""
    try:
        result = rag_manager.reload_documents()
        status = "enabled" if rag_manager.rag else "disabled"
        return {"status": "reloaded", "rag_status": status, "message": result}
    except Exception as e:
        logger.error(f"Error reloading RAG: {e}")
        raise HTTPException(status_code=500, detail="Failed to reload RAG system")

@app.get("/hypermode/status")
async def hypermode_status():
    """Check Hypermode API connection status"""
    if not hypermode_client:
        return {"status": "not_configured", "error": "Hypermode client not initialized"}
    
    try:
        status = await hypermode_client.test_connection()
        return status
    except Exception as e:
        logger.error(f"Error testing Hypermode connection: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/hypermode/models")
async def hypermode_models():
    """Get available Hypermode models"""
    if not hypermode_client:
        raise HTTPException(status_code=500, detail="Hypermode client not configured")
    
    return {
        "available_models": hypermode_client.models,
        "default_model": hypermode_client.default_model,
        "configuration": {
            "max_tokens": hypermode_client.default_max_tokens,
            "temperature": hypermode_client.default_temperature
        }
    }

@app.post("/hypermode/test")
async def test_hypermode(
    message: str = "Hello, this is a test message",
    model: Optional[str] = None
):
    """Test Hypermode API with a custom message"""
    if not hypermode_client:
        raise HTTPException(status_code=500, detail="Hypermode client not configured")
    
    try:
        response = await hypermode_client.generate_response(
            message, 
            "test_user", 
            model
        )
        return {
            "status": "success",
            "test_message": message,
            "model_used": model or hypermode_client._get_model_for_query(message),
            "response": response
        }
    except Exception as e:
        logger.error(f"Error testing Hypermode: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

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