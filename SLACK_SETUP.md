# Slack Integration Setup Guide

## Overview
This guide explains how to set up your Personal Assistant to work with Slack, allowing you to chat with your AI assistant directly in Slack channels and DMs.

## Prerequisites
- Your Personal Assistant application running
- A Slack workspace where you have admin permissions
- ngrok or a public URL for local development

## Quick Setup

### 1. Create a Slack App

1. Go to [Slack App Console](https://api.slack.com/apps)
2. Click **"Create New App"**
3. Choose **"From scratch"**
4. Enter app name: `Personal Assistant`
5. Select your workspace
6. Click **"Create App"**

### 2. Configure Bot User

1. In your app settings, go to **"OAuth & Permissions"**
2. Scroll down to **"Scopes"**
3. Add these **Bot Token Scopes**:
   - `chat:write` - Send messages
   - `channels:read` - View basic channel info
   - `groups:read` - View basic private channel info
   - `im:read` - View basic info about DMs
   - `mpim:read` - View basic info about group DMs
   - `users:read` - View people in the workspace

4. Scroll up and click **"Install to Workspace"**
5. Authorize the app
6. Copy the **"Bot User OAuth Token"** (starts with `xoxb-`)

### 3. Get Signing Secret

1. In your app settings, go to **"Basic Information"**
2. Scroll down to **"App Credentials"**
3. Copy the **"Signing Secret"**

### 4. Configure Environment Variables

Add these to your `.env` file:

```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
```

### 5. Set Up Event Subscriptions

1. In your app settings, go to **"Event Subscriptions"**
2. Turn on **"Enable Events"**
3. Set **Request URL** to: `https://your-domain.com/slack/events`
   - For local development with ngrok: `https://abc123.ngrok.io/slack/events`
4. Under **"Subscribe to bot events"**, add:
   - `message.channels` - Messages in channels
   - `message.groups` - Messages in private channels
   - `message.im` - Direct messages
   - `app_mention` - When someone mentions your bot
5. Click **"Save Changes"**

### 6. Install Bot to Channels

1. Go to your Slack workspace
2. Find your bot in the Apps section
3. Click **"Add this app to a channel"**
4. Select channels where you want the bot to respond

## Local Development Setup

### Using ngrok (Recommended)

1. Install ngrok:
   ```bash
   # macOS
   brew install ngrok
   
   # Or download from https://ngrok.com/
   ```

2. Start your application:
   ```bash
   python main.py
   ```

3. In another terminal, expose your local server:
   ```bash
   ngrok http 8000
   ```

4. Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)
5. Use this URL in your Slack app's Event Subscriptions

## Testing Your Integration

### 1. Test the Setup
```bash
# Test your configuration
python test_slack.py

# Check application status
curl http://localhost:8000/slack/status
```

### 2. Test in Slack

1. **Direct Message**: Send a DM to your bot
2. **Channel Message**: @mention your bot in a channel
3. **Channel Conversation**: If the bot is in a channel, it will respond to all messages

### Example Interactions:

- **"Hello!"** → Bot responds with AI-generated greeting
- **"What's the weather like?"** → Bot provides weather info
- **"Help me with Python"** → Bot gives programming assistance
- **"@YourBot explain quantum physics"** → Bot provides explanation

## Bot Permissions

### Required Scopes:
- `chat:write` - Send messages as the bot
- `channels:read` - Read basic channel information
- `groups:read` - Read private channel information
- `im:read` - Read direct message information
- `users:read` - Read user information

### Optional Scopes (for enhanced features):
- `files:write` - Upload files
- `reactions:write` - Add emoji reactions
- `channels:history` - Read message history

## Troubleshooting

### Common Issues

1. **Bot not responding to messages**
   - Check that Event Subscriptions URL is correct
   - Verify bot token and signing secret
   - Ensure bot is added to the channel

2. **"Slack integration not configured" error**
   - Check environment variables are set correctly
   - Restart your application after adding env vars

3. **ngrok URL verification fails**
   - Make sure your application is running before setting the URL
   - Check that the URL ends with `/slack/events`

### Debug Commands

```bash
# Check environment
python debug_env.py

# Test Slack integration
python test_slack.py

# Check server logs
python main.py  # Look for Slack-related logs
```

### Webhook URL Verification

Slack will send a verification challenge to your webhook URL. The application automatically handles this, but ensure:

1. Your server is running when you set the Event Subscriptions URL
2. The URL is publicly accessible
3. The endpoint responds within 3 seconds

## Advanced Features

### Custom Slash Commands (Optional)

1. In your app settings, go to **"Slash Commands"**
2. Click **"Create New Command"**
3. Set command: `/assistant`
4. Set Request URL: `https://your-domain.com/slack/interactive`
5. Add description and usage hints

### Interactive Components (Optional)

The application includes support for interactive components like buttons and modals. Configure the **Interactivity & Shortcuts** request URL to: `https://your-domain.com/slack/interactive`

## Security Considerations

- Keep your bot token and signing secret secure
- The application verifies all incoming requests from Slack
- Bot tokens should start with `xoxb-`
- Never commit tokens to version control

## Production Deployment

### Environment Variables for Production:
```bash
SLACK_BOT_TOKEN=xoxb-your-production-token
SLACK_SIGNING_SECRET=your-production-secret
```

### Deployment Platforms:
- **Heroku**: Add environment variables in dashboard
- **Railway**: Set in environment settings
- **AWS/GCP**: Use their respective secret management services

## Support

If you encounter issues:

1. Check the [Slack API documentation](https://api.slack.com/)
2. Use the test scripts: `python test_slack.py`
3. Monitor application logs for error messages
4. Verify webhook URLs are accessible from the internet 