# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from config import Config
from src.core.chatbot import CTSEChatbot
from src.ui.chat_interface import ChatInterface
from src.ui.file_upload import FileUploadInterface
from src.ui.sidebar import Sidebar
from src.utils.logger import setup_logger

# Configure page
st.set_page_config(
    page_title="CTSE Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    
    # Setup logging
    logger = setup_logger()
    
    # Check API key first
    if not Config.get_api_key():
        st.error("❌ Google API key not found!")
        st.markdown("""
        **Please set your Google API key:**
        1. Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Create a `.env` file in your project root with:
           ```
           GOOGLE_API_KEY=your_actual_api_key_here
           ```
        3. Restart the application
        """)
        return
    
    # Initialize session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'vectorstore_ready' not in st.session_state:
        st.session_state.vectorstore_ready = False
    
    # Header
    st.title("🎓 CTSE Learning Assistant")
    st.markdown("Ask questions about your Current Trends in Software Engineering course materials")
    
    status_col1, status_col2 = st.columns([3, 1])

    # Initialize chatbot if not already done
    if st.session_state.chatbot is None:
        try:
            with st.spinner("Initializing chatbot..."):
                st.session_state.chatbot = CTSEChatbot()
                # Update the vectorstore ready status immediately after initialization
                st.session_state.vectorstore_ready = st.session_state.chatbot.is_ready()
                
                with status_col1:
                    if st.session_state.vectorstore_ready:
                        st.success("✅ Chatbot ready! Ask your questions below.")
                    else:
                        st.warning("⚠️ No documents found. Please upload course materials.")
        except Exception as e:
            logger.error(f"Failed to initialize chatbot: {e}")
            st.error(f"Failed to initialize chatbot: {e}")
            return
    
    # Sidebar
    sidebar = Sidebar()
    sidebar.render()
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat interface
        if st.session_state.vectorstore_ready:
            chat_interface = ChatInterface(st.session_state.chatbot)
            chat_interface.render()
        else:
            st.info("👆 Please upload your course documents first using the sidebar.")
    
    with col2:
        # File upload interface
        upload_interface = FileUploadInterface()
        upload_interface.render()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "CTSE Learning Assistant - Built with Streamlit & Gemini AI"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()