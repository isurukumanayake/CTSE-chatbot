import streamlit as st
from typing import Dict, Any
import time

from ..utils.logger import get_logger

class ChatInterface:
    """Chat interface component"""
    
    def __init__(self, chatbot):
        self.chatbot = chatbot
        self.logger = get_logger(__name__)
    
    def render(self):
        """Render the chat interface"""
        # Display chat history
        self._display_chat_history()
        
        # Chat input
        self._render_chat_input()
    
    def _display_chat_history(self):
        """Display chat history"""
        if st.session_state.chat_history:
            st.subheader("💬 Conversation History")
            
            for i, exchange in enumerate(st.session_state.chat_history):
                # User question
                with st.chat_message("user"):
                    st.write(exchange["question"])
                
                # Assistant response
                with st.chat_message("assistant"):
                    st.write(exchange["answer"])
                    
                    # Show sources if available
                    if exchange.get("sources"):
                        with st.expander(f"📚 Sources ({len(exchange['sources'])} documents)"):
                            for source in exchange["sources"]:
                                st.write(f"**{source['filename']}** (Page {source['page']})")
                                st.caption(source['content_preview'])
                    
                    # Show performance metrics
                    if exchange.get("processing_time"):
                        st.caption(f"⏱️ Response time: {exchange['processing_time']:.2f}s")
    
    def _render_chat_input(self):
        """Render chat input area"""
        st.subheader("❓ Ask a Question")
        
        # Initialize question input state if not exists
        if 'current_question' not in st.session_state:
            st.session_state.current_question = ""
        
        # Create a form to handle the input properly
        with st.form(key="question_form", clear_on_submit=True):
            question = st.text_input(
                "Type your question about CTSE course materials:",
                placeholder="e.g., What are the key principles of microservices architecture?",
                value=st.session_state.current_question
            )
            
            # Only form submit button inside the form
            ask_button = st.form_submit_button("🚀 Ask Question", type="primary", use_container_width=True)
        
        # Clear button outside the form
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.current_question = ""
            st.rerun()
        
        # Handle form submission
        if ask_button and question.strip():
            self._process_question(question)
        
        # Sample questions
        self._render_sample_questions()
    
    def _process_question(self, question: str):
        """Process user question"""
        with st.spinner("🤔 Thinking..."):
            # Get response from chatbot
            result = self.chatbot.ask_question(question)
            
            # Add to chat history
            exchange = {
                "question": question,
                "answer": result["answer"],
                "sources": result["sources"],
                "processing_time": result["processing_time"],
                "timestamp": time.time()
            }
            
            st.session_state.chat_history.append(exchange)
            
            # Limit chat history size
            max_history = st.session_state.get("max_chat_history", 50)
            if len(st.session_state.chat_history) > max_history:
                st.session_state.chat_history = st.session_state.chat_history[-max_history:]
        
        # Clear the current question and rerun
        st.session_state.current_question = ""
        st.rerun()
    
    def _render_sample_questions(self):
        """Render sample questions"""
        with st.expander("💡 Sample Questions"):
            sample_questions = [
                "What are the main characteristics of microservices architecture?",
                "Explain the difference between REST and GraphQL APIs",
                "What are the benefits of using containerization in software development?",
                "How does DevOps improve software delivery?",
                "What are the key principles of clean code?",
                "Explain the concept of technical debt"
            ]
            
            st.write("Click on any question to use it:")
            
            for i, question in enumerate(sample_questions):
                if st.button(f"📋 {question}", key=f"sample_{i}", use_container_width=True):
                    st.session_state.current_question = question
                    st.rerun()