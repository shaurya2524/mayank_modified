"""
RAG engine for Nyaya-Sahayak.
Primary retrieval is via Databricks Mosaic AI Vector Search.
Falls back to local PageIndex/Keyword searches if Databricks is unavailable.
"""

from __future__ import annotations
import sys, json, os
from pathlib import Path
from typing import Optional
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from nyaya_sahayak.config import (
    BNS_CSV_PATH, BNS_INDEX_PATH, IPC_INDEX_PATH, ROOT,
    LLM_MODEL, LLM_API_KEY, LLM_BASE_URL
)

from dotenv import load_dotenv
load_dotenv(str(ROOT / ".env"))

# ── PageIndex Vendor Path ───────────────────────────────────────────────────────
VENDOR_PATH = ROOT / "vendor" / "PageIndex"
if VENDOR_PATH.exists():
    sys.path.insert(0, str(VENDOR_PATH))

# ── BNS In-Memory Index (built from CSV directly) ────────────────────────────────
class BNSIndex:
    """
    Hierarchical tree index built from bns_sections.csv.
    Structure: chapters → sections (no PDF processing needed).
    """

    def __init__(self):
        self.chapters: dict[str, dict] = {}
        self.sections: dict[int, dict] = {}
        self._built = False

    def build(self) -> "BNSIndex":
        """Parse CSV and build tree."""
        pdf = pd.read_csv(BNS_CSV_PATH, encoding="utf-8")
        pdf.columns = [c.strip().replace(" ", "_") for c in pdf.columns]

        for _, row in pdf.iterrows():
            ch = str(row.get("Chapter", ""))
            ch_name = str(row.get("Chapter_name", ""))
            sec = int(pd.to_numeric(row.get("Section", 0), errors="coerce") or 0)
            sec_name = ""
            for k in row.index:
                if "section" in k.lower() and "name" in k.lower() and k != "Chapter_name":
                    sec_name = str(row[k]); break
            desc = str(row.get("Description", ""))

            if ch not in self.chapters:
                self.chapters[ch] = {"name": ch_name, "sections": []}
            self.chapters[ch]["sections"].append(sec)

            self.sections[sec] = {
                "chapter": ch,
                "chapter_name": ch_name,
                "section_num": sec,
                "section_name": sec_name,
                "description": desc,
                "ref": f"BNS Section {sec}",
            }

        self._built = True
        print(f"[RAG/Local] BNS index built: {len(self.sections)} sections, {len(self.chapters)} chapters")
        return self

    def get_section(self, num: int) -> Optional[dict]:
        return self.sections.get(num)

    def search_keyword(self, keyword: str, top_k: int = 5) -> list[dict]:
        kw = keyword.lower()
        results = []
        for sec, data in self.sections.items():
            score = 0
            text = (data["section_name"] + " " + data["description"]).lower()
            score += text.count(kw) * 2
            if kw in data["section_name"].lower():
                score += 10
            if score > 0:
                results.append({**data, "_score": score})
        results.sort(key=lambda x: x["_score"], reverse=True)
        return results[:top_k]

    def get_chapter_summary(self, chapter_num: str) -> dict:
        ch = self.chapters.get(str(chapter_num), {})
        sections = [self.sections[s] for s in ch.get("sections", []) if s in self.sections]
        return {"chapter": chapter_num, "name": ch.get("name", ""), "sections": sections}

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"chapters": self.chapters, "sections": {str(k): v for k, v in self.sections.items()}}
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[RAG/Local] BNS index saved: {path}")

    def load(self, path: Path) -> "BNSIndex":
        data = json.loads(path.read_text(encoding="utf-8"))
        self.chapters = data["chapters"]
        self.sections = {int(k): v for k, v in data["sections"].items()}
        self._built = True
        print(f"[RAG/Local] BNS index loaded: {len(self.sections)} sections")
        return self


