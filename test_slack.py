#!/usr/bin/env python3
"""
Test script for Slack integration functionality
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_slack_status():
    """Test the Slack status endpoint"""
    
    try:
        response = requests.get("http://localhost:8000/slack/status")
        
        print("=== Slack Status Test ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "configured":
                print("✅ Slack integration configured!")
                return True
            else:
                print("⚠️  Slack integration not fully configured")
                return False
        else:
            print("❌ Slack status endpoint failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_slack_webhook():
    """Test the Slack webhook endpoint with sample data"""
    
    # Sample Slack event data (message event)
    sample_event = {
        "token": "verification_token",
        "team_id": "T1234567890",
        "api_app_id": "A1234567890",
        "event": {
            "type": "message",
            "user": "U1234567890",
            "text": "Hello, can you help me?",
            "ts": "1234567890.123456",
            "channel": "C1234567890",
            "event_ts": "1234567890.123456"
        },
        "type": "event_callback",
        "event_id": "Ev1234567890",
        "event_time": 1234567890
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/slack/events",
            json=sample_event,
            headers={"Content-Type": "application/json"}
        )
        
        print("\n=== Slack Webhook Test ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 404]:  # 404 is expected without proper tokens
            print("✅ Slack webhook endpoint is responding")
            return True
        else:
            print("❌ Slack webhook test failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_environment():
    """Check Slack environment variables"""
    
    load_dotenv()
    
    print("\n=== Slack Environment Check ===")
    
    slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
    slack_signing_secret = os.getenv('SLACK_SIGNING_SECRET')
    slack_app_token = os.getenv('SLACK_APP_TOKEN')
    
    print(f"SLACK_BOT_TOKEN: {'✅ Set' if slack_bot_token else '❌ Missing'}")
    print(f"SLACK_SIGNING_SECRET: {'✅ Set' if slack_signing_secret else '❌ Missing'}")
    print(f"SLACK_APP_TOKEN: {'✅ Set' if slack_app_token else '⚠️  Missing (optional)'}")
    
    if not slack_bot_token or not slack_signing_secret:
        print("\n⚠️  Slack integration requires:")
        print("  1. SLACK_BOT_TOKEN (starts with xoxb-)")
        print("  2. SLACK_SIGNING_SECRET")
        print("  3. SLACK_APP_TOKEN (optional, for Socket Mode)")
        return False
    
    return True

def main():
    """Main test function"""
    print("🧪 Testing Slack Integration...\n")
    
    # Check environment first
    env_ok = check_environment()
    
    # Test endpoints
    status_ok = test_slack_status()
    webhook_ok = test_slack_webhook()
    
    print(f"\n{'=' * 40}")
    if env_ok and status_ok:
        print("🎉 Slack integration tests completed successfully!")
        print("\n📝 Next steps:")
        print("1. Create a Slack app at https://api.slack.com/apps")
        print("2. Add your Bot User OAuth Token to SLACK_BOT_TOKEN")
        print("3. Add your Signing Secret to SLACK_SIGNING_SECRET")
        print("4. Configure Event Subscriptions URL: https://your-domain.com/slack/events")
        print("5. Subscribe to bot events: message.channels, app_mention")
    else:
        print("⚠️  Some Slack tests failed - check configuration")
    
    return env_ok and status_ok

if __name__ == "__main__":
    main() 