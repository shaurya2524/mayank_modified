"""
Sarvam-M LLM client via HuggingFace Inference API (OpenAI-compatible endpoint).
Supports Hindi/English responses and streaming.
"""

from __future__ import annotations
import os
import re
import sys
from pathlib import Path
from typing import Iterator, List, Dict, Optional

from openai import OpenAI

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from nyaya_sahayak.config import (
    LLM_BASE_URL, LLM_API_KEY, LLM_MODEL,
    MAX_TOKENS_ANSWER, TEMPERATURE_LEGAL
)

# ── System Prompts ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT_EN = """You are Nyaya-Sahayak (न्याय-सहायक), an expert Indian legal assistant specializing in:
1. Bharatiya Nyaya Sanhita 2023 (BNS) — India's new penal code
2. Indian Penal Code 1860 (IPC) — the old penal code now replaced by BNS
3. Government schemes and citizen rights

When answering:
- Always cite specific BNS section numbers (e.g., "BNS Section 101")
- When comparing with IPC, cite both (e.g., "IPC 302 → BNS 101")
- Keep language clear and accessible for common citizens
- Flag important legal disclaimers where needed
- Structure your answer with clear headings if long

You are NOT a lawyer and users should consult a qualified advocate for their specific case."""

SYSTEM_PROMPT_HI = """आप न्याय-सहायक हैं, एक विशेषज्ञ भारतीय कानूनी सहायक जो इन विषयों में विशेषज्ञता रखते हैं:
1. भारतीय न्याय संहिता 2023 (BNS) — भारत का नया दंड संहिता
2. भारतीय दंड संहिता 1860 (IPC) — पुरानी दंड संहिता जिसे BNS ने बदला
3. सरकारी योजनाएं और नागरिक अधिकार

उत्तर देते समय:
- हमेशा BNS धारा संख्या बताएं (जैसे "BNS धारा 101")
- IPC से तुलना करते समय दोनों बताएं (जैसे "IPC 302 → BNS 101")
- भाषा सरल और आम नागरिकों के लिए समझने योग्य रखें
- जहां जरूरी हो कानूनी अस्वीकरण लगाएं

आप वकील नहीं हैं — अपने विशिष्ट मामले के लिए योग्य अधिवक्ता से परामर्श लें।"""

# ── Client Factory ──────────────────────────────────────────────────────────────

def _get_client() -> OpenAI:
    """Return an OpenAI-compatible client pointed at Sarvam-M / HF endpoint."""
    return OpenAI(
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        timeout=120.0,
    )


# ── Core Chat Function ──────────────────────────────────────────────────────────

def chat(
    messages: List[Dict[str, str]],
    language: str = "en",
    max_tokens: int = MAX_TOKENS_ANSWER,
    temperature: float = TEMPERATURE_LEGAL,
    stream: bool = False,
    _system_override: Optional[str] = None,
) -> str | Iterator[str]:
    """
    Send a chat request to Sarvam-M.

    Args:
        messages:          List of {"role": ..., "content": ...} dicts (WITHOUT system msg)
        language:          "en" or "hi"
        max_tokens:        Maximum tokens in response
        temperature:       Sampling temperature
        stream:            If True, returns a generator yielding text chunks
        _system_override:  If set, replaces the default system prompt

    Returns:
        Full response string, or a generator if stream=True
    """
    client = _get_client()
    if _system_override:
        system_prompt = _system_override
    else:
        system_prompt = SYSTEM_PROMPT_HI if language == "hi" else SYSTEM_PROMPT_EN

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    if stream:
        return _stream_response(client, full_messages, max_tokens, temperature)
    else:
        try:
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=full_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            raw = response.choices[0].message.content or ""
            return _strip_think_tags(raw)
        except Exception as e:
            return f"⚠️ LLM Error: {e}\n\nPlease check your API token and network connection."


def _stream_response(
    client: OpenAI,
    messages: List[Dict[str, str]],
    max_tokens: int,
    temperature: float,
) -> Iterator[str]:
    """Yield text chunks from a streaming response."""
    try:
        stream = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )
        buffer = ""
        in_think = False
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            buffer += delta
            # Strip <think>...</think> tags on-the-fly
            while True:
                if not in_think:
                    think_start = buffer.find("<think>")
                    if think_start != -1:
                        yield buffer[:think_start]
                        buffer = buffer[think_start + 7:]
                        in_think = True
                    else:
                        yield buffer
                        buffer = ""
                        break
                else:
                    think_end = buffer.find("</think>")
                    if think_end != -1:
                        buffer = buffer[think_end + 8:]
                        in_think = False
                    else:
                        buffer = ""  # discard think content
                        break
    except Exception as e:
        yield f"⚠️ Streaming error: {e}"


def _strip_think_tags(text: str) -> str:
    """Remove Sarvam-M's <think>...</think> reasoning blocks from output."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


