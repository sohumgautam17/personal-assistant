# Personal Assistant API

A complete AI-powered personal assistant with Slack integration, using FastAPI, Hypermode, and RAG capabilities.

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
- `SLACK_BOT_TOKEN`: Your Slack bot token (for Slack integration)
- `SLACK_SIGNING_SECRET`: Your Slack app signing secret

Optional environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key (for enhanced RAG features)
- `OPENROUTER_API_KEY`: Your OpenRouter API key (alternative to OpenAI)
- `SLACK_APP_TOKEN`: Your Slack app token (for Socket Mode)

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

### Slack Setup
1. Create a Slack app at [api.slack.com/apps](https://api.slack.com/apps)
2. Get your Bot User OAuth Token and Signing Secret
3. Configure Event Subscriptions URL: `https://your-domain.com/slack/events`
4. Add required bot scopes: `chat:write`, `channels:read`, `im:read`, `users:read`
5. Install the app to your workspace

For detailed setup instructions, see [SLACK_SETUP.md](SLACK_SETUP.md)

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

### GET /
Health check endpoint - shows status of all integrated services.

### POST /slack/events
Handles incoming Slack events (messages, mentions, etc.).

**Headers:**
- `X-Slack-Signature`: Slack signature for verification
- `X-Slack-Request-Timestamp`: Request timestamp

**Response:** Slack-formatted response

### POST /slack/interactive
Handles Slack interactive components (buttons, modals, etc.).

### GET /slack/status
Check Slack integration status and configuration.

### POST /hypermode/test
Test Hypermode AI responses directly.

**Parameters:**
- `message`: Message to send to AI

### GET /hypermode/status
Check Hypermode API connection status.

### GET /rag/status
Check RAG system status and document loading.

## 🔄 Core Flow

1. **User sends message** in Slack (channel, DM, or @mention)
2. **Slack triggers webhook** to your `/slack/events` endpoint
3. **Backend processes** the message through Hypermode with RAG
4. **Agent responds** directly in Slack thread

## 🧪 Testing

### Test Slack integration:
```bash
# Run the Slack test suite
python test_slack.py

# Check Slack status
curl http://localhost:8000/slack/status
```

### Test Hypermode AI:
```bash
# Test AI responses directly
curl -X POST http://localhost:8000/hypermode/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### Test in Slack:
1. Send a direct message to your bot
2. @mention your bot in a channel
3. Chat naturally - the bot will respond with AI-generated answers

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

### In Slack Channels
**User**: "@assistant What's the weather in San Francisco?"  
**Bot**: "Currently 72°F and sunny in San Francisco. Perfect weather for outdoor activities!"

### Direct Messages
**User**: "Help me write a Python function to sort a list"  
**Bot**: "Here's a simple Python function to sort a list: `def sort_list(items): return sorted(items)`. You can also use `list.sort()` for in-place sorting."

### Team Collaboration
**User**: "Explain machine learning to the team"  
**Bot**: "Machine learning is a subset of AI that enables computers to learn and improve from data without explicit programming. It's like teaching a computer to recognize patterns..."

### Knowledge Base Integration (with RAG)
**User**: "How do I deploy this app?"  
**Bot**: *[Searches your documents]* "Based on your documentation, you can deploy using Railway or Heroku. Here are the steps..."

## 🛠️ Troubleshooting

### Common Issues

1. **Slack bot not responding**
   - Check Event Subscriptions URL is correct and accessible
   - Verify bot token and signing secret are set
   - Ensure bot is added to the channel or has DM permissions
   - Check that your server is publicly accessible via ngrok

2. **Hypermode API errors**
   - Verify API key is correct
   - Check API rate limits
   - Ensure proper JSON formatting

3. **Slack authentication errors**
   - Verify bot token starts with `xoxb-`
   - Check signing secret is correct
   - Ensure bot has required scopes

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