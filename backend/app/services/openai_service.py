# app/services/openai_service.py
"""
OpenAI API service for PDF AI Assistant
"""
import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI API service for chat completions and embeddings"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.organization = os.getenv("OPENAI_ORGANIZATION")
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
            # Mock mode için fallback
            self.client = None
            self.is_mock = True
        else:
            # Async client for FastAPI compatibility
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                organization=self.organization
            )
            self.is_mock = False
        
        # Model configurations
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.max_tokens = int(os.getenv("MAX_TOKENS", 1000))
        self.temperature = float(os.getenv("TEMPERATURE", 0.7))
        
        logger.info(f"OpenAI Service initialized. Model: {self.default_model}, Mock: {self.is_mock}")
    
    async def generate_answer(
        self, 
        question: str, 
        context: str,
        chat_history: Optional[List[Dict]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate answer using OpenAI ChatCompletion
        """
        if self.is_mock or not self.client:
            return await self._generate_mock_answer(question, context)
        
        try:
            # Prepare messages
            messages = []
            
            # System prompt for RAG
            system_prompt = """You are a helpful AI assistant that answers questions based on provided context.
            Context is from PDF documents uploaded by the user.
            If the context doesn't contain relevant information, say "I don't have enough information from the document to answer this question."
            Be concise and accurate."""
            
            messages.append({"role": "system", "content": system_prompt})
            
            # Add chat history if provided
            if chat_history:
                messages.extend(chat_history)
            
            # Add context and question
            user_content = f"""Context from document:
{context}

Question: {question}

Please answer the question based only on the provided context."""
            
            messages.append({"role": "user", "content": user_content})
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=False
            )
            
            # Parse response
            answer = response.choices[0].message.content
            usage = response.usage.dict() if response.usage else {}
            
            return {
                "answer": answer,
                "model": response.model,
                "usage": usage,
                "finish_reason": response.choices[0].finish_reason,
                "is_mock": False
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # Fallback to mock response
            return await self._generate_mock_answer(question, context, error=str(e))
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI Embeddings API
        """
        if self.is_mock or not self.client:
            # Return mock embeddings for FAISS
            return self._generate_mock_embeddings(texts)
        
        try:
            # Batch process to avoid rate limits
            batch_size = 20
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = await self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"OpenAI Embeddings error: {e}")
            # Fallback to mock embeddings
            return self._generate_mock_embeddings(texts)
    
    async def _generate_mock_answer(self, question: str, context: str, error: str = None) -> Dict[str, Any]:
        """Generate mock answer when OpenAI API is not available"""
        import asyncio
        import random
        
        await asyncio.sleep(0.5)  # Simulate API delay
        
        mock_responses = [
            f"Based on the document: {context[:150]}... \n\nYour question '{question}' is addressed in the provided context.",
            f"The PDF contains information about this topic. {context[:100]}...",
            f"According to the document: {question} is mentioned in the context.",
            f"I found relevant information: {context[:200]}"
        ]
        
        if error:
            mock_responses.append(f"[Mock Mode - Add OpenAI API Key for real answers] Error: {error}")
        else:
            mock_responses.append("[Mock Mode - Add your OpenAI API key in .env file for real AI responses]")
        
        return {
            "answer": random.choice(mock_responses),
            "model": "mock-gpt-3.5-turbo",
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            "is_mock": True,
            "warning": "This is a mock response. Add OpenAI API key for real answers."
        }
    
    def _generate_mock_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings (random vectors for FAISS)"""
        import random
        
        # FAISS için 384 boyutlu random vektörler (text-embedding-3-small boyutu)
        embeddings = []
        for text in texts:
            embedding = [random.uniform(-1, 1) for _ in range(384)]
            embeddings.append(embedding)
        
        return embeddings
    
    async def check_api_key(self) -> Dict[str, Any]:
        """Check if OpenAI API key is valid"""
        if self.is_mock or not self.client:
            return {
                "valid": False,
                "message": "OpenAI API key not configured",
                "mock_mode": True
            }
        
        try:
            # Simple API call to check key
            models = await self.client.models.list()
            model_ids = [model.id for model in models.data[:5]]
            
            return {
                "valid": True,
                "message": "OpenAI API key is valid",
                "models_available": model_ids,
                "mock_mode": False
            }
        except Exception as e:
            return {
                "valid": False,
                "message": f"OpenAI API key validation failed: {str(e)}",
                "mock_mode": False
            }


# Global instance
openai_service = OpenAIService()