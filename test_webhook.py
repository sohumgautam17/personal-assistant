#!/usr/bin/env python3
"""
Test script for the SMS webhook endpoint
Run this to test your webhook locally without Twilio
"""

import requests
import json

def test_sms_webhook():
    """Test the /sms endpoint with sample data"""
    
    # Sample Twilio webhook data
    webhook_data = {
        "Body": "What's the weather in San Francisco?",
        "From": "+1234567890",
        "To": "+0987654321"
    }
    
    # Test the webhook endpoint
    try:
        response = requests.post(
            "http://localhost:8000/sms",
            data=webhook_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body:\n{response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
        else:
            print("❌ Webhook test failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_outbound_sms():
    """Test the /respond endpoint"""
    
    test_data = {
        "to": "+1234567890",
        "message": "This is a test message from the SMS Agent Stack!"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/respond",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nOutbound SMS Test:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Outbound SMS test successful!")
        else:
            print("❌ Outbound SMS test failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health_check():
    """Test the health check endpoint"""
    
    try:
        response = requests.get("http://localhost:8000/")
        
        print(f"\nHealth Check Test:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Health check successful!")
        else:
            print("❌ Health check failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Testing SMS Agent Stack Webhook")
    print("=" * 40)
    
    # Test health check first
    test_health_check()
    
    # Test SMS webhook
    test_sms_webhook()
    
    # Test outbound SMS (optional - requires Twilio credentials)
    # test_outbound_sms()
    
    print("\n" + "=" * 40)
    print("🎉 Testing complete!") 