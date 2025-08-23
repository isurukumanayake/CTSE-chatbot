#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import Config
from src.core.chatbot import CTSEChatbot

def main():
    print("🚀 Setting up CTSE Chatbot Vector Store...")
    
    # Validate configuration
    if not Config.validate():
        print("❌ Configuration validation failed")
        return False
    
    # Initialize chatbot
    try:
        chatbot = CTSEChatbot()
        print("✅ Chatbot initialized successfully")
        
        # Check if documents exist
        doc_files = list(Config.DOCUMENTS_DIR.glob("*"))
        doc_files = [f for f in doc_files if f.suffix.lower() in Config.ALLOWED_EXTENSIONS]
        
        if not doc_files:
            print("ℹ️  No documents found. Please add files to the data/documents/ directory")
            return True
        
        print(f"📄 Found {len(doc_files)} documents to process")
        
        # Process documents
        if chatbot.process_documents():
            print("✅ Vector store created successfully!")
            stats = chatbot.get_stats()
            print(f"📊 Statistics: {stats['document_count']} docs, {stats['chunk_count']} chunks")
            return True
        else:
            print("❌ Failed to create vector store")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)