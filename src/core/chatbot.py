import time
from typing import List, Dict, Tuple, Optional
from pathlib import Path

from .document_processor import DocumentProcessor
from .vectorstore import VectorStoreManager
from .llm_handler import LLMHandler
from ..utils.logger import get_logger
from config import Config

class CTSEChatbot:
    """Main chatbot class orchestrating all components"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = Config()
        
        # Initialize components
        self.document_processor = DocumentProcessor()
        self.vectorstore_manager = VectorStoreManager()
        self.llm_handler = LLMHandler()
        
        # Load existing vectorstore or create new one
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self) -> None:
        """Initialize or load vectorstore"""
        try:
            if self.vectorstore_manager.exists():
                self.vectorstore_manager.load()
                self.logger.info("Loaded existing vectorstore")
            else:
                # Check if documents exist to process
                doc_files = list(self.config.DOCUMENTS_DIR.glob("*"))
                doc_files = [f for f in doc_files if f.suffix.lower() in self.config.ALLOWED_EXTENSIONS]
                
                if doc_files:
                    self.logger.info(f"Found {len(doc_files)} documents to process")
                    self.process_documents()
                else:
                    self.logger.info("No documents found for initial processing")
        except Exception as e:
            self.logger.error(f"Failed to initialize vectorstore: {e}")
            raise
    
    def process_documents(self) -> bool:
        """Process all documents in the documents directory"""
        try:
            self.logger.info("Starting document processing...")
            
            # Get all document files
            doc_files = []
            for ext in self.config.ALLOWED_EXTENSIONS:
                doc_files.extend(self.config.DOCUMENTS_DIR.glob(f"*{ext}"))
            
            if not doc_files:
                self.logger.warning("No documents found to process")
                return False
            
            # Process documents
            all_chunks = []
            for doc_file in doc_files:
                self.logger.info(f"Processing {doc_file.name}")
                chunks = self.document_processor.process_file(doc_file)
                all_chunks.extend(chunks)
            
            if not all_chunks:
                self.logger.error("No content extracted from documents")
                return False
            
            # Create vectorstore
            self.vectorstore_manager.create_from_chunks(all_chunks)
            self.logger.info(f"Created vectorstore with {len(all_chunks)} chunks")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Document processing failed: {e}")
            return False
    
    def add_document(self, file_path: Path) -> bool:
        """Add a new document to the vectorstore"""
        try:
            self.logger.info(f"Adding document: {file_path.name}")
            
            # Process the new document
            chunks = self.document_processor.process_file(file_path)
            
            if not chunks:
                self.logger.warning(f"No content extracted from {file_path.name}")
                return False
            
            # Add to existing vectorstore or create new one
            if self.vectorstore_manager.exists():
                self.vectorstore_manager.add_chunks(chunks)
            else:
                self.vectorstore_manager.create_from_chunks(chunks)
            
            self.logger.info(f"Added {len(chunks)} chunks from {file_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add document {file_path.name}: {e}")
            return False
    
    def ask_question(self, question: str) -> Dict[str, any]:
        """Ask a question and get response with metadata"""
        start_time = time.time()
        
        try:
            if not self.is_ready():
                return {
                    "answer": "❌ Chatbot not ready. Please upload documents first.",
                    "sources": [],
                    "processing_time": 0
                }
            
            # Retrieve relevant documents
            retrieval_start = time.time()
            relevant_docs = self.vectorstore_manager.similarity_search(
                question, k=self.config.RETRIEVAL_K
            )
            retrieval_time = time.time() - retrieval_start
            
            if not relevant_docs:
                return {
                    "answer": "❌ No relevant information found in the documents.",
                    "sources": [],
                    "processing_time": time.time() - start_time
                }
            
            # Generate response
            llm_start = time.time()
            answer = self.llm_handler.generate_response(question, relevant_docs)
            llm_time = time.time() - llm_start
            
            # Prepare sources
            sources = []
            for i, doc in enumerate(relevant_docs):
                source_info = {
                    "index": i + 1,
                    "filename": doc.metadata.get("source", "Unknown"),
                    "page": doc.metadata.get("page", "Unknown"),
                    "content_preview": doc.page_content[:200] + "..."
                }
                sources.append(source_info)
            
            total_time = time.time() - start_time
            
            self.logger.info(f"Question answered in {total_time:.2f}s (retrieval: {retrieval_time:.2f}s, LLM: {llm_time:.2f}s)")
            
            return {
                "answer": answer,
                "sources": sources,
                "processing_time": total_time,
                "retrieval_time": retrieval_time,
                "llm_time": llm_time
            }
            
        except Exception as e:
            self.logger.error(f"Failed to answer question: {e}")
            return {
                "answer": f"❌ Error processing question: {str(e)}",
                "sources": [],
                "processing_time": time.time() - start_time
            }
    
    def is_ready(self) -> bool:
        """Check if chatbot is ready to answer questions"""
        return self.vectorstore_manager.exists() and self.vectorstore_manager.vectorstore is not None
    
    def get_stats(self) -> Dict[str, any]:
        """Get chatbot statistics"""
        try:
            all_files = len(list(self.config.DOCUMENTS_DIR.glob("*")))
            doc_count = len([f for f in self.config.DOCUMENTS_DIR.glob("*") 
                           if f.suffix.lower() in self.config.ALLOWED_EXTENSIONS])
            
            if self.vectorstore_manager.vectorstore:
                chunk_count = self.vectorstore_manager.vectorstore.index.ntotal
            else:
                chunk_count = 0
            
            return {
                "total_files": all_files,
                "document_count": doc_count,
                "chunk_count": chunk_count,
                "vectorstore_ready": self.is_ready()
            }
        except Exception:
            return {
                "total_files": 0,
                "document_count": 0,
                "chunk_count": 0,
                "vectorstore_ready": False
            }