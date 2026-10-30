from typing import List
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from ..utils.logger import get_logger
from config import Config

class LLMHandler:
    """Handle LLM interactions"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = Config()
        
        # Get API key
        self.api_key = self.config.get_api_key()
        if not self.api_key:
            raise ValueError("Google API key not found. Please set GOOGLE_API_KEY environment variable.")
        
        self._initialize_llm()
        self._initialize_prompt()
    
    def _initialize_llm(self):
        """Initialize the LLM"""
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.LLM_MODEL,
                google_api_key=self.api_key,
                temperature=self.config.LLM_TEMPERATURE,
                max_output_tokens=self.config.LLM_MAX_OUTPUT_TOKENS
            )
            self.logger.info(f"Initialized LLM: {self.config.LLM_MODEL}")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def _initialize_prompt(self):
        """Initialize the prompt template"""
        template = """
You are a helpful teaching assistant for a Current Trends in Software Engineering (CTSE) course.
Answer the question based only on the following context from the CTSE lecture notes.

Context:
{context}

Question: {question}

Instructions:
- Provide a comprehensive and accurate answer based solely on the provided context
- If the context doesn't contain enough information, say "I don't have enough information about that in my lecture notes."
- Use clear, educational language suitable for students
- Cite relevant sections when possible
- Be concise but thorough

Answer:
"""
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def generate_response(self, question: str, relevant_docs: List[Document]) -> str:
        """Generate response using LLM"""
        try:
            # Prepare context from relevant documents
            context = "\n\n".join([
                f"Document {i+1} (from {doc.metadata.get('source', 'unknown')}):\n{doc.page_content}"
                for i, doc in enumerate(relevant_docs)
            ])
            
            # Format prompt
            formatted_prompt = self.prompt.format(
                context=context,
                question=question
            )
            
            # Generate response
            response = self.llm.invoke(formatted_prompt)
            
            # Extract content from response
            if hasattr(response, 'content'):
                answer = response.content
            else:
                answer = str(response)
            
            self.logger.debug("Generated LLM response")
            return answer.strip()
            
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            return f"❌ Error generating response: {str(e)}"