import openai
from typing import List, Optional, Dict, Any
from config import settings
import tiktoken
import json

class OpenAIService:
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.embedding_model = settings.openai_embedding_model
        self.use_mock = not self.api_key

        if not self.use_mock:
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
            print("OpenAI service initialized with API key")
        else:
            self.client = None
            print("WARNING: OpenAI API key not configured. Using mock mode for development.")

        # Initialize tokenizer for counting tokens
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        except:
            # Fallback tokenizer
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def _mock_chat_completion(self, messages, **kwargs):
        """Mock chat completion for development."""
        # Simulate thinking time
        import time
        time.sleep(0.5)

        # Return a mock response based on the last user message
        last_user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break

        if last_user_message:
            return f"I'm a mock AI tutor. You asked: '{last_user_message[:50]}...'. In a real implementation, this would be answered using OpenAI GPT with context from the textbook."
        else:
            return "I'm a mock AI tutor. How can I help you with Physical AI and Humanoid Robotics?"

    def _mock_embedding(self, text):
        """Mock embedding for development."""
        import numpy as np
        # Return random embedding vector of size 1536 (OpenAI embedding size)
        return np.random.randn(1536).tolist()

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self.tokenizer.encode(text))

    def create_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Create chat completion using OpenAI API."""
        if self.use_mock:
            return self._mock_chat_completion(messages, **kwargs)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text using OpenAI embedding model."""
        if self.use_mock:
            return self._mock_embedding(text)

        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"OpenAI embedding error: {str(e)}")

    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts."""
        if self.use_mock:
            import numpy as np
            return [np.random.randn(1536).tolist() for _ in texts]

        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise Exception(f"OpenAI batch embedding error: {str(e)}")

    def generate_rag_response(self, question: str, context: str, conversation_history: List[Dict] = None) -> str:
        """Generate RAG response using question and retrieved context."""
        system_prompt = """You are an expert tutor for Physical AI & Humanoid Robotics.
        You answer questions based on the provided textbook context.
        If the context doesn't contain relevant information, say so politely.
        Always be helpful, accurate, and pedagogical."""

        user_content = f"""Context from textbook:
        {context}

        Question: {question}

        Answer based on the context above:"""

        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": user_content})

        return self.create_chat_completion(messages, temperature=0.7, max_tokens=1000)

    def extract_citations(self, answer: str, sources: List[str]) -> Dict[str, Any]:
        """Extract citations from answer and map to sources."""
        # This is a simplified version - in production, you'd want more sophisticated citation extraction
        return {
            "answer": answer,
            "sources": sources,
            "citations": []  # Would be populated with actual citation mapping
        }

# Singleton instance
openai_service = OpenAIService()