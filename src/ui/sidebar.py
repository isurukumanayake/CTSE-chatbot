import streamlit as st
from ..utils.logger import get_logger

class Sidebar:
    """Sidebar component"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def render(self):
        """Render sidebar"""
        with st.sidebar:
            st.title("🎓 CTSE Assistant")
            
            # Status section
            self._render_status()
            
            # Statistics
            self._render_statistics()
            
            # Settings
            self._render_settings()
            
            # Help section
            self._render_help()
            
            # About
            self._render_about()
    
    def _render_status(self):
        """Render system status"""
        st.subheader("📊 System Status")
        
        if st.session_state.get('vectorstore_ready', False):
            st.success("🟢 Ready")
        else:
            st.error("🔴 Not Ready")
        
        # API status - Fixed to use the new method
        from config import Config
        api_key = Config.get_api_key()
        if api_key:
            st.success("🔑 API Key Configured")
        else:
            st.error("🔑 API Key Missing")
    
    def _render_statistics(self):
        """Render system statistics"""
        st.subheader("📈 Statistics")
        
        if st.session_state.chatbot:
            stats = st.session_state.chatbot.get_stats()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Documents", stats.get("document_count", 0))
            with col2:
                st.metric("Chunks", stats.get("chunk_count", 0))
            
            # Chat statistics
            chat_count = len(st.session_state.get('chat_history', []))
            st.metric("Questions Asked", chat_count)
    
    def _render_settings(self):
        """Render settings"""
        st.subheader("⚙️ Settings")
        
        # Max chat history
        max_history = st.slider(
            "Max Chat History",
            min_value=10,
            max_value=100,
            value=st.session_state.get('max_chat_history', 50),
            help="Maximum number of conversations to keep in history"
        )
        st.session_state.max_chat_history = max_history
        
        # Auto-scroll
        auto_scroll = st.checkbox(
            "Auto-scroll to latest",
            value=st.session_state.get('auto_scroll', True),
            help="Automatically scroll to the latest message"
        )
        st.session_state.auto_scroll = auto_scroll
    
    def _render_help(self):
        """Render help section"""
        with st.expander("❓ Help & Tips"):
            st.markdown("""
            **Getting Started:**
            1. Upload your CTSE course materials (PDFs, PowerPoint files)
            2. Wait for processing to complete
            3. Ask questions about your course content
            
            **Tips for Better Results:**
            - Be specific in your questions
            - Use course terminology
            - Reference specific topics or concepts
            - Check the sources provided with answers
            
            **Supported File Types:**
            - PDF documents (.pdf)
            - PowerPoint presentations (.pptx)
            - Word documents (.docx)
            - Text files (.txt)
            
            **File Size Limit:** 50MB per file
            """)
    
    def _render_about(self):
        """Render about section"""
        with st.expander("ℹ️ About"):
            st.markdown("""
            **CTSE Learning Assistant v1.0**
            
            A smart chatbot for Current Trends in Software Engineering course materials.
            
            **Technology Stack:**
            - 🚀 Streamlit (Web Framework)
            - 🤖 Google Gemini AI (Language Model)
            - 🔍 FAISS (Vector Search)
            - 📄 LangChain (Document Processing)
            
            **Features:**
            - Document upload and processing
            - Intelligent question answering
            - Source citation
            - Chat history
            - Performance metrics
            
            Built with ❤️ for CTSE students
            """)