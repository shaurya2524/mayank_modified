# ⚖️ Nyaya-Sahayak — AI-Powered Indian Legal Intelligence

> Making the Bharatiya Nyaya Sanhita (BNS 2023) accessible to every Indian citizen, in every Indian language.

[![Built with Databricks](https://img.shields.io/badge/Built_with-Databricks-FF3621?style=flat-square)](https://databricks.com)
[![Powered by Sarvam-M](https://img.shields.io/badge/LLM-Sarvam--M-d4af37?style=flat-square)](https://sarvam.ai)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=flat-square)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

---

## 🇮🇳 Why this exists

In **July 2024**, India's 164-year-old criminal code (IPC 1860) was replaced by the **Bharatiya Nyaya Sanhita 2023 (BNS)**. Overnight, every police officer, lawyer, paralegal, journalist, and citizen had to navigate a brand-new framework — but most have no easy way to:

- Understand what changed
- Find which BNS section replaces an IPC section they know
- Draft an FIR with the correct new provisions
- Check if an offense is bailable under BNSS 2023
- Discover government schemes they qualify for

**Nyaya-Sahayak** is an AI legal companion that bridges this gap — multilingual, free, and grounded in verifiable BNS text.

---

## ✨ Features

Six tools, one assistant — all available in **22+ Indian languages** (Sarvam-M powered):

| # | Tool | What it does |
|---|------|--------------|
| **§** | **Legal Counsel** | Agentic chatbot with hybrid search. Routes each question to BNS, IPC, or both knowledge bases, then synthesizes a citation-rich answer. Maintains conversation memory via sliding summaries. |
| **↔** | **Case Study Analyser** | Describe a scenario → get an animated SVG migration diagram showing how IPC sections map to BNS, side-by-side analysis, and AI synthesis. |
| **⊕** | **Section Lookup** | Translate any IPC section number to its BNS equivalent (300+ mappings). Browse all migrations in a paginated, searchable interface. |
| **◈** | **Scheme Advisor** | Conversational interview that profiles you across 13 dimensions, then matches against **3,400+ central & state government schemes** via Mosaic AI Vector Search. |
| **✦** | **FIR Draft Generator** | Describe an incident → get a properly-formatted, BNS-grounded FIR draft with applicable section citations. Downloadable as a `.txt` file. |
| **⊜** | **Bail Checker** | Enter a BNS section or describe an offense → get a structured bail eligibility verdict, citing BNSS 2023 procedures and the path to apply (BNSS § 480 / 482 / 483). |

---

## 🏗️ Architecture

### Medallion Data Pipeline (Databricks)

```
                  ┌─────────────────────────────────────────┐
                  │         BRONZE  (raw ingestion)         │
                  │   IPC PDFs · BNS CSV · Schemes Parquet  │
                  └──────────────────┬──────────────────────┘
                                     │
                              PySpark + Regex parsing
                                     │
                  ┌──────────────────▼──────────────────────┐
                  │        GOLD  (Delta tables, CDF)        │
                  │   bns_gold · ipc_gold · schemes_gold    │
                  └──────────────────┬──────────────────────┘
                                     │
                              Auto-sync via CDF
                                     │
                  ┌──────────────────▼──────────────────────┐
                  │   Mosaic AI Vector Search Indexes       │
                  │   bns_gold_index · ipc_gold_index ·     │
                  │   schemes_gold_index                    │
                  └──────────────────┬──────────────────────┘
                                     │
                            similarity_search()
                                     │
                  ┌──────────────────▼──────────────────────┐
                  │      Streamlit App (Databricks Apps)    │
                  └─────────────────────────────────────────┘
```

### RAG Flow — Agentic Tool Calling

```
User Question
     │
     ▼
┌─────────────────────────┐
│  Router LLM (Sarvam-M)  │ ─→  decides: "bns" / "ipc" / "both"
└────────────┬────────────┘
             │
   ┌─────────┴─────────┐
   ▼                   ▼
[BNS Index]      [IPC Index]      ─→ Hybrid search:
   │                   │              0.7 × semantic + 0.3 × keyword
   └─────────┬─────────┘
             ▼
┌────────────────────────────────┐
│  Conversation Memory Builder   │ ─→ summary + last 4 turns
└────────────────┬───────────────┘
                 ▼
┌────────────────────────────────┐
│  Answer LLM (Sarvam-M)         │ ─→ Final response with citations
└────────────────────────────────┘
```

### Resilience — 3-Layer Fallback

Every retrieval call has graceful degradation:

```
1. Databricks Mosaic AI Vector Search   (primary, semantic + hybrid)
2. Local in-memory keyword index        (CSV/Parquet, instant)
3. PageIndex tree retrieval             (markdown-based, last resort)
```

---

## 🧠 What's under the hood

### Memory & Caching

- **Sliding summary memory** — every 4 turns, older turns are compressed into 4-6 bullet points by the LLM. The next call sees `[CONVERSATION MEMORY]` + the last 4 raw turns. Token budget stays bounded forever.
- **Semantic query cache** — fresh queries (no conversation context) are cached using Jaccard similarity (threshold 0.72). 100 users asking "punishment for murder" = 1 LLM call.

### Hybrid Search (BNS retrieval)

```python
# 70% weight to Mosaic AI semantic similarity
# 30% weight to local keyword overlap (synonym handling)
hybrid_score = 0.7 * semantic_rank_score + 0.3 * keyword_overlap_score
```

This bubbles up sections that share keywords with the query but rank lower semantically.

### Multilingual

Sarvam-M is trained on 22 Indian scheduled languages. The chatbot offers:
- **English** — always responds in English
- **हिंदी** — always responds in Hindi
- **Auto-detect** — responds in whatever language you typed (Tamil → Tamil, Bengali → Bengali, etc.)

### Bail Eligibility Logic

The Bail Checker prompt teaches the LLM the rules-of-thumb:
- Punishment ≤ 3 years → typically bailable
- Punishment > 3 years → non-bailable, court's discretion
- Death/life imprisonment offenses → always non-bailable
- Women, minors, sick/infirm → courts more liberal
- First-time offenders → bail with conditions usually granted

Then it produces a structured verdict: **BAILABLE / NON-BAILABLE / ANTICIPATORY BAIL ADVISABLE**, with the exact BNSS section to use and steps to apply.

---

## 📁 Project Structure

```
nayay-sahinta-databricks/
├── app.py                           # Streamlit application (6 tabs)
├── app.yaml                         # Databricks Apps configuration
├── requirements.txt                 # Python dependencies
│
├── core/                            # Application logic
│   ├── settings.py                  # Config & env-var loading
│   ├── sarvam_engine.py             # LLM client + system prompts
│   │   ├─ route_query()             #   tool-call router
│   │   ├─ answer_with_context()     #   final answer generator
│   │   ├─ generate_fir()            #   FIR drafting
│   │   ├─ check_bail_eligibility()  #   bail assessment
│   │   └─ summarize_conversation()  #   memory compressor
│   ├── legal_retriever.py           # Hybrid RAG engine (Databricks + local)
│   ├── law_diff.py                  # IPC ↔ BNS comparison + translation
│   ├── welfare_matcher.py           # 3400+ scheme search engine
│   ├── query_memory.py              # Semantic query cache
│   ├── ingestion.py                 # PySpark data pipeline
│   └── pdf_parser.py                # IPC PDF extraction
│
├── notebooks/
│   └── medallion_pipeline.py        # Bronze → Gold ETL on Databricks
│
├── scripts/
│   ├── build_mappings.py            # LLM-assisted IPC→BNS mapping generator
│   └── build_diagram.py             # Architecture diagram renderer
│
├── data/
│   ├── ipc_bns_mapping.csv          # 341 hand-curated + LLM mappings
│   ├── bns_full.md                  # BNS markdown corpus
│   ├── ipc_full.md                  # IPC markdown corpus
│   └── query_cache.json             # Semantic query cache
│
├── data.parquet                     # 3,400+ government schemes
├── bns_sections.csv                 # All 358 BNS sections
├── 250883_english_01042024.pdf      # IPC raw text
└── repealedfileopen.pdf             # Repealed IPC provisions
```

---

## 🚀 Quick Start

### Local development

```bash
git clone https://github.com/shaurya2524/mayank_modified.git
cd mayank_modified

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

export SARVAM_API_KEY=your_sarvam_key_here
streamlit run app.py
```

App will be live at `http://localhost:8501`.

### Environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `SARVAM_API_KEY` | ✅ (or HF_TOKEN) | Direct Sarvam-M API access |
| `HF_TOKEN` | Optional | HuggingFace fallback for Sarvam-M |
| `DATABRICKS_HOST` | Optional | For Mosaic AI Vector Search |
| `DATABRICKS_TOKEN` | Optional | Databricks PAT for Vector Search |

If only `SARVAM_API_KEY` is set, the app falls back to local indexes — chatbot, schemes, FIR, bail all work, just without Mosaic AI.

---

## ☁️ Deployment

### Option 1: Databricks Apps (Production)

1. **Upload data files to a Volume:**
   ```
   /Volumes/legal_catalog/nyaya_sahayak/ipc/250883_english_01042024.pdf
   /Volumes/legal_catalog/nyaya_sahayak/ipc/repealedfileopen.pdf
   /Volumes/legal_catalog/nyaya_sahayak/ipc/bns_sections.csv
   /Volumes/legal_catalog/nyaya_sahayak/schemes/data.parquet
   ```

2. **Run** `notebooks/medallion_pipeline.py` to create Delta tables:
   - `bns_gold` · `ipc_gold` · `repealed_gold` · `schemes_gold`

3. **Create Vector Search indexes** on the `nyaya_sahayak_endpoint`:
   - `bns_gold_index` (index `content` column)
   - `ipc_gold_index`
   - `schemes_gold_index`

4. **Deploy as a Databricks App:**
   - Compute → Apps → Create App
   - Connect this GitHub repo, branch `main`
   - The `app.yaml` injects `SARVAM_API_KEY` from Databricks Secrets

### Option 2: Streamlit Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io)
2. Connect this repo, main file `app.py`
3. Add secrets via the dashboard:
   ```toml
   SARVAM_API_KEY = "your_key"
   HF_TOKEN = "optional_fallback"
   ```

App falls back to local indexes since Streamlit Cloud has no Databricks access.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Sarvam-M (22+ Indian languages, hosted natively on api.sarvam.ai) |
| **Vector Search** | Databricks Mosaic AI Vector Search |
| **Storage** | Delta Lake (Bronze → Gold medallion) |
| **Compute** | PySpark (ingestion), Streamlit (serving) |
| **Frontend** | Streamlit + custom HTML/CSS components, SVG animations |
| **Fonts** | Cormorant Garamond (display) + Inter (body) + Noto Sans Devanagari |
| **Hosting** | Databricks Apps (serverless) / Streamlit Cloud |

---

## 📊 Numbers

- **358** BNS sections indexed
- **341** IPC → BNS mappings (auto-generated + hand-curated)
- **3,400+** central & state government schemes
- **22+** Indian languages supported
- **6** distinct AI tools in one app

---

## 🎨 Design Philosophy

The UI uses a **black + antique gold** palette — inspired by traditional Indian legal documents and the gravitas of the courtroom. **Cormorant Garamond** for headings (a classic legal serif), **Inter** for body text. No neon, no chat-app feel — just authority and clarity.

Every output (chat bubbles, scheme cards, FIR drafts, bail verdicts, migration diagrams) renders inside scoped HTML components for pixel-perfect control over what Streamlit normally restricts.

---

## 🙏 Acknowledgments

- **Sarvam AI** — for open access to Sarvam-M, the only Indian-multilingual LLM that makes this possible
- **Databricks** — for Mosaic AI Vector Search and the Apps platform
- **Government of India** — for publishing BNS, BNSS, and the MyScheme dataset openly
- **The legal community** — whose IPC↔BNS comparison guides informed the mapping logic

---

## ⚠️ Disclaimer

Nyaya-Sahayak provides information for educational and reference purposes only. AI-generated content can be incorrect or incomplete. **For any legal matter affecting your life, liberty, or property, consult a qualified advocate.** The developers are not responsible for outcomes from acting on the app's output.

---

**Built with care for India.** 🇮🇳
