import time
from pathlib import Path
from typing import List, Optional

from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from ..utils.logger import get_logger
from config import Config

class VectorStoreManager:
    """Manage FAISS vector store operations"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = Config()
        self.vectorstore: Optional[FAISS] = None
        self.embeddings = None
        
        self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """Initialize embedding model"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.config.EMBEDDING_MODEL
            )
            self.logger.info(f"Initialized embeddings: {self.config.EMBEDDING_MODEL}")
        except Exception as e:
            self.logger.error(f"Failed to initialize embeddings: {e}")
            raise
    
    def exists(self) -> bool:
        """Check if vectorstore exists on disk"""
        index_file = self.config.VECTORSTORE_DIR / "index.faiss"
        pkl_file = self.config.VECTORSTORE_DIR / "index.pkl"
        return index_file.exists() and pkl_file.exists()
    
    def load(self) -> bool:
        """Load existing vectorstore from disk"""
        try:
            if not self.exists():
                self.logger.warning("No vectorstore found to load")
                return False
            
            self.vectorstore = FAISS.load_local(
                str(self.config.VECTORSTORE_DIR),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            self.logger.info("Loaded vectorstore from disk")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load vectorstore: {e}")
            return False
    
    def save(self) -> bool:
        """Save vectorstore to disk"""
        try:
            if self.vectorstore is None:
                self.logger.warning("No vectorstore to save")
                return False
            
            self.vectorstore.save_local(str(self.config.VECTORSTORE_DIR))
            self.logger.info("Saved vectorstore to disk")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save vectorstore: {e}")
            return False
    
    def create_from_chunks(self, chunks: List[Document]) -> bool:
        """Create new vectorstore from document chunks"""
        try:
            if not chunks:
                self.logger.error("No chunks provided for vectorstore creation")
                return False
            
            start_time = time.time()
            self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
            creation_time = time.time() - start_time
            
            # Save to disk
            self.save()
            
            self.logger.info(f"Created vectorstore with {len(chunks)} chunks in {creation_time:.2f}s")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create vectorstore: {e}")
            return False
    
    def add_chunks(self, chunks: List[Document]) -> bool:
        """Add new chunks to existing vectorstore"""
        try:
            if self.vectorstore is None:
                self.logger.error("No vectorstore loaded")
                return False
            
            if not chunks:
                self.logger.warning("No chunks to add")
                return True
            
            # Create temporary vectorstore for new chunks
            temp_vectorstore = FAISS.from_documents(chunks, self.embeddings)
            
            # Merge with existing vectorstore
            self.vectorstore.merge_from(temp_vectorstore)
            
            # Save updated vectorstore
            self.save()
            
            self.logger.info(f"Added {len(chunks)} chunks to vectorstore")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add chunks: {e}")
            return False
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents"""
        try:
            if self.vectorstore is None:
                self.logger.error("No vectorstore loaded")
                return []
            
            results = self.vectorstore.similarity_search(query, k=k)
            self.logger.debug(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            self.logger.error(f"Similarity search failed: {e}")
            return []