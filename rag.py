import os
import json
import numpy as np
from typing import List, Dict, Any

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class CoffeeKnowledgeRAG:
    """Lightweight vector RAG layer for AI Barista coffee knowledge."""

    def __init__(
        self,
        knowledge_file: str = "coffee_knowledge.md",
        menu_file: str = "menu.json",
        similarity_threshold: float = 0.35
    ):
        self.knowledge_file = knowledge_file
        self.menu_file = menu_file
        self.similarity_threshold = similarity_threshold
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: List[np.ndarray] = []
        self.embedding_model = "text-embedding-004"
        self._load_and_chunk_knowledge()
        self._initialize_embeddings()

    def _load_and_chunk_knowledge(self):
        """Reads coffee_knowledge.md and splits into section chunks."""
        if not os.path.exists(self.knowledge_file):
            return

        try:
            with open(self.knowledge_file, "r", encoding="utf-8") as f:
                content = f.read()

            raw_sections = content.split("---")
            for section in raw_sections:
                text = section.strip()
                if text:
                    lines = [line.strip() for line in text.split("\n") if line.strip()]
                    title = lines[0].replace("#", "").strip() if lines else "Coffee Info"
                    self.chunks.append({
                        "title": title,
                        "text": text
                    })
        except Exception:
            self.chunks = []

    def _get_genai_client(self):
        """Instantiates GenAI client respecting Vertex AI or Gemini API key environment variables."""
        if not GENAI_AVAILABLE:
            return None
        try:
            use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("true", "1")
            project = os.environ.get("GOOGLE_CLOUD_PROJECT")
            location = os.environ.get("GOOGLE_CLOUD_LOCATION")

            if use_vertex and project:
                return genai.Client(vertexai=True, project=project, location=location or "us-central1")
            return genai.Client()
        except Exception:
            return None

    def _initialize_embeddings(self):
        """Generates embeddings for knowledge chunks using currently supported Google embedding model."""
        if not self.chunks:
            return

        client = self._get_genai_client()
        if not client:
            return

        supported_models = ["text-embedding-004", "textembedding-gecko@003", "embedding-001"]
        selected_model = None

        for model_candidate in supported_models:
            try:
                res = client.models.embed_content(
                    model=model_candidate,
                    contents=self.chunks[0]["text"]
                )
                if hasattr(res, "embedding") and hasattr(res.embedding, "values"):
                    selected_model = model_candidate
                    break
            except Exception:
                continue

        if not selected_model:
            selected_model = self.embedding_model

        self.embedding_model = selected_model

        temp_embeddings = []
        try:
            for chunk in self.chunks:
                res = client.models.embed_content(
                    model=self.embedding_model,
                    contents=chunk["text"]
                )
                vec = None
                if hasattr(res, "embedding") and hasattr(res.embedding, "values"):
                    vec = np.array(res.embedding.values, dtype=np.float32)
                elif isinstance(res, dict) and "embedding" in res:
                    vec = np.array(res["embedding"]["values"], dtype=np.float32)

                if vec is not None and len(vec) > 0:
                    norm = np.linalg.norm(vec)
                    if norm > 0:
                        vec = vec / norm
                    temp_embeddings.append(vec)
                else:
                    temp_embeddings.append(None)

            if len(temp_embeddings) == len(self.chunks):
                self.embeddings = temp_embeddings
        except Exception:
            self.embeddings = []

    def search(self, query: str, top_k: int = 2) -> str:
        """Search relevant coffee knowledge using vector similarity or graceful keyword fallback."""
        if not query:
            return self._fallback_menu_search(query)

        # 1. Vector Search
        if len(self.embeddings) == len(self.chunks) and any(e is not None for e in self.embeddings):
            client = self._get_genai_client()
            if client:
                try:
                    res = client.models.embed_content(
                        model=self.embedding_model,
                        contents=query
                    )
                    q_vec = None
                    if hasattr(res, "embedding") and hasattr(res.embedding, "values"):
                        q_vec = np.array(res.embedding.values, dtype=np.float32)
                    elif isinstance(res, dict) and "embedding" in res:
                        q_vec = np.array(res["embedding"]["values"], dtype=np.float32)

                    if q_vec is not None and len(q_vec) > 0:
                        norm = np.linalg.norm(q_vec)
                        if norm > 0:
                            q_vec = q_vec / norm

                        scores = []
                        for idx, emb in enumerate(self.embeddings):
                            if emb is not None:
                                score = float(np.dot(q_vec, emb))
                                scores.append((score, self.chunks[idx]))

                        scores.sort(key=lambda x: x[0], reverse=True)
                        filtered_results = [
                            item[1]["text"] for item in scores[:top_k]
                            if item[0] >= self.similarity_threshold
                        ]

                        if filtered_results:
                            return "\n\n".join(filtered_results)
                except Exception:
                    pass

        # 2. Keyword fallback over knowledge chunks
        matched_chunks = self._keyword_search(query)
        if matched_chunks:
            return matched_chunks

        # 3. Fallback to menu.json search
        return self._fallback_menu_search(query)

    def _keyword_search(self, query: str) -> str:
        if not self.chunks:
            return ""

        query_words = [w for w in query.lower().split() if len(w) > 2]
        if not query_words:
            return ""

        matched = []
        for chunk in self.chunks:
            text_lower = chunk["text"].lower()
            if any(word in text_lower for word in query_words):
                matched.append(chunk["text"])

        return "\n\n".join(matched[:2]) if matched else ""

    def _fallback_menu_search(self, query: str) -> str:
        """Fallback lookup using menu.json."""
        if os.path.exists(self.menu_file):
            try:
                with open(self.menu_file, "r", encoding="utf-8") as f:
                    menu = json.load(f)

                if not query:
                    return json.dumps(menu)

                query_words = [w for w in query.lower().split() if len(w) > 2]
                results = []
                for item in menu:
                    item_text = (item["name"] + " " + item["description"] + " " + " ".join(item["tags"])).lower()
                    if any(w in item_text for w in query_words):
                        results.append(item)

                if not results:
                    results = menu

                return json.dumps(results[:3])
            except Exception:
                pass
        return "Menu information unavailable."


# Singleton instance
rag_engine = CoffeeKnowledgeRAG()


def search_coffee_knowledge(query: str = "") -> str:
    """Retrieve relevant coffee shop knowledge using vector search with safe fallbacks."""
    try:
        return rag_engine.search(query)
    except Exception as e:
        return rag_engine._fallback_menu_search(query)

