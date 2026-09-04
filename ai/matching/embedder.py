"""Embedding abstraction supporting remote embedding APIs and lightweight local NumPy hashing vectorizer."""

import math
import os
import re
from typing import List, Optional, Union

import numpy as np


class SemanticEmbedder:
    """Computes semantic embedding vectors for construction activity descriptions and field notes.

    Supports both online embedding APIs (OpenAI / compatible) and a zero-dependency local
    deterministic vectorizer using subword character n-grams and hashing in NumPy.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        prefer_offline: bool = False,
        dim: int = 512,
    ):
        """Initializes the semantic embedder.

        Args:
            api_key: Optional API key for remote embedding provider.
            base_url: Optional base URL for embedding endpoint.
            model: Remote embedding model name (e.g. 'text-embedding-3-small').
            prefer_offline: If True, uses local NumPy vectorizer without network calls.
            dim: Dimension for the local hashing vectorizer.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("EMBEDDING_API_KEY")
        self.base_url = base_url or os.getenv("EMBEDDING_BASE_URL", "https://api.openai.com/v1")
        self.model = model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.prefer_offline = prefer_offline or (self.api_key is None)
        self.dim = dim

    def embed_text(self, text: str) -> np.ndarray:
        """Computes a normalized embedding vector for a single text string.

        Args:
            text: Input string.

        Returns:
            Normalized 1D numpy array of shape (dim,).
        """
        if not text or not text.strip():
            return np.zeros(self.dim, dtype=np.float32)

        if not self.prefer_offline and self.api_key:
            try:
                return self._call_embedding_api(text.strip())
            except Exception:
                # Fallback to local vectorizer
                return self._embed_local(text.strip())

        return self._embed_local(text.strip())

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Computes normalized embeddings for a list of text strings.

        Args:
            texts: List of input strings.

        Returns:
            Normalized 2D numpy array of shape (len(texts), dim).
        """
        return np.array([self.embed_text(t) for t in texts], dtype=np.float32)

    def similarity(self, text_a: str, text_b: str) -> float:
        """Computes cosine similarity between two text strings in range [0.0, 1.0].

        Args:
            text_a: First string.
            text_b: Second string.

        Returns:
            Cosine similarity score as float.
        """
        vec_a = self.embed_text(text_a)
        vec_b = self.embed_text(text_b)
        return self.compute_cosine_similarity(vec_a, vec_b)

    @staticmethod
    def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Computes cosine similarity between two normalized vectors.

        Args:
            vec_a: Normalized 1D numpy array.
            vec_b: Normalized 1D numpy array.

        Returns:
            Cosine similarity clamped between 0.0 and 1.0.
        """
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        dot = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
        # Clamp to [0.0, 1.0] for matching score semantics
        return max(0.0, min(1.0, dot))

    def _embed_local(self, text: str) -> np.ndarray:
        """Deterministic hashing vectorizer using subword n-grams and word tokens.

        Captures stems, word prefixes/suffixes (e.g. erect vs erection, support vs supports),
        and acronyms without any external dependencies.

        Args:
            text: Text to vectorize.

        Returns:
            L2-normalized 1D float32 numpy array of shape (self.dim,).
        """
        cleaned = re.sub(r"[^\w\s-]", " ", text.lower()).strip()
        words = cleaned.split()

        vec = np.zeros(self.dim, dtype=np.float32)

        if not words:
            return vec

        import zlib

        # 1. Word tokens (with higher weight)
        for w in words:
            idx = zlib.crc32(f"word_{w}".encode("utf-8")) % self.dim
            vec[idx] += 2.0

        # 2. Word bi-grams
        for i in range(len(words) - 1):
            bigram = f"{words[i]}_{words[i+1]}"
            idx = zlib.crc32(f"bi_{bigram}".encode("utf-8")) % self.dim
            vec[idx] += 1.5

        # 3. Character 3-grams and 4-grams for subword morphological matching
        for w in words:
            w_padded = f"<{w}>"
            for n in (3, 4):
                if len(w_padded) >= n:
                    for i in range(len(w_padded) - n + 1):
                        ngram = w_padded[i : i + n]
                        idx = zlib.crc32(f"ng_{ngram}".encode("utf-8")) % self.dim
                        vec[idx] += 0.5

        # Sublinear term frequency scaling: 1 + log(tf)
        non_zero = vec > 0
        vec[non_zero] = 1.0 + np.log(vec[non_zero])

        # L2 Normalization
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return vec

    def _call_embedding_api(self, text: str) -> np.ndarray:
        """Calls remote embedding endpoint.

        Args:
            text: Text to embed.

        Returns:
            Normalized 1D numpy array.
        """
        import requests

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "input": text,
        }
        url = f"{self.base_url.rstrip('/')}/embeddings"
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()

        embedding = resp.json()["data"][0]["embedding"]
        vec = np.array(embedding, dtype=np.float32)
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec
