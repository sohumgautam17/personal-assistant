#!/usr/bin/env python3
"""
Simple RAG (Retrieval-Augmented Generation) implementation
"""

import os
from typing import List
from dotenv import load_dotenv

def load_documents(data_dir: str = "data") -> List[str]:
    """Load documents from data directory"""
    documents = []
    
    if not os.path.exists(data_dir):
        print(f"Data directory {data_dir} not found")
        return documents
    
    for filename in os.listdir(data_dir):
        if filename.endswith(('.txt', '.md')):
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents.append(content)
                    print(f"Loaded: {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return documents

def simple_search(query: str, documents: List[str], max_results: int = 3) -> List[str]:
    """Simple keyword-based document search"""
    results = []
    query_lower = query.lower()
    
    for doc in documents:
        doc_lower = doc.lower()
        # Simple scoring based on keyword matches
        score = 0
        for word in query_lower.split():
            score += doc_lower.count(word)
        
        if score > 0:
            results.append((score, doc))
    
    # Sort by score and return top results
    results.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in results[:max_results]]

def main():
    """Test the simple RAG functionality"""
    load_dotenv()
    
    print("=== Simple RAG Test ===")
    
    # Load documents
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")
    
    if not documents:
        print("No documents found. Add some .txt or .md files to the data/ directory.")
        return
    
    # Test search
    test_query = "personal assistant"
    print(f"\nSearching for: '{test_query}'")
    
    results = simple_search(test_query, documents)
    print(f"Found {len(results)} relevant documents")
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(result[:200] + "..." if len(result) > 200 else result)

if __name__ == "__main__":
    main() 