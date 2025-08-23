import streamlit as st
from pathlib import Path
import tempfile
import shutil
from typing import List

from ..utils.logger import get_logger
from config import Config

class FileUploadInterface:
    """File upload interface component"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = Config()
    
    def render(self):
        """Render file upload interface"""
        st.subheader("📁 Document Management")
        
        # Show current documents
        self._show_current_documents()
        
        # File upload
        self._render_file_upload()
        
        # Bulk operations
        self._render_bulk_operations()
    
    def _show_current_documents(self):
        """Show currently uploaded documents"""
        doc_files = []
        for ext in self.config.ALLOWED_EXTENSIONS:
            doc_files.extend(self.config.DOCUMENTS_DIR.glob(f"*{ext}"))
        
        if doc_files:
            st.write(f"**📚 Current Documents ({len(doc_files)}):**")
            
            # Track which file to delete
            file_to_delete = None
            
            for doc_file in doc_files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    file_size = doc_file.stat().st_size / (1024 * 1024)  # MB
                    st.write(f"• {doc_file.name} ({file_size:.1f} MB)")
                with col2:
                    if st.button("🗑️", key=f"delete_{doc_file.name}", help="Delete file"):
                        file_to_delete = doc_file
            
            # Handle deletion outside of columns for full-width messages
            if file_to_delete:
                self._delete_document(file_to_delete)
        else:
            st.info("No documents uploaded yet.")
    
    def _render_file_upload(self):
        """Render file upload widget"""
        st.write("**📤 Upload New Documents:**")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['pdf', 'pptx', 'docx', 'txt'],
            accept_multiple_files=True,
            help=f"Max file size: {self.config.MAX_FILE_SIZE // (1024*1024)}MB"
        )
        
        if uploaded_files:
            if st.button("🚀 Process Uploaded Files", type="primary"):
                self._process_uploaded_files(uploaded_files)
    
    def _render_bulk_operations(self):
        """Render bulk operations"""
        st.write("**⚙️ Bulk Operations:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Rebuild Vector Database", use_container_width=True):
                self._rebuild_vectorstore()
        
        with col2:
            # Check if we're in confirmation state
            if st.session_state.get('show_clear_confirmation', False):
                # Show confirmation buttons in separate rows
                st.error("⚠️ This will delete ALL documents!")
                
                # Confirm button (first row)
                if st.button("✅ Confirm Delete", type="primary", use_container_width=True):
                    self._clear_all_documents_confirmed()
                
                # Cancel button (second row)
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_clear_confirmation = False
                    st.rerun()
            else:
                # Show initial clear button
                if st.button("🗑️ Clear All Documents", use_container_width=True):
                    st.session_state.show_clear_confirmation = True
                    st.rerun()
    
    def _process_uploaded_files(self, uploaded_files):
        """Process uploaded files"""
        success_count = 0
        
        with st.spinner("Processing uploaded files..."):
            for uploaded_file in uploaded_files:
                try:
                    # Validate file size
                    if uploaded_file.size > self.config.MAX_FILE_SIZE:
                        st.error(f"File {uploaded_file.name} is too large (max {self.config.MAX_FILE_SIZE // (1024*1024)}MB)")
                        continue
                    
                    # Save file to documents directory
                    file_path = self.config.DOCUMENTS_DIR / uploaded_file.name
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Add to chatbot
                    if st.session_state.chatbot and st.session_state.chatbot.add_document(file_path):
                        success_count += 1
                        st.success(f"✅ Processed {uploaded_file.name}")
                    else:
                        st.error(f"❌ Failed to process {uploaded_file.name}")
                        # Remove failed file
                        file_path.unlink(missing_ok=True)
                
                except Exception as e:
                    st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                    self.logger.error(f"File upload error: {e}")
        
        if success_count > 0:
            st.success(f"🎉 Successfully processed {success_count} file(s)!")
            st.session_state.vectorstore_ready = True
            # Clear uploaded files from widget
            st.rerun()
    
    def _delete_document(self, doc_path: Path):
        """Delete a document"""
        try:
            # Delete the file
            doc_path.unlink()
            st.success(f"🗑️ Deleted {doc_path.name}")
            
            # Check remaining documents
            remaining_docs = []
            for ext in self.config.ALLOWED_EXTENSIONS:
                remaining_docs.extend(self.config.DOCUMENTS_DIR.glob(f"*{ext}"))
            
            if remaining_docs and st.session_state.chatbot:
                # Rebuild vectorstore with remaining documents
                with st.spinner("Updating vector database..."):
                    st.session_state.chatbot.process_documents()
                    st.session_state.vectorstore_ready = True
            else:
                # Clear vectorstore if no documents remain
                self._clear_vectorstore()
                st.session_state.vectorstore_ready = False
                st.session_state.chat_history = []  # Clear chat history too
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Failed to delete {doc_path.name}: {str(e)}")
            self.logger.error(f"File deletion error: {e}")
    
    def _rebuild_vectorstore(self):
        """Rebuild the vector database"""
        with st.spinner("Rebuilding vector database..."):
            try:
                # Check if documents exist
                doc_files = []
                for ext in self.config.ALLOWED_EXTENSIONS:
                    doc_files.extend(self.config.DOCUMENTS_DIR.glob(f"*{ext}"))
                
                if not doc_files:
                    st.warning("⚠️ No documents found to rebuild vector database")
                    return
                
                # Clear existing vectorstore
                self._clear_vectorstore()
                
                # Rebuild with current documents
                if st.session_state.chatbot and st.session_state.chatbot.process_documents():
                    st.success("✅ Vector database rebuilt successfully!")
                    st.session_state.vectorstore_ready = True
                else:
                    st.error("❌ Failed to rebuild vector database")
                    st.session_state.vectorstore_ready = False
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error rebuilding vector database: {str(e)}")
                self.logger.error(f"Vectorstore rebuild error: {e}")
    
    def _clear_vectorstore(self):
        """Clear the vector database directory"""
        try:
            if self.config.VECTORSTORE_DIR.exists():
                shutil.rmtree(self.config.VECTORSTORE_DIR)
            self.config.VECTORSTORE_DIR.mkdir(exist_ok=True)
            self.logger.info("Cleared vectorstore directory")
        except Exception as e:
            self.logger.error(f"Error clearing vectorstore: {e}")
    
    def _clear_all_documents_confirmed(self):
        """Clear all documents after confirmation"""
        try:
            with st.spinner("Clearing all documents..."):
                # Delete all document files
                deleted_count = 0
                for doc_file in self.config.DOCUMENTS_DIR.iterdir():
                    if doc_file.is_file() and doc_file.suffix.lower() in self.config.ALLOWED_EXTENSIONS:
                        doc_file.unlink()
                        deleted_count += 1
                        self.logger.info(f"Deleted document: {doc_file.name}")
                
                # Clear vectorstore
                self._clear_vectorstore()
                
                # Reset session state
                st.session_state.vectorstore_ready = False
                st.session_state.chat_history = []
                st.session_state.show_clear_confirmation = False
                
                # Reinitialize chatbot to reset its state
                if st.session_state.chatbot:
                    st.session_state.chatbot = None
                
                st.success(f"🗑️ Successfully cleared {deleted_count} document(s)!")
                st.info("ℹ️ Upload new documents to start using the chatbot again.")
                
            st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error clearing documents: {str(e)}")
            self.logger.error(f"Clear documents error: {e}")
            st.session_state.show_clear_confirmation = False