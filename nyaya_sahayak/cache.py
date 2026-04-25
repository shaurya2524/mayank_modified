"""
Query cache with local JSON persistence and Jaccard similarity fallback.
Only caches fresh, context-free queries (no conversation history).
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Optional

SIMILARITY_THRESHOLD = 0.72
CACHE_FILE = Path("data/query_cache.json")


def _normalize(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text.lower()).strip()


def _jaccard(a: str, b: str) -> float:
    wa, wb = set(_normalize(a).split()), set(_normalize(b).split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


class QueryCache:
    def __init__(self):
        self._store: dict[str, str] = {}  # normalized_query → answer
        self._load()

    def _load(self):
        if CACHE_FILE.exists():
            try:
                self._store = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            except Exception:
                self._store = {}

    def _save(self):
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(
            json.dumps(self._store, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def check(self, query: str) -> Optional[str]:
        """Return cached answer if a sufficiently similar query exists, else None."""
        norm = _normalize(query)

        # Exact match first
        if norm in self._store:
            return self._store[norm]

        # Jaccard similarity over all cached queries
        best_score, best_answer = 0.0, None
        for cached_q, answer in self._store.items():
            score = _jaccard(norm, cached_q)
            if score > best_score:
                best_score, best_answer = score, answer

        if best_score >= SIMILARITY_THRESHOLD:
            return best_answer
        return None

    def store(self, query: str, answer: str):
        """Cache a query-answer pair."""
        self._store[_normalize(query)] = answer
        self._save()

    def clear(self):
        self._store = {}
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
