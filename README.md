# Personal Assistant API

A complete AI-powered personal assistant API using FastAPI and Hypermode with RAG capabilities.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `env.example` to `.env` and fill in your credentials:
```bash
cp env.example .env
```

Required environment variables:
- `HYPERMODE_API_KEY`: Your Hypermode API key
- `OPENAI_API_KEY`: Your OpenAI API key (optional, for enhanced RAG features)
- `OPENROUTER_API_KEY`: Your OpenRouter API key (optional, alternative to OpenAI)

### 3. Run Locally
```bash
python main.py
```

The server will start on `http://localhost:8000`

## 🔧 Setup Instructions

### Twilio Setup
1. Create a Twilio account at [twilio.com](https://twilio.com)
2. Get a phone number
3. Configure webhook URL in Twilio Console:
   - Go to Phone Numbers → Manage → Active numbers
   - Set webhook URL to: `https://your-domain.com/sms`
   - Method: POST

### Hypermode Setup
1. Get your API key from [hypertmode.com](https://hypertmode.com)
2. Add to `.env` file

### Local Development with ngrok
For testing locally, use ngrok to expose your local server:

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from ngrok.com

# Expose local server
ngrok http 8000

# Use the ngrok URL in Twilio webhook configuration
```

## 📡 API Endpoints

### POST /sms
Handles incoming SMS from Twilio webhook.

**Parameters:**
- `Body`: Message content
- `From`: Sender phone number
- `To`: Recipient phone number

**Response:** TwiML XML with agent response

### POST /respond
Send outbound SMS messages (optional).

**Parameters:**
- `to`: Recipient phone number
- `message`: Message content

### GET /
Health check endpoint.

## 🔄 Core Flow

1. **User sends SMS** to your Twilio number
2. **Twilio triggers webhook** to your `/sms` endpoint
3. **Backend processes** the message through Hypermode
4. **Agent responds** via Twilio SMS back to user

## 🧪 Testing

### Test the webhook locally:
```bash
curl -X POST http://localhost:8000/sms \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Body=What's the weather in SF?&From=+1234567890&To=+0987654321"
```

### Test outbound SMS:
```bash
curl -X POST http://localhost:8000/respond \
  -H "Content-Type: application/json" \
  -d '{"to": "+1234567890", "message": "Test message"}'
```

## 🚀 Deployment

### Option 1: Render (Recommended)
1. Connect your GitHub repo to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python main.py`
5. Add environment variables in Render dashboard

### Option 2: Railway
1. Connect your GitHub repo to Railway
2. Railway will auto-detect Python
3. Add environment variables in Railway dashboard

### Option 3: Heroku
1. Create `Procfile`:
```
web: python main.py
```
2. Deploy to Heroku
3. Add environment variables in Heroku dashboard

## 🔧 Customization

### Adding Tools
Extend the `HypermodeClient.generate_response()` method to include:
- Weather API calls
- Database queries
- External service integrations

### Memory/Context
Add conversation history to maintain context:
```python
# Store conversation history
conversation_history = {
    "user_phone": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
}
```

### RAG Integration
Add LlamaIndex for document retrieval:
```python
from llama_index import VectorStoreIndex, SimpleDirectoryReader

# Load documents
documents = SimpleDirectoryReader('data/').load_data()
index = VectorStoreIndex.from_documents(documents)

# Query in response generation
response = index.as_query_engine().query(user_message)
```

## 📝 Example Use Cases

### Weather Assistant
User: "What's the weather in San Francisco?"
Agent: "Currently 72°F and sunny in San Francisco. Perfect weather for outdoor activities!"

### Task Assistant
User: "Remind me to call mom tomorrow"
Agent: "I'll remind you to call mom tomorrow. I've set a reminder for you!"

### General Q&A
User: "What's the capital of France?"
Agent: "The capital of France is Paris. It's known as the 'City of Light' and is famous for its culture, cuisine, and landmarks like the Eiffel Tower."

## 🛠️ Troubleshooting

### Common Issues

1. **Webhook not receiving messages**
   - Check Twilio webhook URL configuration
   - Ensure server is publicly accessible
   - Verify ngrok is running (for local testing)

2. **Hypermode API errors**
   - Verify API key is correct
   - Check API rate limits
   - Ensure proper JSON formatting

3. **Twilio authentication errors**
   - Verify Account SID and Auth Token
   - Check phone number format (+1XXXXXXXXXX)

### Logs
Check application logs for detailed error information:
```bash
# View logs in real-time
tail -f logs/app.log
```

## 📚 Next Steps

- Add conversation memory
- Integrate with external APIs (weather, calendar, etc.)
- Add user authentication
- Implement rate limiting
- Add analytics and monitoring
- Create admin dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details. 