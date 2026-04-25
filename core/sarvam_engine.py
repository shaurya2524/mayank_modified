import os
import requests
from typing import List, Dict

# ── CONFIG ─────────────────────────────────────────

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY") or "sk_your_backup_key_here"
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"

if not SARVAM_API_KEY:
    raise ValueError("No API key found")

print("API KEY EXISTS:", bool(SARVAM_API_KEY))


# ── CORE CHAT FUNCTION ─────────────────────────────

def chat(messages: List[Dict[str, str]]) -> str:
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "sarvam-m",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 500,
    }

    try:
        response = requests.post(SARVAM_URL, headers=headers, json=payload)

        # 🔴 IMPORTANT DEBUG
        print("STATUS CODE:", response.status_code)
        print("RAW RESPONSE:", response.text)

        if response.status_code != 200:
            return f"❌ API Error: {response.text}"

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"⚠️ LLM Error: {str(e)}"


# ── SIMPLE WRAPPER ─────────────────────────────────

def ask_legal_question(question: str) -> str:
    return chat([
        {"role": "user", "content": question}
    ])


# ── TEST ───────────────────────────────────────────

if __name__ == "__main__":
    print("Testing...")
    print(ask_legal_question("What is punishment for theft?"))
