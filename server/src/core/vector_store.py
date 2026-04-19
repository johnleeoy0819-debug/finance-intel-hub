"""Vector store backed by ChromaDB + sentence-transformers."""
import logging
from pathlib import Path
from typing import List, Dict, Optional

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from src.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Singleton wrapper around ChromaDB for article embeddings."""

    _instance: Optional["VectorStore"] = None

    def __new__(cls) -> "VectorStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self) -> None:
        Path(settings.VECTOR_DB_PATH).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
        self.ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="articles",
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("VectorStore initialized")

    def add_article(self, article_id: int, title: str, summary: str, content: str) -> None:
        """Index an article into the vector store."""
        text = f"{title}\n\n{summary or ''}\n\n{(content or '')[:3000]}"
        self.collection.add(
            ids=[str(article_id)],
            documents=[text],
            metadatas=[{"title": title or "Untitled"}],
        )
        logger.info(f"Indexed article {article_id} into vector store")

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Semantic search: returns list of {article_id, distance, title}."""
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            include=["metadatas", "distances"],
        )
        items: List[Dict] = []
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        for i, aid in enumerate(ids):
            items.append({
                "article_id": int(aid),
                "distance": distances[i] if distances else None,
                "title": metadatas[i].get("title", "") if metadatas and i < len(metadatas) else "",
            })
        return items

    def delete_article(self, article_id: int) -> None:
        self.collection.delete(ids=[str(article_id)])
        logger.info(f"Deleted article {article_id} from vector store")

    def update_article(self, article_id: int, title: str, summary: str, content: str) -> None:
        self.delete_article(article_id)
        self.add_article(article_id, title, summary, content)