# ── Convenience Wrappers ────────────────────────────────────────────────────────

def ask_legal_question(question: str, language: str = "en", context: str = "") -> str:
    """Ask a straightforward legal question."""
    user_content = question
    if context:
        user_content = f"Context:\n{context}\n\nQuestion: {question}"
    return chat([{"role": "user", "content": user_content}], language=language)


def explain_section(
    section_text: str, section_ref: str, language: str = "en"
) -> str:
    """Explain a BNS section in plain language."""
    prompt = (
        f"Please explain {section_ref} in simple language that a common citizen can understand.\n\n"
        f"Section text:\n{section_text}"
    )
    if language == "hi":
        prompt = (
            f"कृपया {section_ref} को सरल भाषा में समझाएं जिसे एक आम नागरिक समझ सके।\n\n"
            f"धारा का पाठ:\n{section_text}"
        )
    return chat([{"role": "user", "content": prompt}], language=language)


def compare_sections(
    ipc_text: str,
    bns_text: str,
    ipc_ref: str,
    bns_ref: str,
    language: str = "en",
) -> str:
    """Generate a natural-language comparison between an IPC and BNS section."""
    prompt = f"""Compare {ipc_ref} (old IPC) with {bns_ref} (new BNS):

**{ipc_ref} — Indian Penal Code:**
{ipc_text}

**{bns_ref} — Bharatiya Nyaya Sanhita 2023:**
{bns_text}

Provide:
1. Key similarities
2. Key differences / changes
3. Practical impact for citizens
4. Any new provisions added or old provisions removed"""

    return chat([{"role": "user", "content": prompt}], language=language)


def classify_query(query: str) -> str:
    """
    Classify a user query into one of:
    'chatbot' | 'comparison' | 'translate_section' | 'scheme'
    """
    prompt = f"""Classify this legal query into exactly one category:
- chatbot: General legal question about BNS/IPC
- comparison: Wants to compare IPC vs BNS sections or scenarios
- translate_section: Wants to find BNS equivalent of an IPC section number
- scheme: About government schemes or eligibility

Query: "{query}"

Reply with ONLY the category name, nothing else."""

    result = chat(
        [{"role": "user", "content": prompt}],
        language="en",
        max_tokens=10,
        temperature=0.0,
    )
    result = result.strip().lower()
    valid = {"chatbot", "comparison", "translate_section", "scheme"}
    return result if result in valid else "chatbot"


FIR_SYSTEM_PROMPT = """You are an expert Indian legal document drafter specializing in First Information Reports (FIRs) under the Bharatiya Nyaya Sanhita 2023 (BNS).

You will be given:
- Complainant details
- Incident details (description, date, time, place)
- Accused details (if known)
- Witness details (if any)
- Relevant BNS sections retrieved from the incident description

Your task is to draft a formal, legally precise FIR in the following structure:

---
FIRST INFORMATION REPORT
(Under Section 173 BNS / As per CrPC Section 154)

FIR No.: [To be assigned by Police Station]
Date of Filing: {date}
Police Station: [To be filled by Officer]
District: [To be filled by Officer]

---
PART I — COMPLAINANT INFORMATION
Name:
Address:
Contact:
Relationship to Incident:

---
PART II — INCIDENT DETAILS
Date of Incident:
Time of Incident:
Place of Incident:
Nature of Offence:

---
PART III — DESCRIPTION OF INCIDENT
[Detailed factual account in formal language, first person, past tense. 3-5 paragraphs.]

---
PART IV — ACCUSED DETAILS
[If known, else write "Unknown at this time"]

---
PART V — WITNESSES
[If any, else write "None known at this time"]

---
PART VI — APPLICABLE BNS SECTIONS
[List each section with its name and a one-line reason why it applies]

---
PART VII — RELIEF SOUGHT
[State what action the complainant requests from police]

---
DECLARATION
I, [complainant name], hereby declare that the information given above is true and correct to the best of my knowledge and belief.

Signature of Complainant: _______________
Date: _______________
---

Rules:
- Use ONLY BNS sections provided in the context — do not invent or hallucinate section numbers
- Write in formal, precise legal English
- Keep the incident description factual — no emotional language
- If the incident description suggests sections not in the provided context, note them as "Further investigation may reveal additional applicable sections"
- Do NOT add sections from IPC — only BNS is currently in force"""


