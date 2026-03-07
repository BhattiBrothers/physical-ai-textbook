"""Auto-ingests all textbook markdown files into Qdrant at startup."""
import os
import re

DOCS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "book", "docs")

def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter from markdown."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].strip()
    return text

def _strip_markdown(text: str) -> str:
    """Remove markdown syntax, keep plain text."""
    text = re.sub(r"```[\s\S]*?```", "", text)   # code blocks
    text = re.sub(r"`[^`]+`", "", text)           # inline code
    text = re.sub(r"#+\s+", "", text)             # headings
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # bold
    text = re.sub(r"\*([^*]+)\*", r"\1", text)   # italic
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)   # images
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # links
    text = re.sub(r"^\s*[-*>|]+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def collect_docs() -> list[dict]:
    """Walk book/docs and collect all markdown files."""
    docs = []
    docs_path = os.path.abspath(DOCS_PATH)

    if not os.path.exists(docs_path):
        print(f"⚠️  Docs path not found: {docs_path}")
        return docs

    for root, _, files in os.walk(docs_path):
        for filename in sorted(files):
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(root, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw = f.read()

            text = _strip_markdown(_strip_frontmatter(raw))
            if len(text.strip()) < 50:
                continue

            # Build a human-readable doc_id from relative path
            rel = os.path.relpath(filepath, docs_path)
            doc_id = rel.replace("\\", "/").replace(".md", "")

            # Extract module from path
            parts = rel.replace("\\", "/").split("/")
            module = parts[0] if len(parts) > 1 else "general"

            docs.append({
                "doc_id": doc_id,
                "text": text,
                "metadata": {
                    "source": doc_id,
                    "module": module,
                    "filename": filename,
                }
            })
            print(f"  📄 Loaded: {doc_id} ({len(text)} chars)")

    return docs

# In-memory store for keyword fallback search
_doc_store: list[dict] = []

def ingest_all(rag_service_instance):
    """Ingest all textbook docs. Called once at startup."""
    global _doc_store
    print("\n📚 Ingesting textbook content...")
    docs = collect_docs()

    if not docs:
        print("⚠️  No docs found to ingest.")
        return

    _doc_store = docs  # keep for keyword fallback

    for doc in docs:
        try:
            rag_service_instance.ingest_document(
                document_text=doc["text"],
                document_id=doc["doc_id"],
                metadata=doc["metadata"],
            )
        except Exception as e:
            print(f"  ❌ Failed to ingest {doc['doc_id']}: {e}")

    print(f"✅ Ingested {len(docs)} documents into Qdrant.\n")


def keyword_search(query: str, top_k: int = 3) -> str:
    """Keyword-based search over loaded docs."""
    if not _doc_store:
        return ""

    # Strip punctuation and expand aliases
    clean_query = re.sub(r'[^\w\s]', '', query.lower())
    aliases = {
        "vla": "vision language action",
        "ros": "robot operating system ros2",
        "ros2": "robot operating system",
        "lidar": "lidar sensor",
        "urdf": "unified robot description format",
        "slam": "simultaneous localization mapping",
        "nav2": "navigation path planning",
        "imu": "inertial measurement unit",
        "gazebo": "gazebo simulation",
        "isaac": "nvidia isaac",
    }
    for short, full in aliases.items():
        if short in clean_query.split():
            clean_query += " " + full

    stop = {"ka", "kia", "ha", "hai", "kya", "the", "is", "a", "an", "in", "of", "and", "to",
            "what", "how", "why", "which", "who", "explain", "tell", "me", "about"}
    query_words = set(clean_query.split()) - stop
    query_words = {w for w in query_words if len(w) > 1}

    if not query_words:
        return ""

    scored = []
    for doc in _doc_store:
        text_lower = doc["text"].lower()
        score = sum(text_lower.count(w) for w in query_words)
        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Return full text of top docs (not just matching paragraphs)
    parts = []
    for _, doc in scored[:top_k]:
        parts.append(f"[Source: {doc['doc_id']}]\n{doc['text']}")

    return "\n\n---\n\n".join(parts)
