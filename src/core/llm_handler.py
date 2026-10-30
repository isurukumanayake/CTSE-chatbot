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
        """Initialize the primary and fallback LLMs"""
        try:
            self.llm = self._build_llm(self.config.LLM_MODEL)
            self.logger.info(f"Initialized LLM: {self.config.LLM_MODEL}")

            self.fallback_llm = None
            if getattr(self.config, "LLM_FALLBACK_MODEL", None):
                self.fallback_llm = self._build_llm(self.config.LLM_FALLBACK_MODEL)
                self.logger.info(f"Initialized fallback LLM: {self.config.LLM_FALLBACK_MODEL}")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM: {e}")
            raise

    def _build_llm(self, model: str) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=self.api_key,
            temperature=self.config.LLM_TEMPERATURE,
            max_output_tokens=self.config.LLM_MAX_OUTPUT_TOKENS,
            timeout=30,
            max_retries=2,
        )
    
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
            
            # Generate response, falling back to a secondary model if the
            # primary one is unavailable or overloaded
            try:
                response = self.llm.invoke(formatted_prompt)
            except Exception as primary_error:
                if self.fallback_llm is None:
                    raise
                self.logger.warning(
                    f"Primary LLM ({self.config.LLM_MODEL}) failed ({primary_error}); "
                    f"retrying with fallback ({self.config.LLM_FALLBACK_MODEL})"
                )
                response = self.fallback_llm.invoke(formatted_prompt)

            # Extract content from response
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)

            # Newer Gemini models can return content as a list of parts
            if isinstance(content, list):
                content = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                )

            self.logger.debug("Generated LLM response")
            return content.strip()

        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            return f"❌ Error generating response: {str(e)}"