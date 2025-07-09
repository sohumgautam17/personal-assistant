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
    
    # Check OpenAI (optional)
    openai_key = os.getenv('OPENAI_API_KEY')
    print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '⚠️  Missing (RAG features disabled)'}")
    
    # Check OpenRouter (optional)
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    print(f"OPENROUTER_API_KEY: {'✅ Set' if openrouter_key else '⚠️  Missing (alternative to OpenAI)'}")
    
    print("\n=== System Status ===")
    print("Environment check complete!")

if __name__ == "__main__":
    debug_environment() 