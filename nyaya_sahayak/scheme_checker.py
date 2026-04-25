"""
Government scheme eligibility checker for Nyaya-Sahayak.
Primary:  Databricks Mosaic AI Vector Search on schemes_gold_index (3400+ schemes).
Fallback: Local data.parquet keyword search.
"""

from __future__ import annotations
import re
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from nyaya_sahayak.llm_client import chat

PARQUET_PATH = Path(__file__).parent.parent / "data.parquet"
MYSCHEME_BASE = "https://www.myscheme.gov.in/schemes"
DBX_ENDPOINT  = "nyaya_sahayak_endpoint"
DBX_INDEX     = "legal_catalog.nyaya_sahayak.schemes_gold_index"
DBX_COLUMNS   = ["scheme_name", "slug", "benefits", "eligibility", "schemeCategory", "level", "tags"]


def _tokenize(text: str) -> list[str]:
    return re.sub(r"[^\w\s]", "", str(text).lower()).split()


def _profile_to_query(profile: dict) -> str:
    """Convert a structured profile dict into a keyword-rich search query."""
    parts = []

    gender = profile.get("gender", "").lower()
    caste = profile.get("caste", "").lower()
    location = profile.get("location", "").lower()
    occupation = profile.get("occupation", "").lower()
    age = int(profile.get("age", 30))
    income = float(profile.get("annual_income_lpa", 5.0))

    if "female" in gender or "f" == gender:
        parts += ["women", "woman", "female", "girl", "mahila"]
    elif "male" in gender:
        parts += ["men", "man", "male"]

    if caste in ("sc", "scheduled caste"):
        parts += ["scheduled caste", "SC", "dalit", "marginalized", "backward"]
    if caste in ("st", "scheduled tribe"):
        parts += ["scheduled tribe", "ST", "tribal", "adivasi", "marginalized"]
    if caste == "obc":
        parts += ["OBC", "other backward class", "backward"]

    if location == "rural":
        parts += ["rural", "village", "panchayat", "gram sabha"]
    elif location == "urban":
        parts += ["urban", "city", "municipal", "town"]

    if "farmer" in occupation:
        parts += ["farmer", "agriculture", "agricultural", "kisan", "crop", "cultivation", "farming"]
    if "student" in occupation or profile.get("is_student"):
        parts += ["student", "scholarship", "education", "study", "college", "school", "training"]
    if "self-employed" in occupation or "business" in occupation or profile.get("is_entrepreneur"):
        parts += ["self-employed", "entrepreneur", "business", "MSME", "enterprise", "loan", "MUDRA"]
    if "unemployed" in occupation:
        parts += ["unemployment", "job", "employment", "skill training", "livelihood"]
    if "salaried" in occupation:
        parts += ["salaried", "worker", "employee", "employment"]

    if income < 2.5 or profile.get("is_bpl"):
        parts += ["BPL", "below poverty line", "low income", "poor", "economically weaker", "EWS", "ration card"]
    elif income < 5:
        parts += ["low income", "EWS", "marginalized", "financial assistance"]

    if profile.get("has_disability"):
        parts += ["disabled", "disability", "differently abled", "handicapped", "divyang", "specially abled"]
    if profile.get("is_violence_survivor"):
        parts += ["violence", "survivor", "victim", "domestic violence", "sexual assault", "nirbhaya", "women safety", "rehabilitation"]
    if profile.get("needs_legal_aid"):
        parts += ["legal aid", "legal assistance", "free lawyer", "NALSA", "legal services", "legal help"]
    if profile.get("has_agricultural_land"):
        parts += ["farmer", "agriculture", "kisan", "land", "crop", "farming", "PM kisan"]
    if profile.get("has_girl_child"):
        parts += ["girl child", "daughter", "sukanya", "beti bachao", "girl education", "girl welfare"]
    if profile.get("no_lpg"):
        parts += ["LPG", "gas connection", "cooking fuel", "ujjwala", "cylinder"]
    if profile.get("is_student"):
        parts += ["scholarship", "education", "tuition", "fee", "stipend"]

    if age < 18:
        parts += ["child", "minor", "children welfare", "youth"]
    elif age < 30:
        parts += ["youth", "young", "skill development"]
    elif age >= 60:
        parts += ["senior citizen", "elderly", "old age", "pension", "vridha"]

    return " ".join(parts)


