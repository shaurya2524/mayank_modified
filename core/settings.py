"""
Configuration management for Nyaya-Sahayak.
"""

import os
from pathlib import Path

try:
    import streamlit as st
    _secrets = dict(st.secrets)
except Exception:
    _secrets = {}

ROOT = Path(__file__).parent.parent

LLM_BASE_URL = "https://api.sarvam.ai/v1"
LLM_API_KEY  = _secrets.get("SARVAM_API_KEY", os.getenv("SARVAM_API_KEY", ""))
LLM_MODEL    = "sarvam-m"

print(f"[Config] LLM endpoint: {LLM_BASE_URL} | Model: {LLM_MODEL}")

BNS_CSV_PATH          = Path(os.getenv("BNS_CSV_PATH",          ROOT / "bns_sections.csv"))
IPC_PDF_PATH          = Path(os.getenv("IPC_PDF_PATH",          ROOT / "250883_english_01042024.pdf"))
IPC_REPEALED_PDF_PATH = Path(os.getenv("IPC_REPEALED_PDF_PATH", ROOT / "repealedfileopen.pdf"))
IPC_BNS_MAPPING_PATH  = Path(os.getenv("IPC_BNS_MAPPING_PATH",  ROOT / "data/ipc_bns_mapping.csv"))
SCHEMES_JSON_PATH     = Path(os.getenv("SCHEMES_JSON_PATH",      ROOT / "data/schemes.json"))

BNS_INDEX_PATH  = Path(os.getenv("BNS_INDEX_PATH",  ROOT / "data/bns_index/bns_tree.json"))
IPC_INDEX_PATH  = Path(os.getenv("IPC_INDEX_PATH",  ROOT / "data/ipc_index/ipc_tree.json"))

(ROOT / "data" / "bns_index").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "ipc_index").mkdir(parents=True, exist_ok=True)

MAX_TOKENS_ANSWER   = 1024
MAX_TOKENS_THINK    = 2048
TEMPERATURE_LEGAL   = 0.2
TEMPERATURE_HINDI   = 0.3

PAGEINDEX_MAX_PAGES_PER_NODE   = 10
PAGEINDEX_MAX_TOKENS_PER_NODE  = 8000