# ── PageIndex Tree RAG ──────────────────────────────────────────────────────────
class PageIndexRAG:
    """
    Wraps the PageIndex library (cloned to vendor/) for PDF-based retrieval.
    Falls back to keyword search if PageIndex is unavailable.
    """

    def __init__(self, label: str, md_path: Path, index_path: Path):
        self.label = label
        self.md_path = md_path
        self.index_path = index_path
        self._tree = None
        self._pi = None

    def _load_pageindex(self):
        """Try to import and configure PageIndex."""
        try:
            import litellm
            # Configure litellm to use HF endpoint
            os.environ.setdefault("OPENAI_API_KEY", LLM_API_KEY)
            os.environ.setdefault("OPENAI_API_BASE", LLM_BASE_URL)

            # Dynamic import from vendor path
            sys.path.insert(0, str(VENDOR_PATH))
            from pageindex.page_index import PageIndex
            self._pi = PageIndex(model=f"openai/{LLM_MODEL}")
            print(f"[RAG/Local/{self.label}] PageIndex loaded successfully")
            return True
        except Exception as e:
            print(f"[RAG/Local/{self.label}] PageIndex not available ({e}), using built-in retrieval")
            return False

    def build_or_load(self) -> "PageIndexRAG":
        """Build a new index or load from cache."""
        if self.index_path.exists():
            print(f"[RAG/Local/{self.label}] Loading cached index: {self.index_path}")
            self._tree = json.loads(self.index_path.read_text(encoding="utf-8"))
            return self

        if not self.md_path.exists():
            print(f"[RAG/Local/{self.label}] ⚠️ MD file not found: {self.md_path}")
            return self

        if self._load_pageindex() and self._pi:
            try:
                print(f"[RAG/Local/{self.label}] Building PageIndex tree from {self.md_path}...")
                self._tree = self._pi.build_from_md(str(self.md_path))
                self.index_path.parent.mkdir(parents=True, exist_ok=True)
                self.index_path.write_text(
                    json.dumps(self._tree, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                print(f"[RAG/Local/{self.label}] Tree saved to {self.index_path}")
            except Exception as e:
                print(f"[RAG/Local/{self.label}] Tree build failed: {e}")
        return self

    def query(self, question: str, top_k: int = 3) -> list[dict]:
        """Query the index. Returns list of relevant section dicts."""
        if self._pi and self._tree:
            try:
                result = self._pi.query(self._tree, question, top_k=top_k)
                return self._format_pageindex_results(result)
            except Exception as e:
                print(f"[RAG/Local/{self.label}] Query error: {e}")

        # Fallback: simple keyword search over the MD file
        return self._keyword_search(question, top_k)

    def _keyword_search(self, query: str, top_k: int) -> list[dict]:
        """Keyword search supporting both Markdown (BNS) and plain-text (IPC) files."""
        if not self.md_path.exists():
            return []
        text = self.md_path.read_text(encoding="utf-8")
        kws = [k for k in query.lower().split() if len(k) > 2]
        parts = []

        if "\n### " in text:
            # Markdown format (BNS) — split by section headers
            for sec in text.split("\n### ")[1:]:
                lines = sec.strip().split("\n")
                parts.append((lines[0], "\n".join(lines[1:])))
        else:
            # Plain-text format (IPC PDF) — split by section number pattern
            import re
            chunks = re.split(r'\n(?=\d{1,3}[A-Z]?\.\s)', text)
            for chunk in chunks:
                lines = chunk.strip().split("\n")
                header = lines[0][:120] if lines else ""
                body = "\n".join(lines[1:])
                parts.append((header, body))

        results = []
        for header, body in parts:
            combined = (header + " " + body).lower()
            score = sum(combined.count(kw) + header.lower().count(kw) * 2 for kw in kws)
            if score > 0:
                results.append({
                    "title": header.strip(),
                    "text": body[:800].strip(),
                    "score": score,
                    "source": self.label,
                })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def _format_pageindex_results(self, pi_result) -> list[dict]:
        """Convert PageIndex output to our standard format."""
        if isinstance(pi_result, list):
            return [{"title": r.get("title",""), "text": r.get("content",""), "source": self.label} for r in pi_result]
        if isinstance(pi_result, dict):
            return [{"title": pi_result.get("title",""), "text": pi_result.get("content",""), "source": self.label}]
        return [{"title": "Result", "text": str(pi_result), "source": self.label}]


# ── Unified RAG Engine (Databricks with Local Fallback) ──────────────────────────
class NyayaRAGEngine:
    """
    Main RAG engine.
    Tries Databricks Vector Search first. If it fails, falls back to local PageIndex.
    """

    def __init__(self):
        self.dbx_client = None
        self.bns_dbx_index = None
        self.ipc_dbx_index = None
        self.endpoint_name = "nyaya_sahayak_endpoint"
        
        # Local Indices (Fallback)
        self.local_bns_index = BNSIndex()
        self.local_bns_rag = PageIndexRAG("BNS", ROOT / "data" / "bns_full.md", BNS_INDEX_PATH)
        self.local_ipc_rag = PageIndexRAG("IPC", ROOT / "data" / "ipc_full.md", IPC_INDEX_PATH)

    def initialize(self) -> "NyayaRAGEngine":
        # 1. Try to connect to Databricks
        try:
            from databricks.vector_search.client import VectorSearchClient
            self.dbx_client = VectorSearchClient(disable_notice=True)
            self.bns_dbx_index = self.dbx_client.get_index(
                endpoint_name=self.endpoint_name,
                index_name="legal_catalog.nyaya_sahayak.bns_gold_index"
            )
            self.ipc_dbx_index = self.dbx_client.get_index(
                endpoint_name=self.endpoint_name,
                index_name="legal_catalog.nyaya_sahayak.ipc_gold_index"
            )
            print("[RAG] Databricks Mosaic AI Engine connected ✅")
        except Exception as e:
            print(f"[RAG] Databricks connection failed, using local index fallback. Error: {e}")
            self.dbx_client = None

        # 2. Build local indices regardless (for fallback)
        self.local_bns_index.build()
        self.local_bns_rag.build_or_load()
        self.local_ipc_rag.build_or_load()
        
        return self

    # ── Public Query Methods ────────────────────────────────────────────────────

    def query_bns(self, question: str, top_k: int = 3) -> list[dict]:
        """Query BNS with hybrid search (0.7 semantic + 0.3 keyword) when Databricks is available."""
        if self.bns_dbx_index:
            try:
                pool = top_k * 3
                raw = self.bns_dbx_index.similarity_search(
                    query_text=question,
                    columns=["section_num", "Chapter_name", "Section__name", "content"],
                    num_results=pool
                )
                semantic_results = self._format_dbx_results(raw, "BNS")

                # Rank-based semantic scores: rank 0 → 1.0, rank pool-1 → ~0
                for rank, r in enumerate(semantic_results):
                    r["_semantic_score"] = (pool - rank) / pool

                # Keyword scores from local index
                kw_results = self.local_bns_index.search_keyword(question, top_k=pool)
                max_kw = max((r["_score"] for r in kw_results), default=1)
                kw_map = {
                    r["section_num"]: r["_score"] / max_kw
                    for r in kw_results
                }

                # Combine scores
                for r in semantic_results:
                    kw_score = kw_map.get(r["section_num"], 0.0)
                    r["_hybrid_score"] = 0.7 * r["_semantic_score"] + 0.3 * kw_score

                semantic_results.sort(key=lambda x: x["_hybrid_score"], reverse=True)
                return semantic_results[:top_k]

            except Exception as e:
                print(f"[RAG Error] BNS Databricks Query Failed, falling back to local: {e}")

        # Local Fallback
        kw_results = self.local_bns_index.search_keyword(question, top_k=top_k)
        if kw_results:
            return [{"title": f"BNS Section {r['section_num']} — {r['section_name']}",
                     "text": r["description"][:800],
                     "section_num": r["section_num"],
                     "source": "BNS"} for r in kw_results]
        return self.local_bns_rag.query(question, top_k=top_k)

    def query_ipc(self, question: str, top_k: int = 3) -> list[dict]:
        """Query IPC via Databricks first, local second."""
        if self.ipc_dbx_index:
            try:
                results = self.ipc_dbx_index.similarity_search(
                    query_text=question,
                    columns=["section_num", "section_label", "section_name", "content"],
                    num_results=top_k
                )
                return self._format_dbx_results(results, "IPC")
            except Exception as e:
                print(f"[RAG Error] IPC Databricks Query Failed, falling back to local: {e}")
                
        # Local Fallback
        return self.local_ipc_rag.query(question, top_k=top_k)

    def query_bns_section(self, section_num: int) -> Optional[dict]:
        """Get a specific BNS section by number."""
        return self.local_bns_index.get_section(section_num)

    def _format_dbx_results(self, dbx_results: dict, source: str) -> list[dict]:
        """Format Databricks JSON response into the standard app format."""
        docs = []
        if not dbx_results.get('result', {}).get('data_array'):
            return docs
            
        data = dbx_results['result']['data_array']
        for row in data:
            title_text = row[2] if len(row) > 2 else "Unknown"
            text_content = row[3] if len(row) > 3 else ""
            docs.append({
                "title": f"{source} Section {row[0]} - {title_text}",
                "text": text_content,
                "section_num": row[0],
                "source": source
            })
        return docs

    def format_context(self, results: list[dict]) -> str:
        """Format RAG results into a context string for the LLM."""
        parts = []
        for r in results:
            parts.append(f"**{r.get('title','Section')}**\n{r.get('text','')}")
        return "\n\n---\n\n".join(parts)

    def agentic_query(
        self,
        question: str,
        language: str = "auto",
        top_k: int = 3,
        chat_summary: str = "",
        recent_turns: list = [],
    ) -> str:
        """
        Two-step tool-calling pipeline:
          1. Router LLM decides which index(es) to query (bns / ipc / both)
          2. Fetch top_k results from each selected index
          3. Answer LLM generates final response with labeled context + conversation memory
        """
        from nyaya_sahayak.llm_client import route_query, answer_with_context

        tool = route_query(question)
        print(f"[Agentic] Router selected: {tool}")

        bns_context = ""
        ipc_context = ""

        if tool in ("bns", "both"):
            bns_results = self.query_bns(question, top_k=top_k)
            bns_context = self.format_context(bns_results)

        if tool in ("ipc", "both"):
            ipc_results = self.query_ipc(question, top_k=top_k)
            ipc_context = self.format_context(ipc_results)

        return answer_with_context(
            question=question,
            bns_context=bns_context,
            ipc_context=ipc_context,
            language=language,
            chat_summary=chat_summary,
            recent_turns=recent_turns,
        )


# ── Singleton ────────────────────────────────────────────────────────────────────
_engine: Optional[NyayaRAGEngine] = None

def get_engine() -> NyayaRAGEngine:
    """Return (or lazily initialize) the global RAG engine."""
    global _engine
    if _engine is None:
        _engine = NyayaRAGEngine().initialize()
    return _engine


if __name__ == "__main__":
    engine = get_engine()
    results = engine.query_bns("murder punishment")
    for r in results:
        print(r["title"])
        print(r["text"][:200])
        print("---")
