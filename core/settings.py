"""
Configuration management for Nyaya-Sahayak.
Loads settings from environment variables / .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env — try both the file's parent directory and CWD
ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env", override=True)
load_dotenv(Path.cwd() / ".env", override=True)

# ── LLM Configuration ──────────────────────────────────────────────────────────
HF_TOKEN         = os.getenv("HF_TOKEN", "")
HF_BASE_URL      = os.getenv("HF_BASE_URL", "https://api-inference.huggingface.co/v1")
SARVAM_MODEL     = os.getenv("SARVAM_MODEL", "sarvamai/sarvam-m")

# Optional direct Sarvam API (faster)
sarvam_api_key   = os.getenv("sarvam_api_key", "")
SARVAM_API_BASE  = os.getenv("SARVAM_API_BASE", "https://api.sarvam.ai/v1")

# Decide which endpoint to use
USE_SARVAM_DIRECT = bool(sarvam_api_key)
LLM_BASE_URL = SARVAM_API_BASE if USE_SARVAM_DIRECT else HF_BASE_URL
LLM_API_KEY  = sarvam_api_key  if USE_SARVAM_DIRECT else HF_TOKEN
LLM_MODEL    = "sarvam-m"      if USE_SARVAM_DIRECT else SARVAM_MODEL

# ── Data Paths ──────────────────────────────────────────────────────────────────
BNS_CSV_PATH          = Path(os.getenv("BNS_CSV_PATH",          ROOT / "bns_sections.csv"))
IPC_PDF_PATH          = Path(os.getenv("IPC_PDF_PATH",          ROOT / "250883_english_01042024.pdf"))
IPC_REPEALED_PDF_PATH = Path(os.getenv("IPC_REPEALED_PDF_PATH", ROOT / "repealedfileopen.pdf"))
IPC_BNS_MAPPING_PATH  = Path(os.getenv("IPC_BNS_MAPPING_PATH",  ROOT / "data/ipc_bns_mapping.csv"))
SCHEMES_JSON_PATH     = Path(os.getenv("SCHEMES_JSON_PATH",      ROOT / "data/schemes.json"))

# ── Index Cache Paths ───────────────────────────────────────────────────────────
BNS_INDEX_PATH  = Path(os.getenv("BNS_INDEX_PATH",  ROOT / "data/bns_index/bns_tree.json"))
IPC_INDEX_PATH  = Path(os.getenv("IPC_INDEX_PATH",  ROOT / "data/ipc_index/ipc_tree.json"))

# Ensure data dirs exist
(ROOT / "data" / "bns_index").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "ipc_index").mkdir(parents=True, exist_ok=True)

# ── Generation Settings ─────────────────────────────────────────────────────────
MAX_TOKENS_ANSWER   = 1024
MAX_TOKENS_THINK    = 2048
TEMPERATURE_LEGAL   = 0.2   # Low temperature for factual legal queries
TEMPERATURE_HINDI   = 0.3

# ── PageIndex Settings ──────────────────────────────────────────────────────────
PAGEINDEX_MAX_PAGES_PER_NODE   = 10
PAGEINDEX_MAX_TOKENS_PER_NODE  = 8000

print(f"[Config] LLM endpoint: {LLM_BASE_URL} | Model: {LLM_MODEL}")
