# RAG Setup Guide

## Overview
This guide explains how to set up Retrieval-Augmented Generation (RAG) capabilities for your Personal Assistant.

## Prerequisites
- OpenAI API key (for enhanced RAG features)
- Python environment with required dependencies
- Document files in the `data/` directory

## Quick Setup

### 1. Get OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Generate an API key
4. Add it to your `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### 2. Add Documents
1. Place your documents in the `data/` directory
2. Supported formats: `.txt`, `.md`
3. Examples:
   - Personal notes
   - Documentation
   - Knowledge base articles
   - FAQs

### 3. Test RAG Setup
```bash
# Test basic RAG functionality
python3 test_rag.py

# Test simple document search
python3 simple_rag.py
```

## Configuration Options

### Environment Variables
- `OPENAI_API_KEY`: Required for enhanced RAG features
- `RAG_MAX_RESULTS`: Maximum search results (default: 3)
- `RAG_SIMILARITY_THRESHOLD`: Minimum similarity score (default: 0.5)

### Document Processing
- Documents are automatically loaded from `data/` directory
- Text preprocessing includes basic cleaning and tokenization
- Vector embeddings are generated for semantic search

## Usage Examples

### Basic Search
```python
from simple_rag import load_documents, simple_search

# Load documents
documents = load_documents()

# Search for relevant content
results = simple_search("How to configure SMS?", documents)
```

### Integration with SMS
When RAG is enabled, SMS responses will include relevant information from your documents, making the assistant more helpful and context-aware.

## Troubleshooting

### Common Issues
1. **No documents found**: Ensure `.txt` or `.md` files are in `data/` directory
2. **OpenAI API errors**: Check your API key and quota
3. **Import errors**: Run `pip install -r requirements.txt`

### Debug Commands
```bash
# Check environment
python3 debug_env.py

# Test document loading
python3 simple_rag.py

# Full system test
python3 test_rag.py
```

## Performance Tips
- Keep documents focused and well-structured
- Use clear, descriptive filenames
- Regular cleanup of irrelevant documents
- Monitor OpenAI API usage

## Advanced Features
- Semantic search with embeddings
- Context-aware response generation
- Multi-document synthesis
- Continuous learning from interactions 