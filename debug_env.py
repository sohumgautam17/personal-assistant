#!/usr/bin/env python3
"""
Debug script to check environment variables and configuration
"""

import os
from dotenv import load_dotenv

def debug_environment():
    """Debug environment variables"""
    
    # Load environment variables
    load_dotenv()
    
    print("=== Environment Debug ===")
    
    # Check Hypermode
    hypermode_key = os.getenv('HYPERMODE_API_KEY')
    print(f"HYPERMODE_API_KEY: {'✅ Set' if hypermode_key else '❌ Missing'}")
    
    # Check Twilio
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    
    print(f"TWILIO_ACCOUNT_SID: {'✅ Set' if twilio_sid else '❌ Missing'}")
    print(f"TWILIO_AUTH_TOKEN: {'✅ Set' if twilio_token else '❌ Missing'}")
    print(f"TWILIO_PHONE_NUMBER: {'✅ Set' if twilio_phone else '❌ Missing'}")
    
    # Check OpenAI (optional)
    openai_key = os.getenv('OPENAI_API_KEY')
    print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '⚠️  Missing (RAG features disabled)'}")
    
    print("\n=== System Status ===")
    print("Environment check complete!")

if __name__ == "__main__":
    debug_environment() 