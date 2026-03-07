import openai
from typing import List, Optional, Dict, Any
from config import settings
import tiktoken

class OpenAIService:
    def __init__(self):
        self.model = settings.openai_model
        self.embedding_model = settings.openai_embedding_model

        # Priority: Groq → OpenAI → mock
        if settings.groq_api_key:
            self.client = openai.OpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1",
            )
            self.model = settings.groq_model
            self.use_mock = False
            self.use_local_embeddings = True  # Groq has no embedding API
            print(f"✅ Groq LLM ready — model: {self.model}")

        elif settings.openai_api_key:
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
            self.use_mock = False
            self.use_local_embeddings = False
            print(f"✅ OpenAI ready — model: {self.model}")

        else:
            self.client = None
            self.use_mock = True
            self.use_local_embeddings = True
            print("⚠️  No API key found — running in mock mode")

        # Local sentence-transformer model (used when Groq or mock)
        self._st_model = None

        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        except Exception:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def _get_st_model(self):
        """Lazy-load sentence-transformers model."""
        if self._st_model is None:
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Local embedding model loaded (all-MiniLM-L6-v2)")
        return self._st_model

    # ── Chat ──────────────────────────────────────────────────────────

    def create_chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        if self.use_mock:
            return self._mock_chat_completion(messages)
        try:
            # Groq doesn't support all kwargs (e.g. some OpenAI-specific ones)
            safe_kwargs = {k: v for k, v in kwargs.items() if k in ('temperature', 'max_tokens', 'top_p')}
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **safe_kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")

    def _mock_chat_completion(self, messages):
        last_user = next(
            (m['content'] for m in reversed(messages) if m.get('role') == 'user'),
            ''
        )
        return (
            f"[Mock mode] You asked: '{last_user[:80]}'. "
            "Add a GROQ_API_KEY to your .env file to get real answers."
        )

    # ── Embeddings ────────────────────────────────────────────────────

    def create_embedding(self, text: str) -> List[float]:
        if self.use_local_embeddings:
            return self._get_st_model().encode([text])[0].tolist()
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model, input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Embedding error: {str(e)}")

    def create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        if self.use_local_embeddings:
            return self._get_st_model().encode(texts).tolist()
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model, input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise Exception(f"Batch embedding error: {str(e)}")

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    # ── RAG helpers ───────────────────────────────────────────────────

    def generate_rag_response(self, question: str, context: str, conversation_history: List[Dict] = None) -> str:
        system_prompt = (
            "You are a tutor for a specific textbook on Physical AI & Humanoid Robotics.\n\n"
            "STRICT RULES — follow these exactly:\n"
            "1. ONLY use the textbook context provided below. NEVER use your own training knowledge.\n"
            "2. In this textbook: ROS = Robot Operating System (NOT 'Robotic Nervous System' — Module 1 is titled that but ROS itself stands for Robot Operating System). "
            "VLA = Vision-Language-Action (NOT Very Large Array). "
            "Always use these exact definitions from the book.\n"
            "3. If the context does not contain the answer, say exactly: "
            "'Book mein is sawaal ka jawab nahi mila.' (or in English: 'This answer was not found in the book.')\n"
            "4. Language rule: detect the language of the question and reply in the EXACT same language. "
            "Roman Urdu question → Roman Urdu answer. English question → English answer. Urdu script → Urdu script.\n"
            "5. Format every answer professionally like a senior AI tutor:\n"
            "   - Start with a clear introduction (1-2 sentences).\n"
            "   - Use bold headings in the SAME language as the question "
            "(English question → English headings like **What is it**, **How it Works**, **Why it Matters**, **Summary**; "
            "Roman Urdu question → Roman Urdu headings like **Kya Hai**, **Kaise Kaam Karta Hai**, **Kyun Zaroori Hai**, **Khulasa**).\n"
            "   - Use bullet points for features, components, or steps.\n"
            "   - Write minimum 3 detailed sections.\n"
            "   - Use markdown: **bold**, bullet points, line breaks between sections.\n"
            "   - Never write everything in one paragraph. Always use structure."
        )
        if not context or not context.strip():
            user_content = (
                f"No textbook context was retrieved for this question.\n\n"
                f"Question: {question}\n\n"
                f"Reply: 'Book mein is sawaal ka jawab nahi mila.'"
            )
        else:
            user_content = (
                f"--- TEXTBOOK CONTEXT (use ONLY this) ---\n{context}\n"
                f"--- END CONTEXT ---\n\n"
                f"Question: {question}\n\nAnswer strictly from the context above:"
            )

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_content})

        return self.create_chat_completion(messages, temperature=0.7, max_tokens=1024)

    def extract_citations(self, answer: str, sources: List[str]) -> Dict[str, Any]:
        return {"answer": answer, "sources": sources, "citations": []}


# Singleton instance
openai_service = OpenAIService()
