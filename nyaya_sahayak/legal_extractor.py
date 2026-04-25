"""
Self-contained mapping extractor using legal_extractor's LLM setup.
Chunks the PDF properly to extract 300+ mappings.
Run from project root: python generate_mappings.py
"""
import sys, os, json, re, time
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# Load env so LLM creds work
from dotenv import load_dotenv
load_dotenv(str(ROOT / ".env"))

from nyaya_sahayak.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, ROOT
from nyaya_sahayak.comparator import _BUILTIN_MAPPING, IPC_BNS_MAPPING_PATH
from openai import OpenAI

# ── Config ───────────────────────────────────────────────────────────────────
CHUNK_SIZE   = 3000   # chars per chunk sent to LLM
CHUNK_OVERLAP = 300   # overlap so section boundaries aren't missed
SLEEP_BETWEEN_CHUNKS = 1.5  # seconds, avoids rate limiting
PDF_FILES = [
    ROOT / "repealedfileopen.pdf",
    ROOT / "250883_english_01042024.pdf",
]

# ── LLM Client ───────────────────────────────────────────────────────────────
def get_client():
    return OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL, timeout=120.0)

# ── Extract from one chunk ────────────────────────────────────────────────────
def extract_mappings_from_chunk(chunk: str, client, chunk_num: int) -> list[dict]:
    prompt = f"""You are analyzing Indian legal text that shows the transition from IPC (Indian Penal Code 1860) to BNS (Bharatiya Nyaya Sanhita 2023).

Extract ALL IPC → BNS section mappings from the text below.
Return ONLY a valid JSON array. No explanation, no markdown, just the array.

Format:
[
  {{
    "ipc_section": "302",
    "ipc_name": "Punishment for Murder",
    "bns_section": "103",
    "bns_name": "Punishment for Murder",
    "category": "Homicide",
    "note": "Brief note on key change if any"
  }}
]

Rules:
- Only include entries where BOTH an IPC section number AND a BNS section number are clearly identifiable
- If a BNS section has no IPC equivalent, use "NEW" as ipc_section
- If an IPC section was repealed with no BNS equivalent, use "REPEALED" as bns_section
- category should be one of: Homicide, Women, Sexual Offences, Kidnapping, Trafficking, Property, Fraud, Forgery, Public Order, State Security, Reputation, Intimidation, Marriage, Domestic Violence, Public Servant, Justice, Organised Crime, Terrorism, Hurt, Other
- Extract as many mappings as you can find, even partial ones

Text:
{chunk}

JSON array:"""

    try:
        client_obj = get_client()
        response = client_obj.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.0,
        )
        raw = response.choices[0].message.content or ""

        # Strip markdown fences if present
        raw = re.sub(r"```json|```", "", raw).strip()

        # Find JSON array
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if not match:
            print(f"  [Chunk {chunk_num}] No JSON array found in response")
            return []

        data = json.loads(match.group())
        if isinstance(data, list):
            print(f"  [Chunk {chunk_num}] Extracted {len(data)} mappings")
            return data
    except json.JSONDecodeError as e:
        print(f"  [Chunk {chunk_num}] JSON parse error: {e}")
    except Exception as e:
        print(f"  [Chunk {chunk_num}] LLM error: {e}")
    return []

# ── Read entire PDF ───────────────────────────────────────────────────────────
def read_full_pdf(pdf_path: Path) -> str:
    import pdfplumber
    texts = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        total = len(pdf.pages)
        print(f"  PDF has {total} pages — reading all...")
        for i, page in enumerate(pdf.pages):   # ← no page limit
            t = page.extract_text() or ""
            if t.strip():
                texts.append(t)
            if (i+1) % 20 == 0:
                print(f"  Read {i+1}/{total} pages...")
    return "\n".join(texts)

# ── Chunk text with overlap ───────────────────────────────────────────────────
def chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    print(f"  Split into {len(chunks)} chunks of ~{CHUNK_SIZE} chars")
    return chunks

# ── Validate a single mapping row ────────────────────────────────────────────
def is_valid(entry: dict) -> bool:
    ipc = str(entry.get("ipc_section", "")).strip()
    bns = str(entry.get("bns_section", "")).strip()
    ipc_name = str(entry.get("ipc_name", "")).strip()
    bns_name = str(entry.get("bns_name", "")).strip()
    # Must have section numbers and names
    if not ipc or not bns:
        return False
    if not ipc_name or not bns_name:
        return False
    # IPC section must be a number or NEW
    if ipc not in ("NEW",) and not re.match(r'^\d{1,3}[A-Z]?$', ipc):
        return False
    return True

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    client = get_client()
    all_mappings = []

    # Start with built-in mappings
    builtin_df = pd.DataFrame(_BUILTIN_MAPPING)
    print(f"Starting with {len(builtin_df)} built-in mappings")
    all_mappings.extend(_BUILTIN_MAPPING)

    # Process each PDF
    for pdf_path in PDF_FILES:
        if not pdf_path.exists():
            print(f"\n⚠️  PDF not found, skipping: {pdf_path.name}")
            continue

        print(f"\n📄 Processing: {pdf_path.name}")
        full_text = read_full_pdf(pdf_path)
        print(f"  Total text length: {len(full_text):,} chars")

        chunks = chunk_text(full_text)
        pdf_mappings = []

        for i, chunk in enumerate(chunks):
            print(f"\n  Chunk {i+1}/{len(chunks)}...")
            extracted = extract_mappings_from_chunk(chunk, client, i+1)
            pdf_mappings.extend(extracted)
            time.sleep(SLEEP_BETWEEN_CHUNKS)

        print(f"\n  Raw extracted from {pdf_path.name}: {len(pdf_mappings)}")
        all_mappings.extend(pdf_mappings)

    # Build DataFrame and clean up
    df = pd.DataFrame(all_mappings)

    # Ensure all required columns exist
    for col in ["ipc_section", "ipc_name", "bns_section", "bns_name", "category", "note"]:
        if col not in df.columns:
            df[col] = ""

    # Normalize types
    df["ipc_section"] = df["ipc_section"].astype(str).str.strip()
    df["bns_section"] = df["bns_section"].astype(str).str.strip()
    df["ipc_name"]    = df["ipc_name"].astype(str).str.strip()
    df["bns_name"]    = df["bns_section"].astype(str).str.strip()
    df["category"]    = df["category"].astype(str).str.strip()
    df["note"]        = df["note"].astype(str).str.strip()

    # Filter invalid rows
    before = len(df)
    df = df[df.apply(is_valid, axis=1)]
    print(f"\n  Removed {before - len(df)} invalid rows")

    # Deduplicate — keep first occurrence (built-in takes priority)
    df = df.drop_duplicates(subset=["ipc_section", "bns_section"], keep="first")

    # Sort nicely
    def sort_key(s):
        try: return (0, int(re.sub(r'[A-Z]', '', s)))
        except: return (1, s)
    df["_sort"] = df["ipc_section"].apply(sort_key)
    df = df.sort_values("_sort").drop(columns=["_sort"])

    # Save
    IPC_BNS_MAPPING_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(IPC_BNS_MAPPING_PATH, index=False)

    print(f"\n✅ Final mapping: {len(df)} entries saved to:")
    print(f"   {IPC_BNS_MAPPING_PATH}")
    print(f"\nSample:")
    print(df[["ipc_section","ipc_name","bns_section","bns_name","category"]].head(10).to_string())

if __name__ == "__main__":
    main()