SUMMARIZE_PROMPT = """You are compressing a legal conversation into memory bullets for a future LLM call.

Extract ONLY concrete facts worth remembering:
- Specific BNS/IPC sections already discussed
- The user's legal situation (accused / victim / general inquiry)
- Key facts established (crime type, location, parties, outcome so far)
- Questions already fully answered (so they are not repeated)
- Any unresolved questions the user still has

Output 4-6 tight bullet points. No filler, no vague summaries. Every bullet must be a specific, reusable fact."""


ROUTER_SYSTEM_PROMPT = """You are a legal query router for an Indian law assistant.

You have access to two knowledge bases:
- BNS: Bharatiya Nyaya Sanhita 2023 — India's NEW penal code (currently in force)
- IPC: Indian Penal Code 1860 — the OLD penal code, now replaced by BNS

Your only job is to decide which knowledge base(s) a question needs.

Rules:
- Return "bns"  → question is about the current/new law, a BNS section, or general punishment today
- Return "ipc"  → question is specifically about the old/historical IPC law only
- Return "both" → question compares old vs new, asks about legal changes/transitions, mentions both IPC and BNS, or needs historical + current context for a complete answer

When in doubt between "bns" and "both", prefer "both" — it is always better to have more context.

Reply with ONLY one word: bns, ipc, or both. No explanation."""


ANSWER_SYSTEM_PROMPT_EN = """You are Nyaya-Sahayak (न्याय-सहायक), an expert Indian legal assistant specializing in the Bharatiya Nyaya Sanhita 2023 (BNS) and the Indian Penal Code 1860 (IPC).

You will be given retrieved legal context (from IPC, BNS, or both) followed by the user's question. Use ONLY the provided context to answer — do not hallucinate section numbers or provisions not present in the context.

Guidelines:
- Always cite specific section numbers (e.g., "BNS Section 103", "IPC Section 302")
- When both IPC and BNS context is available, clearly label OLD LAW (IPC) vs NEW LAW (BNS)
- Highlight key changes, additions, or removals between IPC and BNS where relevant
- Use plain, accessible language for common citizens — avoid dense legal jargon
- If the context does not contain enough information to answer, say so honestly
- Keep your answer structured with short paragraphs or bullet points where appropriate
- End with: "⚠️ This is for informational purposes only. For your specific case, consult a qualified advocate."

Respond in the SAME language as the user's question (Hindi if asked in Hindi, English otherwise)."""


ANSWER_SYSTEM_PROMPT_HI = """आप न्याय-सहायक हैं, एक विशेषज्ञ भारतीय कानूनी सहायक जो भारतीय न्याय संहिता 2023 (BNS) और भारतीय दंड संहिता 1860 (IPC) में विशेषज्ञता रखते हैं।

आपको कानूनी संदर्भ (IPC, BNS, या दोनों से) और उपयोगकर्ता का प्रश्न दिया जाएगा। केवल दिए गए संदर्भ का उपयोग करें — संदर्भ में न हो ऐसी धाराएं या प्रावधान न बनाएं।

दिशानिर्देश:
- हमेशा विशिष्ट धारा संख्या बताएं (जैसे "BNS धारा 103", "IPC धारा 302")
- जब IPC और BNS दोनों संदर्भ उपलब्ध हों, तो पुराना कानून (IPC) और नया कानून (BNS) स्पष्ट रूप से अलग करें
- IPC और BNS के बीच मुख्य बदलाव, जोड़ या हटाए गए प्रावधान बताएं
- आम नागरिकों के लिए सरल भाषा में उत्तर दें
- यदि संदर्भ में पर्याप्त जानकारी नहीं है तो ईमानदारी से बताएं
- ⚠️ अंत में लिखें: "यह केवल जानकारी के लिए है। अपने विशिष्ट मामले के लिए योग्य अधिवक्ता से परामर्श लें।"

उपयोगकर्ता के प्रश्न की भाषा में उत्तर दें।"""