class SchemeSearchEngine:
    """
    Searches 3400+ schemes.
    Primary:  Databricks Mosaic AI Vector Search (semantic).
    Fallback: Local data.parquet keyword overlap.
    """

    def __init__(self):
        self._dbx_index = None          # Mosaic AI vector index
        self.df: Optional[pd.DataFrame] = None   # local fallback
        self._token_sets: list[set] = []

    def load(self) -> "SchemeSearchEngine":
        # 1. Try Databricks Vector Search
        try:
            from databricks.vector_search.client import VectorSearchClient
            client = VectorSearchClient(disable_notice=True)
            self._dbx_index = client.get_index(
                endpoint_name=DBX_ENDPOINT,
                index_name=DBX_INDEX,
            )
            print("[Schemes] Databricks Vector Search connected ✅")
        except Exception as e:
            print(f"[Schemes] Databricks unavailable, using local parquet fallback. Error: {e}")
            self._dbx_index = None

        # 2. Always load local parquet as fallback
        if PARQUET_PATH.exists():
            self.df = pd.read_parquet(PARQUET_PATH)
            self.df = self.df.drop(columns=["Unnamed: 9"], errors="ignore")
            self.df["_content"] = (
                self.df["scheme_name"].fillna("") + " "
                + self.df["eligibility"].fillna("") + " "
                + self.df["benefits"].fillna("") + " "
                + self.df["schemeCategory"].fillna("") + " "
                + self.df["tags"].fillna("")
            )
            self._token_sets = [set(_tokenize(c)) for c in self.df["_content"]]
            print(f"[Schemes] Local parquet loaded ({len(self.df)} schemes)")

        return self

    def _search_databricks(self, query: str, top_k: int) -> list[dict]:
        """Semantic search via Mosaic AI Vector Search."""
        results = self._dbx_index.similarity_search(
            query_text=query,
            columns=DBX_COLUMNS,
            num_results=top_k,
        )
        rows = results.get("result", {}).get("data_array", [])
        out = []
        for i, row in enumerate(rows):
            # columns order: scheme_name, slug, benefits, eligibility, schemeCategory, level, tags
            slug = str(row[1]).strip() if len(row) > 1 else ""
            out.append({
                "name":        str(row[0]).strip(),
                "slug":        slug,
                "benefit":     str(row[2])[:250].strip() if len(row) > 2 else "",
                "description": str(row[3])[:150].strip() if len(row) > 3 else "",
                "category":    str(row[4]).strip()       if len(row) > 4 else "",
                "level":       str(row[5]).strip()       if len(row) > 5 else "",
                "tags":        str(row[6]).strip()       if len(row) > 6 else "",
                "url":         f"{MYSCHEME_BASE}/{slug}" if slug else "",
                "_score":      top_k - i,   # rank-based score
                "hindi_name":  "",
            })
        return out

    def _search_local(self, query: str, top_k: int) -> list[dict]:
        """Keyword overlap search on local parquet."""
        if self.df is None:
            return []
        query_tokens = set(_tokenize(query))
        scores = [len(query_tokens & s) for s in self._token_sets]
        self.df["_score"] = scores
        matched = self.df[self.df["_score"] > 0].sort_values("_score", ascending=False).head(top_k)
        return self._format_local(matched)

    def _format_local(self, df: pd.DataFrame) -> list[dict]:
        out = []
        for _, row in df.iterrows():
            slug = str(row.get("slug", "")).strip()
            out.append({
                "name":        str(row["scheme_name"]).strip(),
                "category":    str(row.get("schemeCategory", "")).strip(),
                "benefit":     str(row.get("benefits", ""))[:250].strip(),
                "description": str(row.get("eligibility", ""))[:150].strip(),
                "url":         f"{MYSCHEME_BASE}/{slug}" if slug else "",
                "_score":      int(row.get("_score", 0)),
                "hindi_name":  "",
                "level":       str(row.get("level", "")).strip(),
                "tags":        str(row.get("tags", "")).strip(),
            })
        return out

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search schemes — Databricks first, local fallback."""
        if self._dbx_index:
            try:
                return self._search_databricks(query, top_k)
            except Exception as e:
                print(f"[Schemes] Databricks query failed, falling back: {e}")
        return self._search_local(query, top_k)

    def _format_results(self, df: pd.DataFrame) -> list[dict]:
        results = []
        for _, row in df.iterrows():
            slug = str(row.get("slug", "")).strip()
            results.append({
                "name": str(row["scheme_name"]).strip(),
                "category": str(row.get("schemeCategory", "General")).strip(),
                "benefit": str(row.get("benefits", ""))[:250].strip(),
                "description": str(row.get("eligibility", ""))[:150].strip(),
                "url": f"{MYSCHEME_BASE}/{slug}" if slug else "",
                "_score": int(row.get("_score", 0)),
                "hindi_name": "",
                "level": str(row.get("level", "")).strip(),
                "tags": str(row.get("tags", "")).strip(),
                "application": str(row.get("application", ""))[:300].strip(),
            })
        return results

    def check_eligibility(self, profile: dict, language: str = "en") -> dict:
        """Search schemes from profile, return top matches + LLM explanation."""
        query = _profile_to_query(profile)
        top_matches = self.search(query, top_k=5)

        # LLM explanation
        profile_summary = ", ".join(
            f"{k}: {v}" for k, v in profile.items() if v and v is not False
        )
        schemes_summary = "\n".join(
            f"- {s['name']} ({s['category']}): {s['benefit'][:120]}"
            for s in top_matches
        ) or "None found"

        if language == "hi":
            prompt = f"""उपयोगकर्ता की प्रोफ़ाइल: {profile_summary}

मिलान की गई सरकारी योजनाएं:
{schemes_summary}

कृपया इन योजनाओं के बारे में सरल हिंदी में बताएं और आवेदन कैसे करें यह भी समझाएं।"""
        else:
            prompt = f"""User profile: {profile_summary}

Top matched government schemes:
{schemes_summary}

Explain these schemes in simple language — what each offers, who qualifies, and how to apply. Mention key documents needed."""

        explanation = chat(
            [{"role": "user", "content": prompt}],
            language=language,
            max_tokens=700,
        )

        return {
            "matched_schemes": top_matches,
            "total_matched": len(top_matches),
            "explanation": explanation,
            "profile": profile,
        }

    def get_categories(self) -> list[str]:
        if self.df is None:
            return []
        return sorted(self.df["schemeCategory"].dropna().unique().tolist())


# ── Singleton ────────────────────────────────────────────────────────────────────
_checker: Optional[SchemeSearchEngine] = None


def get_checker() -> SchemeSearchEngine:
    global _checker
    if _checker is None:
        _checker = SchemeSearchEngine().load()
    return _checker


if __name__ == "__main__":
    checker = get_checker()
    result = checker.check_eligibility({
        "age": 25, "gender": "female", "annual_income_lpa": 1.5,
        "caste": "sc", "location": "rural", "is_student": True,
        "has_girl_child": True,
    })
    for s in result["matched_schemes"]:
        print(f"[{s['_score']}] {s['name']} | {s['category']} | {s['benefit'][:80]}")
