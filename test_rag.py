#!/usr/bin/env python3
"""
Test script for RAG (Retrieval-Augmented Generation) functionality
"""

import os
from dotenv import load_dotenv
from simple_rag import load_documents, simple_search

def test_rag():
    """Test RAG functionality"""
    
    load_dotenv()
    
    print("=== RAG System Test ===")
    
    # Check OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("⚠️  OPENAI_API_KEY not found - using simple search only")
    else:
        print("✅ OpenAI API key found")
    
    # Test document loading
    print("\n📚 Testing document loading...")
    documents = load_documents()
    
    if not documents:
        print("❌ No documents found in data/ directory")
        print("Add some .txt or .md files to test RAG functionality")
        return False
    
    print(f"✅ Loaded {len(documents)} documents")
    
    # Test search functionality
    print("\n🔍 Testing search functionality...")
    test_queries = [
        "personal assistant",
        "SMS integration", 
        "configuration",
        "API endpoints"
    ]
    
    for query in test_queries:
        print(f"\nSearching: '{query}'")
        results = simple_search(query, documents, max_results=2)
        print(f"Found {len(results)} results")
        
        if results:
            # Show first few words of first result
            first_result = results[0][:100] + "..." if len(results[0]) > 100 else results[0]
            print(f"Top result preview: {first_result}")
    
    print("\n✅ RAG search test completed")
    return True

def main():
    """Main test function"""
    print("🧪 Running RAG tests...\n")
    
    success = test_rag()
    
    print(f"\n{'=' * 40}")
    if success:
        print("🎉 RAG tests completed successfully!")
    else:
        print("⚠️  RAG tests encountered issues")
    
    return success

if __name__ == "__main__":
    main() 