def route_query(question: str) -> str:
    """
    Decide which knowledge base(s) to search for a given question.
    Returns: "bns", "ipc", or "both"
    """
    result = chat(
        [{"role": "user", "content": f'Question: "{question}"'}],
        language="en",
        max_tokens=5,
        temperature=0.0,
        # Override system prompt to router prompt
        _system_override=ROUTER_SYSTEM_PROMPT,
    )
    result = result.strip().lower().split()[0] if result.strip() else "bns"
    return result if result in {"bns", "ipc", "both"} else "bns"


def answer_with_context(
    question: str,
    bns_context: str,
    ipc_context: str,
    language: str = "auto",
    max_tokens: int = MAX_TOKENS_ANSWER,
    chat_summary: str = "",
    recent_turns: list = [],
) -> str:
    """
    Generate a final answer given retrieved IPC/BNS context and optional conversation memory.
    """
    sections = []
    if ipc_context:
        sections.append(f"[IPC CONTEXT — Old Law (Indian Penal Code 1860)]\n{ipc_context}")
    if bns_context:
        sections.append(f"[BNS CONTEXT — New Law (Bharatiya Nyaya Sanhita 2023)]\n{bns_context}")

    context_block = "\n\n---\n\n".join(sections) if sections else "[No relevant sections found in the knowledge base.]"

    memory_block = f"[CONVERSATION MEMORY]\n{chat_summary}\n\n" if chat_summary else ""

    current_message = f"""{memory_block}[LEGAL CONTEXT]\n{context_block}\n\n---\n\nUser Question: {question}"""

    # Build messages: inject recent turns as real conversation history
    messages = []
    for role, content in recent_turns:
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": current_message})

    system = ANSWER_SYSTEM_PROMPT_HI if language == "hi" else ANSWER_SYSTEM_PROMPT_EN
    return chat(
        messages,
        language=language,
        max_tokens=max_tokens,
        temperature=TEMPERATURE_LEGAL,
        _system_override=system,
    )


def generate_fir(
    complainant_name: str,
    complainant_address: str,
    complainant_contact: str,
    incident_date: str,
    incident_time: str,
    incident_place: str,
    incident_description: str,
    accused_details: str,
    witness_details: str,
    bns_context: str,
    language: str = "en",
) -> str:
    """Draft a formal FIR using complainant details and retrieved BNS sections."""
    user_message = f"""Draft a formal FIR using the details below.

COMPLAINANT DETAILS:
- Name: {complainant_name}
- Address: {complainant_address}
- Contact: {complainant_contact}

INCIDENT DETAILS:
- Date: {incident_date}
- Time: {incident_time}
- Place: {incident_place}
- Description: {incident_description}

ACCUSED DETAILS:
{accused_details if accused_details.strip() else "Unknown at this time"}

WITNESS DETAILS:
{witness_details if witness_details.strip() else "None known at this time"}

RETRIEVED BNS SECTIONS (use ONLY these):
{bns_context if bns_context else "[No sections retrieved — note this in the FIR]"}"""

    return chat(
        [{"role": "user", "content": user_message}],
        language=language,
        max_tokens=1800,
        temperature=0.15,
        _system_override=FIR_SYSTEM_PROMPT,
    )


def summarize_conversation(chat_summary: str, recent_turns: list) -> str:
    """Compress conversation history into bullet-point memory."""
    turns_text = "\n".join(
        f"{role.upper()}: {content}" for role, content in recent_turns
    )
    prior = f"[EXISTING SUMMARY]\n{chat_summary}\n\n" if chat_summary else ""
    prompt = f"{prior}[RECENT CONVERSATION]\n{turns_text}\n\nCompress all of the above into 4-6 bullet points."

    return chat(
        [{"role": "user", "content": prompt}],
        language="en",
        max_tokens=200,
        temperature=0.1,
        _system_override=SUMMARIZE_PROMPT,
    )


if __name__ == "__main__":
    # Quick smoke test
    print("Testing Sarvam-M connection...")
    response = ask_legal_question("What is the punishment for murder under BNS?")
    print(response[:500])
