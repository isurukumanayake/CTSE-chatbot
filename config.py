import os
from pathlib import Path
from typing import Optional

class Config:
    """Application configuration"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    DOCUMENTS_DIR = DATA_DIR / "documents"
    VECTORSTORE_DIR = DATA_DIR / "vectorstore"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Create directories if they don't exist
    for directory in [DATA_DIR, DOCUMENTS_DIR, VECTORSTORE_DIR, LOGS_DIR]:
        directory.mkdir(exist_ok=True, parents=True)
    
    # API Configuration - Fixed to handle both local and deployment
    @staticmethod
    def get_api_key() -> Optional[str]:
        """Get API key from environment or Streamlit secrets"""
        # First try environment variable
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            return api_key
        
        # Then try Streamlit secrets (only if streamlit is available and secrets exist)
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'GOOGLE_API_KEY' in st.secrets:
                return st.secrets["GOOGLE_API_KEY"]
        except (ImportError, Exception):
            pass
        
        return None
    
    # LLM Configuration
    LLM_MODEL = "gemini-1.5-flash"
    LLM_TEMPERATURE = 0.1
    LLM_MAX_OUTPUT_TOKENS = 1024
    
    # Embedding Configuration
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Document Processing
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {".pdf", ".pptx", ".docx", ".txt"}
    
    # Retrieval Configuration
    RETRIEVAL_K = 5  # Number of documents to retrieve
    
    # UI Configuration
    MAX_CHAT_HISTORY = 50
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        api_key = cls.get_api_key()
        if not api_key:
            # Don't use st.error here to avoid import issues
            print("❌ Google API key not found. Please set GOOGLE_API_KEY environment variable.")
            print("Get your free API key from: https://aistudio.google.com/app/apikey")
            return False
        return True