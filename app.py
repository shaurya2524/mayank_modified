"""
Nyaya-Sahayak — Premium Streamlit UI
"""
import sys, os, json
from pathlib import Path
import streamlit as st
import pandas as pd


ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# ── Page Config ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="न्याय-सहायक | Nyaya-Sahayak",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&family=Inter:wght@300;400;500;600;700&family=Noto+Sans+Devanagari:wght@300;400;500;600&display=swap');

/* ═══════════════════════════════════════════════════════════
   RESET & BASE — BLACK + GOLD THEME
═══════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main,
.block-container {
    background-color: #0a0a0a !important;
    color: #e8e0d0 !important;
    font-family: 'Inter', 'Noto Sans Devanagari', sans-serif !important;
}

[data-testid="stAppViewContainer"] > section,
[data-testid="stAppViewContainer"] > section > div,
.stApp { background-color: #0a0a0a !important; }

[data-testid="stHeader"] { background: #0a0a0a !important; border-bottom: 1px solid #1e1e1e !important; }
[data-testid="stSidebar"] { background: #111111 !important; border-right: 1px solid #1e1e1e !important; }
[data-testid="stSidebar"] * { color: #e8e0d0 !important; }

/* ═══════════════════════════════════════════════════════════
   HERO BANNER
═══════════════════════════════════════════════════════════ */
.hero {
    background: linear-gradient(180deg, #111111 0%, #0a0a0a 100%);
    border: 1px solid #2a2a2a;
    border-top: 3px solid #d4af37;
    padding: 2.2rem 2.5rem 1.8rem;
    text-align: center;
    margin-bottom: 1.4rem;
}
.hero-emblem {
    font-size: 2rem; line-height: 1; margin-bottom: .5rem;
    display: block; color: #d4af37;
}
.hero h1 {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 2.8rem; font-weight: 700;
    letter-spacing: 1px; line-height: 1.1;
    margin-bottom: .4rem;
    color: #d4af37;
}
.hero .tagline {
    color: #888; font-size: .88rem;
    letter-spacing: 2px; text-transform: uppercase;
    margin-bottom: .9rem; font-weight: 400;
}
.hero-rule { width: 40px; height: 1px; background: #d4af37; margin: 0 auto .9rem; opacity: .6; }
.hero .subtitle { display: inline-flex; flex-wrap: wrap; gap: .5rem; justify-content: center; }
.hero .pill {
    background: transparent; border: 1px solid #2a2a2a;
    padding: .2rem .8rem; font-size: .68rem;
    color: #666; letter-spacing: 1px; font-weight: 500; text-transform: uppercase;
}

/* ═══════════════════════════════════════════════════════════
   STAT CARDS
═══════════════════════════════════════════════════════════ */
.stat-card {
    background: #111111; border: 1px solid #2a2a2a; border-top: 2px solid #d4af37;
    padding: 1.1rem 1.2rem; display: flex; align-items: center; gap: .9rem;
    transition: border-top-color .2s, box-shadow .2s;
}
.stat-card:hover { box-shadow: 0 4px 24px rgba(212,175,55,0.08); border-top-color: #b8960c; }
.stat-icon {
    width: 40px; height: 40px; background: rgba(212,175,55,0.07);
    border: 1px solid rgba(212,175,55,0.15); display: flex;
    align-items: center; justify-content: center; font-size: 1.1rem;
    flex-shrink: 0; color: #d4af37;
}
.stat-icon.amber, .stat-icon.violet, .stat-icon.green, .stat-icon.blue { background: rgba(212,175,55,0.06); }
.stat-body { display: flex; flex-direction: column; gap: .12rem; }
.stat-value {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.6rem; font-weight: 700; color: #d4af37; line-height: 1;
}
.stat-label { font-size: .62rem; color: #666; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600; }
.lang-card {
    background: #111111; border: 1px solid #2a2a2a; border-top: 2px solid #555;
    padding: .9rem 1.2rem; display: flex; align-items: center; gap: .8rem;
    color: #888; font-size: .85rem; height: 100%;
}
.lang-card .lang-icon { font-size: 1.2rem; color: #d4af37; }
.lang-card strong { color: #e8e0d0; font-weight: 600; }

/* ═══════════════════════════════════════════════════════════
   CARDS
═══════════════════════════════════════════════════════════ */
.card {
    background: #111111; border: 1px solid #2a2a2a;
    border-left: 3px solid #d4af37;
    padding: 1.2rem 1.5rem; margin-bottom: 1.2rem;
    transition: box-shadow .2s;
}
.card:hover { box-shadow: 0 4px 20px rgba(212,175,55,0.07); }
.card h4 {
    font-family: 'Cormorant Garamond', Georgia, serif;
    color: #d4af37; font-size: 1.05rem; font-weight: 600;
    margin-bottom: .4rem; display: flex; align-items: center; gap: .5rem;
}
.card p { color: #888; font-size: .88rem; line-height: 1.7; }

/* ═══════════════════════════════════════════════════════════
   COMPARISON TABLE
═══════════════════════════════════════════════════════════ */
.compare-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.compare-table th {
    background: #111111; color: #d4af37; padding: .75rem 1rem;
    text-align: left; font-size: .72rem; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase; border-bottom: 1px solid #2a2a2a;
}
.compare-table td {
    padding: .75rem 1rem; border-bottom: 1px solid #1a1a1a;
    color: #ccc; font-size: .87rem; vertical-align: top;
}
.compare-table tr:hover td { background: #111111; }

/* ═══════════════════════════════════════════════════════════
   TAGS
═══════════════════════════════════════════════════════════ */
.tag-bns {
    display: inline-flex; align-items: center; gap: .3rem;
    background: rgba(212,175,55,0.08); color: #d4af37;
    border: 1px solid rgba(212,175,55,0.25);
    padding: 3px 11px; font-size: .72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .6px;
}
.tag-ipc {
    display: inline-flex; align-items: center; gap: .3rem;
    background: rgba(255,255,255,0.05); color: #888;
    border: 1px solid #2a2a2a;
    padding: 3px 11px; font-size: .72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .6px;
}
.tag-new {
    display: inline-flex; align-items: center; gap: .3rem;
    background: rgba(212,175,55,0.06); color: #b8960c;
    border: 1px solid rgba(212,175,55,0.18);
    padding: 3px 11px; font-size: .72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .6px;
}

/* ═══════════════════════════════════════════════════════════
   SCHEME BADGES
═══════════════════════════════════════════════════════════ */
.scheme-badge {
    display: inline-block; padding: 2px 8px;
    font-size: .65rem; font-weight: 700; margin-right: .3rem; border: 1px solid;
    text-transform: uppercase; letter-spacing: .8px; color: #d4af37;
    background: rgba(212,175,55,0.07); border-color: rgba(212,175,55,0.2);
}
.scheme-badge.cat-agriculture,.scheme-badge.cat-social,.scheme-badge.cat-education,
.scheme-badge.cat-health,.scheme-badge.cat-housing,.scheme-badge.cat-finance,
.scheme-badge.cat-women,.scheme-badge.cat-legal,.scheme-badge.cat-default {
    color: #d4af37; background: rgba(212,175,55,0.06); border-color: rgba(212,175,55,0.18);
}

/* ═══════════════════════════════════════════════════════════
   SCHEME CARDS
═══════════════════════════════════════════════════════════ */
.scheme-card {
    background: #111111; border: 1px solid #2a2a2a;
    border-left: 3px solid #d4af37;
    padding: 1.1rem 1.3rem; margin-bottom: .9rem;
    transition: box-shadow .2s;
}
.scheme-card:hover { box-shadow: 0 4px 20px rgba(212,175,55,0.08); }
.scheme-card .sc-title   { color: #e8e0d0; font-weight: 700; font-size: .95rem; font-family: 'Cormorant Garamond', Georgia, serif; }
.scheme-card .sc-benefit { color: #d4af37; font-size: .84rem; margin: .35rem 0; font-weight: 500; }
.scheme-card .sc-eligibility { color: #666; font-size: .81rem; line-height: 1.6; }

/* ═══════════════════════════════════════════════════════════
   CHAT BUBBLES
═══════════════════════════════════════════════════════════ */
.msg-user {
    background: rgba(212,175,55,0.06); border: 1px solid rgba(212,175,55,0.15);
    border-left: 3px solid #d4af37; padding: .9rem 1.1rem;
    margin: .7rem 0 .7rem 14%; color: #e8e0d0; font-size: .92rem; line-height: 1.7;
}
.msg-bot {
    background: #111111; border: 1px solid #2a2a2a;
    border-left: 3px solid #555; padding: .9rem 1.1rem;
    margin: .7rem 14% .7rem 0; color: #ccc; font-size: .92rem; line-height: 1.75;
}
.msg-bot strong { color: #d4af37; }

/* ═══════════════════════════════════════════════════════════
   TABS
═══════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important; background: transparent !important; padding: 0 !important;
    border-bottom: 1px solid #2a2a2a !important; margin-bottom: 1.2rem !important;
}
.stTabs [data-baseweb="tab"] {
    color: #555 !important; background: transparent !important; border-radius: 0 !important;
    padding: .55rem 1.3rem !important; font-size: .75rem !important; font-weight: 600 !important;
    letter-spacing: 1.2px !important; text-transform: uppercase !important;
    border-bottom: 2px solid transparent !important; margin-bottom: -1px !important;
    transition: color .15s, border-color .15s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #d4af37 !important; background: transparent !important; border-bottom-color: rgba(212,175,55,0.3) !important; }
.stTabs [aria-selected="true"] { color: #d4af37 !important; border-bottom: 2px solid #d4af37 !important; font-weight: 700 !important; background: transparent !important; box-shadow: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 0 !important; }

/* ═══════════════════════════════════════════════════════════
   INPUTS & FORMS
═══════════════════════════════════════════════════════════ */
.stTextInput input, .stTextArea textarea,
div[data-baseweb="select"] > div, .stNumberInput input {
    background: #111111 !important; border: 1px solid #2a2a2a !important;
    color: #e8e0d0 !important; font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #d4af37 !important; box-shadow: 0 0 0 2px rgba(212,175,55,0.12) !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label,
.stNumberInput label, .stCheckbox label, .stRadio label { color: #888 !important; font-size: .83rem !important; font-weight: 500 !important; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #444 !important; }
div[data-baseweb="select"] span { color: #e8e0d0 !important; }
div[data-baseweb="popover"] { background: #111111 !important; border: 1px solid #2a2a2a !important; }

/* ═══════════════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════════════ */
.stButton > button, .stFormSubmitButton > button {
    background: transparent !important; color: #d4af37 !important;
    border: 1px solid #d4af37 !important;
    font-weight: 600 !important; font-size: .78rem !important;
    letter-spacing: 1.2px !important; text-transform: uppercase !important;
    padding: .55rem 1.6rem !important; transition: all .2s ease !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background: rgba(212,175,55,0.1) !important; box-shadow: 0 0 20px rgba(212,175,55,0.15) !important;
}
[data-testid="stDownloadButton"] button {
    background: transparent !important; border: 1px solid #555 !important;
    color: #888 !important; letter-spacing: 1px !important;
}

/* ═══════════════════════════════════════════════════════════
   MISC
═══════════════════════════════════════════════════════════ */
.stSpinner > div { border-top-color: #d4af37 !important; }
hr { border: none !important; border-top: 1px solid #1e1e1e !important; margin: 1rem 0 !important; }
[data-testid="metric-container"] { background: #111111; border: 1px solid #2a2a2a; border-top: 2px solid #d4af37; }
[data-testid="metric-container"] label { color: #555 !important; font-size: .65rem !important; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600 !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #d4af37 !important; font-weight: 700 !important; font-family: 'Cormorant Garamond', Georgia, serif !important; }
.stCheckbox label { color: #888 !important; }
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] h4 { font-family: 'Cormorant Garamond', Georgia, serif !important; color: #d4af37 !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #111111; }
::-webkit-scrollbar-thumb { background: #333; }
::-webkit-scrollbar-thumb:hover { background: #d4af37; }
.footer { text-align: center; color: #333; font-size: .74rem; margin-top: 3rem; padding-top: 1.2rem; border-top: 1px solid #1e1e1e; letter-spacing: .5px; }
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding-top: 0.5rem !important; padding-bottom: 1rem !important; max-width: 1200px !important; }
.streamlit-expanderHeader { background: #111111 !important; border: 1px solid #2a2a2a !important; color: #888 !important; }
[data-testid="stDataFrame"] { border: 1px solid #2a2a2a !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <span class="hero-emblem">⚖</span>
  <h1>NYAYA-SAHAYAK</h1>
  <div class="tagline">MikeRoss in the form of a Chatbot for Indian Legal System</div>
  <div class="hero-rule"></div>
  <div class="subtitle">
    <span class="pill">BNS 2023</span>
    <span class="pill">IPC migration infrastructure</span>
    <span class="pill">3400+ Schemes</span>
    <span class="pill">FIR Generator</span>
    <span class="pill">Bail Checker</span>
    <span class="pill">22+ Languages supported </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stats Row ────────────────────────────────────────────────────────────────────
col_lang, col_stat1, col_stat2, col_stat3, col_stat4 = st.columns([2,1,1,1,1])
with col_lang:
    st.markdown("""
    <div class="lang-card">
        <span class="lang-icon">&#127760;</span>
        <div>
            <strong>Multilingual</strong><br>
            <span style="font-size:.8rem; color:#4a4a6a;">Type in any Indian language</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    lang_code = "auto"
with col_stat1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon amber">&#128483;</div>
        <div class="stat-body">
            <span class="stat-value">22+</span>
            <span class="stat-label">Languages</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_stat2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon violet">&#128220;</div>
        <div class="stat-body">
            <span class="stat-value">358</span>
            <span class="stat-label">BNS Sections</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_stat3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon green">&#8646;</div>
        <div class="stat-body">
            <span class="stat-value">300+</span>
            <span class="stat-label">IPC&rarr;BNS Maps</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_stat4:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon blue">&#127963;</div>
        <div class="stat-body">
            <span class="stat-value">3400+</span>
            <span class="stat-label">Gov Schemes</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Lazy-load heavy modules ─────────────────────────────────────────────────────
@st.cache_resource(show_spinner="⚙️ Initializing Nyaya-Sahayak engine…")
def load_engine():
    from core.legal_retriever import get_engine
    return get_engine()

@st.cache_resource(show_spinner="Loading comparison engine…")
def load_comparator():
    from core.law_diff import get_comparator
    return get_comparator()

@st.cache_resource(show_spinner="Loading cache…")
def load_cache():
    from core.query_memory import QueryCache
    return QueryCache()

@st.cache_resource(show_spinner="Loading scheme database…")
def load_checker():
    from core.welfare_matcher import get_checker
    return get_checker()

# ── Tabs ─────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "§  Counsel",
    "↔  Law Changes",
    "⊕  Section Lookup",
    "◈  Schemes",
    "✦  FIR Draft",
    "⊜  Bail Check",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LEGAL CHATBOT
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="card">
      <h4>§ Legal Counsel</h4>
      <p>Ask any question about BNS 2023 or IPC. Choose your preferred response language below.</p>
    </div>
    """, unsafe_allow_html=True)

    if "chat_lang" not in st.session_state:
        st.session_state.chat_lang = None

    if st.session_state.chat_lang is None:
        st.markdown("#### Select response language")
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            if st.button("🇬🇧  English", use_container_width=True):
                st.session_state.chat_lang = "en"
                st.rerun()
        with lc2:
            if st.button("🇮🇳  हिंदी", use_container_width=True):
                st.session_state.chat_lang = "hi"
                st.rerun()
        with lc3:
            if st.button("🌐  Auto-detect", use_container_width=True):
                st.session_state.chat_lang = "auto"
                st.rerun()

    if st.session_state.chat_lang is not None:
        # Show selected language + option to change
        lang_label = {"en": "English", "hi": "हिंदी", "auto": "Auto-detect"}[st.session_state.chat_lang]
        col_lbl, col_chg = st.columns([5, 1])
        with col_lbl:
            st.markdown(f'<div style="color:#d4af37; font-size:.78rem; letter-spacing:1px; text-transform:uppercase; padding:.3rem 0;">Response language: {lang_label}</div>', unsafe_allow_html=True)
        with col_chg:
            if st.button("Change", key="change_lang"):
                st.session_state.chat_lang = None
                st.session_state.chat_history = []
                st.session_state.chat_summary = ""
                st.session_state.recent_turns = []
                st.session_state.turn_count = 0
                st.rerun()

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "chat_summary" not in st.session_state:
            st.session_state.chat_summary = ""
        if "recent_turns" not in st.session_state:
            st.session_state.recent_turns = []
        if "turn_count" not in st.session_state:
            st.session_state.turn_count = 0

        # Display history as a single self-contained HTML component
        if st.session_state.chat_history:
            msgs_html = ""
            for role, msg in st.session_state.chat_history:
                if role == "user":
                    msgs_html += f"""<div class="bubble user-bubble"><span class="bubble-label">You</span><div class="bubble-text">{msg}</div></div>"""
                else:
                    msgs_html += f"""<div class="bubble bot-bubble"><span class="bubble-label">&#9878; Nyaya-Sahayak</span><div class="bubble-text">{msg}</div></div>"""

            st.components.v1.html(f"""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ background: #0a0a0a; font-family: 'Inter', sans-serif; padding: 12px; }}
            .bubble {{ margin-bottom: 16px; max-width: 85%; }}
            .bubble-label {{ display: block; font-size: 10px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 6px; }}
            .bubble-text {{ padding: 14px 18px; line-height: 1.7; font-size: 14px; white-space: pre-wrap; }}
            .user-bubble {{ margin-left: auto; text-align: right; }}
            .user-bubble .bubble-label {{ color: #d4af37; }}
            .user-bubble .bubble-text {{ background: #111111; border: 1px solid #2a2a2a; border-right: 3px solid #d4af37; color: #e8e0d0; }}
            .bot-bubble {{ margin-right: auto; }}
            .bot-bubble .bubble-label {{ color: #888; font-family: 'Cormorant Garamond', serif; font-size: 12px; letter-spacing: 0.5px; text-transform: none; font-weight: 600; }}
            .bot-bubble .bubble-text {{ background: #111111; border: 1px solid #2a2a2a; border-left: 3px solid #444; color: #ccc; font-size: 14px; }}
            .bot-bubble .bubble-text strong {{ color: #d4af37; }}
            </style>
            </head>
            <body>{msgs_html}</body>
            </html>
            """, height=min(400 + len(st.session_state.chat_history) * 80, 800), scrolling=True)

        # Input
        with st.form("chat_form", clear_on_submit=True):
            c1, c2 = st.columns([5,1])
            with c1:
                user_q = st.text_input(
                    "Ask a question…",
                    placeholder="e.g. What is the punishment for rape under BNS? / हत्या के लिए सजा क्या है?",
                    label_visibility="collapsed",
                )
            with c2:
                submitted = st.form_submit_button("Send ➤", use_container_width=True)

        if submitted and user_q.strip():
            st.session_state.chat_history.append(("user", user_q))

            with st.spinner("Thinking…"):
                try:
                    engine = load_engine()
                    cache  = load_cache()

                    # Check cache only for fresh queries (no conversation context yet)
                    answer = None
                    is_fresh = not st.session_state.chat_summary and not st.session_state.recent_turns
                    if is_fresh:
                        answer = cache.check(user_q)

                    if answer is None:
                        answer = engine.agentic_query(
                            user_q,
                            language=st.session_state.get("chat_lang", "auto"),
                            top_k=3,
                            chat_summary=st.session_state.chat_summary,
                            recent_turns=st.session_state.recent_turns,
                        )
                        if is_fresh:
                            cache.store(user_q, answer)

                except Exception as e:
                    answer = f"⚠️ Error: {e}\n\nPlease check your API token and network connection."

            # Update memory
            st.session_state.recent_turns.append(("user", user_q))
            st.session_state.recent_turns.append(("assistant", answer))
            st.session_state.turn_count += 1

            # Compress every 4 turns
            if st.session_state.turn_count % 4 == 0:
                from core.sarvam_engine import summarize_conversation
                st.session_state.chat_summary = summarize_conversation(
                    st.session_state.chat_summary,
                    st.session_state.recent_turns,
                )
                st.session_state.recent_turns = st.session_state.recent_turns[-4:]

            st.session_state.chat_history.append(("bot", answer))
            st.rerun()

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.chat_summary = ""
            st.session_state.recent_turns = []
            st.session_state.turn_count = 0
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — IPC vs BNS COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="card">
      <h4>⊜ Case Study Analyser — IPC vs BNS</h4>
      <p>Describe a legal scenario or pick a case study. Get a visual migration diagram with side-by-side analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    scenario = st.text_area(
        "Describe the scenario",
        placeholder="e.g. A person threatens someone with a knife to take their money…",
        height=90,
        label_visibility="collapsed",
    )

    QUICK = ["Murder / हत्या", "Theft / चोरी", "Rape / बलात्कार",
             "Cheating / धोखाधड़ी", "Acid attack / एसिड हमला", "Stalking / पीछा करना"]
    q_pick = st.selectbox("Or pick a quick scenario:", ["—"] + QUICK, label_visibility="collapsed")
    if q_pick != "—":
        scenario = q_pick.split(" / ")[0]

    if st.button("⊜ Analyse Case Study", key="cmp_btn"):
        if not scenario.strip():
            st.warning("Please enter a scenario.")
        else:
            with st.spinner("Querying BNS & IPC indices…"):
                try:
                    comp = load_comparator()
                    result = comp.compare_scenario(scenario, language="auto")
                except Exception as e:
                    st.error(f"Error: {e}")
                    result = None

            if result:
                bns_r = result["bns_results"]
                ipc_r = result["ipc_results"]

                # ── Migration Flow Diagram (SVG) ──────────────────────────────────
                # Build IPC and BNS node lists
                def _section_num(r):
                    title = str(r.get("title",""))
                    import re as _re
                    m = _re.search(r"(\d{1,3}[A-Z]?)", title)
                    return m.group(1) if m else "?"

                def _short_name(r):
                    title = str(r.get("title",""))
                    parts = title.split("—") if "—" in title else title.split("-")
                    return (parts[-1] if len(parts) > 1 else title).strip()[:35]

                ipc_nodes = [(_section_num(r), _short_name(r)) for r in (ipc_r or [])][:3]
                bns_nodes = [(_section_num(r), _short_name(r)) for r in (bns_r or [])][:3]

                # Pad with placeholders if empty
                while len(ipc_nodes) < 3: ipc_nodes.append(("—", "—"))
                while len(bns_nodes) < 3: bns_nodes.append(("—", "—"))

                # Build SVG nodes and connections
                svg_height = 320
                left_x  = 90
                right_x = 540
                node_w  = 170
                node_h  = 60
                gap     = 30
                start_y = 30

                ipc_svg = ""
                bns_svg = ""
                lines_svg = ""

                for i, (sec, name) in enumerate(ipc_nodes):
                    y = start_y + i * (node_h + gap)
                    ipc_svg += f"""
                    <rect x="{left_x}" y="{y}" width="{node_w}" height="{node_h}" rx="2"
                          fill="rgba(136,136,136,0.06)" stroke="#555" stroke-width="1"/>
                    <text x="{left_x + 12}" y="{y + 22}" fill="#888" font-size="10"
                          font-weight="700" letter-spacing="1px" font-family="Inter, sans-serif">IPC § {sec}</text>
                    <text x="{left_x + 12}" y="{y + 44}" fill="#bbb" font-size="11"
                          font-family="Inter, sans-serif">{name}</text>
                    """

                for i, (sec, name) in enumerate(bns_nodes):
                    y = start_y + i * (node_h + gap)
                    bns_svg += f"""
                    <rect x="{right_x}" y="{y}" width="{node_w}" height="{node_h}" rx="2"
                          fill="rgba(212,175,55,0.08)" stroke="#d4af37" stroke-width="1.5"/>
                    <text x="{right_x + 12}" y="{y + 22}" fill="#d4af37" font-size="10"
                          font-weight="700" letter-spacing="1px" font-family="Inter, sans-serif">BNS § {sec}</text>
                    <text x="{right_x + 12}" y="{y + 44}" fill="#e8e0d0" font-size="11"
                          font-family="Inter, sans-serif">{name}</text>
                    """

                # Draw connecting curves (each IPC connects to corresponding BNS)
                for i in range(min(len(ipc_nodes), len(bns_nodes))):
                    y_left  = start_y + i * (node_h + gap) + node_h // 2
                    y_right = start_y + i * (node_h + gap) + node_h // 2
                    mid_x   = (left_x + node_w + right_x) // 2
                    lines_svg += f"""
                    <path d="M {left_x + node_w} {y_left} C {mid_x} {y_left}, {mid_x} {y_right}, {right_x} {y_right}"
                          stroke="#d4af37" stroke-width="1.2" fill="none" opacity="0.5"
                          stroke-dasharray="4,4">
                      <animate attributeName="stroke-dashoffset" from="0" to="-16"
                               dur="1.2s" repeatCount="indefinite"/>
                    </path>
                    <circle r="3" fill="#d4af37">
                      <animateMotion dur="2s" repeatCount="indefinite"
                                     path="M {left_x + node_w} {y_left} C {mid_x} {y_left}, {mid_x} {y_right}, {right_x} {y_right}"/>
                    </circle>
                    """

                # Section text content for cards below diagram
                bns_cards_html = ""
                for r in (bns_r or [])[:3]:
                    bns_cards_html += f"""
                    <div class="sec-card bns">
                      <div class="sec-tag bns-tag">BNS · NEW LAW</div>
                      <div class="sec-title">{r.get('title','BNS Section')}</div>
                      <div class="sec-text">{r.get('text','')[:400]}{'…' if len(r.get('text','')) > 400 else ''}</div>
                    </div>"""

                ipc_cards_html = ""
                for r in (ipc_r or [])[:3]:
                    ipc_cards_html += f"""
                    <div class="sec-card ipc">
                      <div class="sec-tag ipc-tag">IPC · OLD LAW</div>
                      <div class="sec-title">{r.get('title','IPC Section')}</div>
                      <div class="sec-text">{r.get('text','')[:400]}{'…' if len(r.get('text','')) > 400 else ''}</div>
                    </div>"""

                # Stat counts
                bns_count = len([r for r in (bns_r or []) if r])
                ipc_count = len([r for r in (ipc_r or []) if r])
                shared_count = min(bns_count, ipc_count)

                st.components.v1.html(f"""<!DOCTYPE html><html><head>
                <style>
                @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');
                *{{box-sizing:border-box;margin:0;padding:0;}}
                body{{background:#0a0a0a;font-family:'Inter',sans-serif;padding:8px;color:#e8e0d0;}}

                .scenario-banner {{
                    background: linear-gradient(180deg, #111 0%, #0a0a0a 100%);
                    border: 1px solid #2a2a2a; border-left: 3px solid #d4af37;
                    padding: 14px 20px; margin-bottom: 18px;
                }}
                .scenario-banner .label {{
                    font-size: 10px; color:#888; letter-spacing: 2px;
                    text-transform: uppercase; font-weight: 700; margin-bottom: 4px;
                }}
                .scenario-banner .text {{ color:#e8e0d0; font-size: 14px; }}

                .stats-row {{
                    display: grid; grid-template-columns: repeat(3, 1fr);
                    gap: 10px; margin-bottom: 18px;
                }}
                .stat {{
                    background: #111; border: 1px solid #2a2a2a; padding: 12px 14px;
                    text-align: center;
                }}
                .stat .num {{
                    font-family:'Cormorant Garamond',serif; font-size: 1.8rem;
                    font-weight: 700; color: #d4af37; line-height: 1;
                }}
                .stat .lab {{
                    font-size: 9px; color: #666; text-transform: uppercase;
                    letter-spacing: 1.2px; font-weight: 600; margin-top: 4px;
                }}

                .diagram-box {{
                    background: #0d0d0d; border: 1px solid #2a2a2a;
                    padding: 20px; margin-bottom: 18px;
                }}
                .diagram-title {{
                    text-align: center; color: #d4af37;
                    font-family: 'Cormorant Garamond', serif;
                    font-size: 18px; font-weight: 700;
                    letter-spacing: 1px; margin-bottom: 12px;
                }}
                .diagram-sub {{
                    text-align: center; color: #555; font-size: 10px;
                    text-transform: uppercase; letter-spacing: 2px;
                    margin-bottom: 18px;
                }}
                .header-labels {{
                    display: flex; justify-content: space-around;
                    color: #888; font-size: 10px; font-weight: 700;
                    text-transform: uppercase; letter-spacing: 1.5px;
                    margin-bottom: 8px;
                }}
                .header-labels .ipc-h {{ color: #888; }}
                .header-labels .bns-h {{ color: #d4af37; }}

                .cards-grid {{
                    display: grid; grid-template-columns: 1fr 1fr;
                    gap: 14px; margin-top: 8px;
                }}
                .sec-card {{
                    background: #111; border: 1px solid #2a2a2a; padding: 14px 16px;
                }}
                .sec-card.ipc {{ border-left: 3px solid #555; }}
                .sec-card.bns {{ border-left: 3px solid #d4af37; }}
                .sec-tag {{
                    display: inline-block; font-size: 9px; font-weight: 700;
                    text-transform: uppercase; letter-spacing: 1.5px;
                    padding: 2px 8px; margin-bottom: 8px;
                }}
                .sec-tag.ipc-tag {{ background: rgba(136,136,136,0.08); color: #888; border: 1px solid #333; }}
                .sec-tag.bns-tag {{ background: rgba(212,175,55,0.1); color: #d4af37; border: 1px solid rgba(212,175,55,0.3); }}
                .sec-title {{
                    font-family: 'Cormorant Garamond', serif;
                    font-size: 14px; color: #e8e0d0; font-weight: 700;
                    margin-bottom: 6px;
                }}
                .sec-text {{ font-size: 12px; color: #999; line-height: 1.6; }}

                .col-header {{
                    font-family: 'Cormorant Garamond', serif;
                    text-align: center; padding: 8px 0; margin-bottom: 4px;
                    font-size: 14px; font-weight: 700; letter-spacing: 2px;
                    text-transform: uppercase;
                }}
                .col-header.ipc {{ color: #888; border-bottom: 1px solid #333; }}
                .col-header.bns {{ color: #d4af37; border-bottom: 1px solid rgba(212,175,55,0.3); }}
                </style></head><body>

                <div class="scenario-banner">
                    <div class="label">⊜ Case Scenario</div>
                    <div class="text">{scenario}</div>
                </div>

                <div class="stats-row">
                    <div class="stat"><div class="num">{ipc_count}</div><div class="lab">IPC Sections</div></div>
                    <div class="stat"><div class="num">{shared_count}</div><div class="lab">Mappings Found</div></div>
                    <div class="stat"><div class="num">{bns_count}</div><div class="lab">BNS Sections</div></div>
                </div>

                <div class="diagram-box">
                    <div class="diagram-title">⟿  Migration Diagram  ⟿</div>
                    <div class="diagram-sub">Old Law &nbsp;→&nbsp; New Law</div>

                    <div class="header-labels">
                        <span class="ipc-h">IPC 1860 (OLD)</span>
                        <span class="bns-h">BNS 2023 (NEW)</span>
                    </div>

                    <svg width="100%" height="{svg_height}" viewBox="0 0 800 {svg_height}"
                         preserveAspectRatio="xMidYMid meet">
                        {lines_svg}
                        {ipc_svg}
                        {bns_svg}
                    </svg>
                </div>

                <div class="cards-grid">
                    <div>
                        <div class="col-header ipc">IPC · Old Provisions</div>
                        {ipc_cards_html or '<div class="sec-card ipc"><div class="sec-text">No IPC sections retrieved.</div></div>'}
                    </div>
                    <div>
                        <div class="col-header bns">BNS · New Provisions</div>
                        {bns_cards_html or '<div class="sec-card bns"><div class="sec-text">No BNS sections retrieved.</div></div>'}
                    </div>
                </div>

                </body></html>""", height=svg_height + 700, scrolling=True)

                st.markdown("---")
                st.markdown("### Legal Analysis")
                st.markdown(f'<div class="msg-bot">{result["llm_analysis"]}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SECTION TRANSLATOR
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="card">
      <h4>🔄 IPC → BNS Section Translator</h4>
      <p>Enter an old IPC section number and instantly find its BNS equivalent.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        ipc_input = st.text_input("Enter IPC Section Number", placeholder="e.g. 302, 420, 376D, 498A")
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        translate_btn = st.button("🔄 Translate", key="trans_btn", use_container_width=True)

    # Migration Infra — paginated mapping browser
    st.markdown("#### Migration Infra for Common IPC Sections")
    try:
        comp = load_comparator()
        df = comp.get_full_mapping_df()
        df_display = df[df["bns_section"] != "NEW"].reset_index(drop=True)

        if "mig_page" not in st.session_state:
            st.session_state.mig_page = 0

        PER_PAGE = 20
        total_rows = len(df_display)
        total_pages = max(1, (total_rows + PER_PAGE - 1) // PER_PAGE)

        # Clamp page
        st.session_state.mig_page = max(0, min(st.session_state.mig_page, total_pages - 1))

        start = st.session_state.mig_page * PER_PAGE
        end   = min(start + PER_PAGE, total_rows)
        page_df = df_display.iloc[start:end]

        # Build HTML rows
        rows_html = ""
        for _, row in page_df.iterrows():
            ipc_s   = str(row.get("ipc_section",""))
            ipc_n   = str(row.get("ipc_name","")).strip()
            bns_s   = str(row.get("bns_section",""))
            bns_n   = str(row.get("bns_name","")).strip()
            note    = str(row.get("note","")).strip()
            note    = "" if note in ("nan","None") else note
            rows_html += f"""
            <div class="mig-row">
              <div class="mig-side ipc">
                <div class="mig-tag">IPC § {ipc_s}</div>
                <div class="mig-name">{ipc_n}</div>
              </div>
              <div class="mig-arrow">→</div>
              <div class="mig-side bns">
                <div class="mig-tag bns-tag">BNS § {bns_s}</div>
                <div class="mig-name">{bns_n}</div>
              </div>
              {f'<div class="mig-note">📝 {note}</div>' if note else ''}
            </div>
            """

        st.components.v1.html(f"""<!DOCTYPE html><html><head>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;500;600&display=swap');
        *{{box-sizing:border-box;margin:0;padding:0;}}
        body{{background:#0a0a0a;font-family:'Inter',sans-serif;padding:8px;}}
        .mig-box{{background:#111111;border:1px solid #2a2a2a;border-left:3px solid #ec4899;padding:18px 22px;}}
        .mig-row{{display:grid;grid-template-columns:1fr auto 1fr;gap:14px;padding:12px 0;border-bottom:1px solid #1a1a1a;align-items:center;}}
        .mig-row:last-child{{border-bottom:none;}}
        .mig-side{{padding:6px 10px;}}
        .mig-tag{{display:inline-block;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;padding:2px 8px;border:1px solid rgba(236,72,153,0.3);background:rgba(236,72,153,0.07);color:#ec4899;margin-bottom:4px;}}
        .mig-tag.bns-tag{{border-color:rgba(236,72,153,0.5);background:rgba(236,72,153,0.12);color:#f9a8d4;}}
        .mig-name{{font-size:13px;color:#e8e0d0;line-height:1.5;}}
        .mig-arrow{{color:#ec4899;font-size:20px;font-weight:700;text-align:center;}}
        .mig-note{{grid-column:1/-1;font-size:11.5px;color:#888;font-style:italic;padding:4px 10px 0;}}
        </style></head><body>
        <div class="mig-box">{rows_html}</div>
        </body></html>""", height=int(min(700, 80 + len(page_df) * 75)), scrolling=True)

        # Pagination controls
        pc1, pc2, pc3 = st.columns([1, 3, 1])
        with pc1:
            if st.button("← Previous", key="mig_prev", disabled=st.session_state.mig_page == 0, use_container_width=True):
                st.session_state.mig_page -= 1
                st.rerun()
        with pc2:
            st.markdown(
                f'<div style="text-align:center; color:#ec4899; font-size:.82rem; letter-spacing:1.5px; '
                f'text-transform:uppercase; padding:.55rem 0; font-weight:600;">'
                f'Page {st.session_state.mig_page + 1} of {total_pages} &nbsp;·&nbsp; '
                f'<span style="color:#666;">Showing {start+1}–{end} of {total_rows} mappings</span></div>',
                unsafe_allow_html=True
            )
        with pc3:
            if st.button("Next →", key="mig_next", disabled=st.session_state.mig_page >= total_pages - 1, use_container_width=True):
                st.session_state.mig_page += 1
                st.rerun()

    except Exception as e:
        st.warning(f"Could not load mapping table: {e}")

    if translate_btn and ipc_input.strip():
        with st.spinner(f"Looking up IPC {ipc_input}…"):
            try:
                comp = load_comparator()
                result = comp.translate_ipc_to_bns(ipc_input.strip())
            except Exception as e:
                result = {"found": False, "note": str(e)}

        if result.get("found"):
            bns_sec = result["bns_section"]
            is_repealed = bns_sec in ("REPEALED",)
            color = "#f87171" if is_repealed else "#4ade80"
            st.markdown(f"""
            <div class="card" style="border-color: {color}40;">
              <div style="display:flex; gap:1rem; align-items:flex-start;">
                <div style="flex:1;">
                  <span class="tag-ipc">IPC § {result['ipc_section']}</span>
                  <h4 style="margin-top:.5rem;">{result['ipc_name']}</h4>
                </div>
                <div style="font-size:1.5rem; color:#64748b;">→</div>
                <div style="flex:1;">
                  <span class="{'tag-bns' if not is_repealed else 'tag-ipc'}">BNS § {bns_sec}</span>
                  <h4 style="margin-top:.5rem;">{result['bns_name']}</h4>
                </div>
              </div>
              {("<p style='color:#94a3b8; margin-top:.7rem;'>📝 " + str(result['note']) + "</p>") if str(result.get('note','') or '').strip() not in ('', 'nan') else ""}
            </div>
            """, unsafe_allow_html=True)

            if result.get("bns_text"):
                with st.expander(f"📄 Full text of BNS § {bns_sec}"):
                    st.write(result["bns_text"])

            # LLM explanation
            if not is_repealed:
                with st.spinner("Getting AI explanation…"):
                    from core.sarvam_engine import chat as llm_chat
                    explanation = llm_chat([
                        {"role": "user", "content":
                         f"Explain the change from IPC {result['ipc_section']} ({result['ipc_name']}) "
                         f"to BNS {bns_sec} ({result['bns_name']}). What are the key differences?"}
                    ], language="auto", max_tokens=500)
                st.markdown(f'<div class="msg-bot">⚖️ {explanation}</div>', unsafe_allow_html=True)
        else:
            st.warning(f"IPC Section {ipc_input} not found in mapping table. Try the chatbot for manual lookup.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — SCHEME ELIGIBILITY CHECKER
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div class="card">
      <h4>◈ Scheme Advisor</h4>
      <p>Answer a few questions and discover which of 3400+ government schemes you qualify for.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Scheme chat state ─────────────────────────────────────────────────────────
    SCHEME_QUESTIONS = [
        ("age",               "What is your age?"),
        ("gender",            "What is your gender? (Male / Female / Other)"),
        ("annual_income_lpa", "What is your approximate annual household income in lakhs? (e.g. type 1.5 for ₹1.5 lakh/year, or 0 if no income)"),
        ("caste",             "What is your caste category? (General / OBC / SC / ST)"),
        ("location",          "Do you live in an Urban or Rural area?"),
        ("occupation",        "What is your occupation?\n(Farmer / Student / Salaried / Self-employed / Unemployed / Business)"),
        ("flags",             "Last step! Do any of these apply to you? Type the numbers separated by commas (or type 'none'):\n\n1. BPL card holder\n2. Differently-abled\n3. Survived domestic/sexual violence\n4. Need free legal aid\n5. Have agricultural land\n6. Have a girl child under 10 years\n7. No LPG gas connection at home\n8. Running or planning a small business"),
    ]

    def _parse_scheme_answer(field, answer):
        a = answer.strip().lower()
        if field == "age":
            nums = [int(x) for x in answer.split() if x.isdigit()]
            return nums[0] if nums else 25
        if field == "annual_income_lpa":
            import re as _re
            nums = _re.findall(r"[\d.]+", answer)
            return float(nums[0]) if nums else 2.0
        if field == "gender":
            if any(w in a for w in ["female","woman","lady","girl","f"]): return "female"
            if any(w in a for w in ["male","man","boy","m"]): return "male"
            return "other"
        if field == "caste":
            if "sc" in a or "scheduled caste" in a or "dalit" in a: return "sc"
            if "st" in a or "scheduled tribe" in a or "tribal" in a or "adivasi" in a: return "st"
            if "obc" in a or "backward" in a: return "obc"
            return "general"
        if field == "location":
            return "rural" if "rural" in a or "village" in a or "gram" in a else "urban"
        if field == "occupation":
            for occ in ["farmer","student","salaried","self-employed","unemployed","business"]:
                if occ in a: return occ
            return "unemployed"
        if field == "flags":
            if "none" in a: return []
            import re as _re
            return [int(x) for x in _re.findall(r"\d", answer)]
        return answer

    def _flags_to_profile_bools(flags):
        nums = flags if isinstance(flags, list) else []
        return {
            "is_bpl":               1 in nums,
            "has_disability":       2 in nums,
            "is_violence_survivor": 3 in nums,
            "needs_legal_aid":      4 in nums,
            "has_agricultural_land":5 in nums,
            "has_girl_child":       6 in nums,
            "no_lpg":               7 in nums,
            "is_entrepreneur":      8 in nums,
        }

    if "sc_history" not in st.session_state:
        st.session_state.sc_history = []           # [(role, msg)]
    if "sc_q_idx" not in st.session_state:
        st.session_state.sc_q_idx = 0              # current question index
    if "sc_answers" not in st.session_state:
        st.session_state.sc_answers = {}           # field → parsed value
    if "sc_done" not in st.session_state:
        st.session_state.sc_done = False
    if "sc_result" not in st.session_state:
        st.session_state.sc_result = None
    if "scheme_profile" not in st.session_state:
        st.session_state.scheme_profile = None
    if "scheme_matched" not in st.session_state:
        st.session_state.scheme_matched = []

    # Seed first question
    if not st.session_state.sc_history and not st.session_state.sc_done:
        first_q = SCHEME_QUESTIONS[0][1]
        st.session_state.sc_history.append(("bot", f"Hello! I'll help you find government schemes you qualify for. Let's start.\n\n{first_q}"))

    # Display chat history
    if st.session_state.sc_history:
        msgs_html = ""
        for role, msg in st.session_state.sc_history:
            msg_escaped = msg.replace("\n", "<br>")
            if role == "user":
                msgs_html += f'<div class="bubble user-bubble"><span class="bubble-label">You</span><div class="bubble-text">{msg_escaped}</div></div>'
            else:
                msgs_html += f'<div class="bubble bot-bubble"><span class="bubble-label">◈ Scheme Advisor</span><div class="bubble-text">{msg_escaped}</div></div>'
        st.components.v1.html(f"""<!DOCTYPE html><html><head>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600&family=Inter:wght@400;500;600&display=swap');
        * {{ box-sizing:border-box; margin:0; padding:0; }}
        body {{ background:#0a0a0a; font-family:'Inter',sans-serif; padding:12px; }}
        .bubble {{ margin-bottom:14px; max-width:88%; }}
        .bubble-label {{ display:block; font-size:10px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:5px; }}
        .bubble-text {{ padding:13px 16px; line-height:1.75; font-size:13.5px; }}
        .user-bubble {{ margin-left:auto; text-align:right; }}
        .user-bubble .bubble-label {{ color:#d4af37; }}
        .user-bubble .bubble-text {{ background:#111111; border:1px solid #2a2a2a; border-right:3px solid #d4af37; color:#e8e0d0; }}
        .bot-bubble {{ margin-right:auto; }}
        .bot-bubble .bubble-label {{ color:#888; font-family:'Cormorant Garamond',serif; font-size:11px; letter-spacing:.5px; text-transform:none; font-weight:600; }}
        .bot-bubble .bubble-text {{ background:#111111; border:1px solid #2a2a2a; border-left:3px solid #444; color:#ccc; }}
        .bot-bubble .bubble-text strong {{ color:#d4af37; }}
        </style></head>
        <body>{msgs_html}</body></html>""",
        height=min(120 + len(st.session_state.sc_history) * 90, 500), scrolling=True)

    # Input area — only show if not done
    if not st.session_state.sc_done:
        with st.form("scheme_chat_form", clear_on_submit=True):
            sc_input = st.text_input("Your answer…", label_visibility="collapsed",
                                     placeholder="Type your answer and press Enter")
            sc_send = st.form_submit_button("Reply ➤", use_container_width=True)

        if sc_send and sc_input.strip():
            field, _ = SCHEME_QUESTIONS[st.session_state.sc_q_idx]
            parsed = _parse_scheme_answer(field, sc_input)
            st.session_state.sc_answers[field] = parsed
            st.session_state.sc_history.append(("user", sc_input))
            st.session_state.sc_q_idx += 1

            if st.session_state.sc_q_idx < len(SCHEME_QUESTIONS):
                next_q = SCHEME_QUESTIONS[st.session_state.sc_q_idx][1]
                st.session_state.sc_history.append(("bot", next_q))
            else:
                st.session_state.sc_done = True
                st.session_state.sc_history.append(("bot", "Thanks! Finding your matching schemes now..."))
            st.rerun()

    # Run scheme search once all answers collected
    if st.session_state.sc_done and st.session_state.sc_result is None:
        ans = st.session_state.sc_answers
        flags = ans.get("flags", [])
        profile = {
            "age":                  ans.get("age", 25),
            "gender":               ans.get("gender", "male"),
            "annual_income_lpa":    ans.get("annual_income_lpa", 2.0),
            "caste":                ans.get("caste", "general"),
            "location":             ans.get("location", "urban"),
            "occupation":           ans.get("occupation", "unemployed"),
            **_flags_to_profile_bools(flags),
        }
        with st.spinner("Searching 3400+ schemes…"):
            try:
                checker = load_checker()
                result = checker.check_eligibility(profile, language="auto")
                st.session_state.sc_result = result
                st.session_state.scheme_profile = profile
                st.session_state.scheme_matched = result.get("matched_schemes", [])
            except Exception as e:
                st.error(f"Error: {e}")

    # Show results
    if st.session_state.sc_result:
        result = st.session_state.sc_result
        matched = result["matched_schemes"]
        st.success(f"Found **{result['total_matched']}** matching schemes. Showing top {len(matched)}.")

        cards_html = ""
        for scheme in matched:
            cat   = scheme.get("category", "")
            benefit = scheme.get("benefit", "")
            url   = scheme.get("url", "")
            score = scheme.get("_score", 0)
            level = scheme.get("level", "")
            description = scheme.get("description", "")
            level_color = "#d4af37" if level == "Central" else "#888"
            link_html = f'<a class="card-link" href="{url}" target="_blank">Apply &#8599;</a>' if url else ""
            cards_html += f"""
            <div class="card">
              <div class="card-header">
                <div class="card-title">{scheme['name']}</div>
                <div class="card-score">{score} pts</div>
              </div>
              <div class="card-meta">
                <span class="badge" style="color:#d4af37;background:rgba(212,175,55,0.07);border-color:rgba(212,175,55,0.2);">{cat}</span>
                <span class="badge" style="color:{level_color};background:rgba(255,255,255,0.03);border-color:#2a2a2a;">{level}</span>
              </div>
              <div class="card-benefit">&#128184; {benefit[:200]}</div>
              <div class="card-eligibility">{description[:150]}{'&hellip;' if len(description)>150 else ''}</div>
              {link_html}
            </div>"""

        st.components.v1.html(f"""<!DOCTYPE html><html><head>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;500;600&display=swap');
        *{{box-sizing:border-box;margin:0;padding:0;}}
        body{{background:#0a0a0a;font-family:'Inter',sans-serif;padding:8px;}}
        .card{{background:#111111;border:1px solid #2a2a2a;border-left:4px solid #d4af37;padding:18px 22px;margin-bottom:10px;}}
        .card-header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;}}
        .card-title{{font-family:'Cormorant Garamond',serif;font-size:16px;color:#e8e0d0;font-weight:700;flex:1;padding-right:12px;}}
        .card-score{{font-size:11px;color:#d4af37;font-weight:700;background:rgba(212,175,55,0.07);padding:3px 10px;border:1px solid rgba(212,175,55,0.2);white-space:nowrap;}}
        .card-meta{{display:flex;gap:8px;margin-bottom:8px;flex-wrap:wrap;}}
        .badge{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;padding:3px 10px;border:1px solid;}}
        .card-benefit{{font-size:13px;color:#ccc;margin-bottom:6px;line-height:1.6;}}
        .card-eligibility{{font-size:12px;color:#666;line-height:1.5;margin-bottom:8px;}}
        .card-link{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:#d4af37;text-decoration:none;border-bottom:1px solid #d4af37;padding-bottom:1px;}}
        </style></head><body>{cards_html}</body></html>""",
        height=int(len(matched) * 200), scrolling=True)

        st.markdown("---")
        st.markdown(f'<div class="msg-bot">{result["explanation"]}</div>', unsafe_allow_html=True)

        # Follow-up Q&A
        st.markdown("---")
        with st.form("scheme_followup_form", clear_on_submit=True):
            followup_q = st.text_input("Ask a follow-up about your schemes…", label_visibility="collapsed",
                                       placeholder="e.g. How do I apply for PM Kisan?")
            followup_submit = st.form_submit_button("Ask ➤", use_container_width=True)

        if followup_submit and followup_q.strip():
            with st.spinner("Thinking…"):
                try:
                    from core.sarvam_engine import chat as llm_chat, ANSWER_SYSTEM_PROMPT_EN
                    profile_text = "\n".join(f"- {k}: {v}" for k, v in st.session_state.scheme_profile.items())
                    schemes_text = "\n".join(f"- {s['name']}: {s.get('benefit','')}" for s in st.session_state.scheme_matched)
                    followup_answer = llm_chat(
                        [{"role":"user","content":f"[USER PROFILE]\n{profile_text}\n\n[MATCHED SCHEMES]\n{schemes_text}\n\n---\n\nQuestion: {followup_q}"}],
                        language="auto", max_tokens=600, _system_override=ANSWER_SYSTEM_PROMPT_EN,
                    )
                except Exception as e:
                    followup_answer = f"⚠️ Error: {e}"
            st.markdown(f'<div class="msg-bot">{followup_answer}</div>', unsafe_allow_html=True)

        if st.button("Start Over", key="scheme_restart"):
            for k in ["sc_history","sc_q_idx","sc_answers","sc_done","sc_result","scheme_profile","scheme_matched"]:
                st.session_state.pop(k, None)
            st.rerun()

with tab5:
    st.markdown("""
    <div class="card">
      <h4>📋 FIR Draft Generator</h4>
      <p>Describe your incident and get a formal FIR draft with applicable BNS sections. Take this draft to your nearest police station.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("fir_form"):
        st.markdown("##### Complainant Details")
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            fir_name = st.text_input("Full Name *", placeholder="e.g. Ramesh Kumar Sharma")
        with fc2:
            fir_contact = st.text_input("Contact Number", placeholder="e.g. 9876543210")
        with fc3:
            fir_date = st.date_input("Date of Filing")

        fir_address = st.text_area("Address *", placeholder="House No., Street, City, State, PIN", height=68)

        st.markdown("##### Incident Details")
        fi1, fi2, fi3 = st.columns(3)
        with fi1:
            incident_date = st.date_input("Date of Incident")
        with fi2:
            incident_time = st.time_input("Time of Incident")
        with fi3:
            incident_place = st.text_input("Place of Incident *", placeholder="e.g. Near Bus Stand, Sector 4, Delhi")

        incident_desc = st.text_area(
            "Describe the Incident *",
            placeholder="Describe what happened in detail — who did what, how, in what sequence. The more detail, the better the FIR.",
            height=150,
        )

        st.markdown("##### Additional Details (Optional)")
        fa1, fa2 = st.columns(2)
        with fa1:
            accused_details = st.text_area("Accused Details", placeholder="Name, address, physical description if known", height=100)
        with fa2:
            witness_details = st.text_area("Witness Details", placeholder="Name and contact of any witnesses", height=100)

        fir_submit = st.form_submit_button("📋 Generate FIR Draft", use_container_width=True)

    if fir_submit:
        if not fir_name.strip() or not fir_address.strip() or not incident_place.strip() or not incident_desc.strip():
            st.warning("Please fill in all required fields marked with *")
        else:
            with st.spinner("Retrieving applicable BNS sections and drafting FIR…"):
                try:
                    from core.sarvam_engine import generate_fir
                    engine = load_engine()

                    # Retrieve top 5 BNS sections from incident description
                    bns_results = engine.query_bns(incident_desc, top_k=5)
                    bns_context = engine.format_context(bns_results)

                    fir_draft = generate_fir(
                        complainant_name=fir_name,
                        complainant_address=fir_address,
                        complainant_contact=fir_contact,
                        incident_date=str(incident_date),
                        incident_time=str(incident_time),
                        incident_place=incident_place,
                        incident_description=incident_desc,
                        accused_details=accused_details,
                        witness_details=witness_details,
                        bns_context=bns_context,
                    )
                except Exception as e:
                    fir_draft = f"⚠️ Error generating FIR: {e}"

            st.markdown("---")
            st.markdown("#### Generated FIR Draft")
            st.components.v1.html(f"""<!DOCTYPE html><html><head>
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;500;600&display=swap');
            *{{box-sizing:border-box;margin:0;padding:0;}}
            body{{background:#0a0a0a;font-family:'Inter',sans-serif;padding:12px;}}
            .fir-box{{background:#111111;border:1px solid #2a2a2a;border-left:3px solid #d4af37;padding:24px 28px;}}
            .fir-box pre{{
                white-space:pre-wrap; font-family:'Inter',sans-serif;
                font-size:13.5px; line-height:1.8; color:#ccc;
            }}
            .fir-box pre strong{{color:#d4af37;}}
            </style></head>
            <body><div class="fir-box"><pre>{fir_draft}</pre></div></body></html>""",
            height=720, scrolling=True)
            st.download_button(
                label="⬇️ Download FIR Draft (.txt)",
                data=fir_draft,
                file_name=f"FIR_Draft_{fir_name.replace(' ', '_')}_{incident_date}.txt",
                mime="text/plain",
            )
            st.warning("⚠️ This is an AI-generated draft for reference only. Review with a qualified advocate before submission.")

with tab6:
    st.markdown("""
    <div class="card">
      <h4>🔓 Bail or No Bail Checker</h4>
      <p>Enter a BNS section number or describe the offense to get an instant bail eligibility assessment under BNSS 2023.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("bail_form"):
        bc1, bc2 = st.columns([2, 1])
        with bc1:
            bail_offense = st.text_area(
                "Offense Description or BNS Section *",
                placeholder="e.g. BNS Section 103 (Murder) — or describe: 'accused of theft of mobile phone worth ₹15,000'",
                height=100,
            )
        with bc2:
            bail_section = st.text_input("BNS Section Number (optional)", placeholder="e.g. 103, 64, 318")

        st.markdown("##### Accused Circumstances (optional — helps refine assessment)")
        ba1, ba2, ba3 = st.columns(3)
        with ba1:
            bail_gender   = st.selectbox("Gender", ["Not specified", "Male", "Female", "Other"])
            bail_age      = st.number_input("Age", 0, 100, 0)
        with ba2:
            bail_first    = st.checkbox("First-time offender")
            bail_sick     = st.checkbox("Sick / Infirm")
        with ba3:
            bail_custody  = st.number_input("Days in custody", 0, 3650, 0)
            bail_lang     = st.selectbox("Response language", ["English", "Hindi"])

        bail_submit = st.form_submit_button("⚖️ Check Bail Eligibility", use_container_width=True)

    if bail_submit:
        if not bail_offense.strip():
            st.warning("Please describe the offense or enter a BNS section number.")
        else:
            with st.spinner("Analysing bail eligibility…"):
                try:
                    from core.sarvam_engine import check_bail_eligibility
                    engine = load_engine()

                    # Build search query
                    query = bail_section.strip() if bail_section.strip() else bail_offense
                    bns_results = engine.query_bns(query, top_k=3)
                    bns_context = engine.format_context(bns_results)

                    # Build accused details string
                    accused_parts = []
                    if bail_gender != "Not specified": accused_parts.append(f"Gender: {bail_gender}")
                    if bail_age > 0:                   accused_parts.append(f"Age: {bail_age}")
                    if bail_first:                     accused_parts.append("First-time offender")
                    if bail_sick:                      accused_parts.append("Sick / Infirm")
                    if bail_custody > 0:               accused_parts.append(f"Days in custody: {bail_custody}")
                    accused_details = ", ".join(accused_parts)

                    language = "hi" if bail_lang == "Hindi" else "en"
                    assessment = check_bail_eligibility(
                        offense_description=bail_offense,
                        bns_context=bns_context,
                        accused_details=accused_details,
                        language=language,
                    )
                except Exception as e:
                    assessment = f"⚠️ Error: {e}"

            # Display verdict with colour coding
            verdict_color = "#1a5c2e"  # green default
            if "NON-BAILABLE" in assessment.upper():
                verdict_color = "#8b1a1a"
            elif "ANTICIPATORY" in assessment.upper():
                verdict_color = "#6b4c1a"

            st.components.v1.html(f"""
            <!DOCTYPE html><html><head>
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Inter:wght@400;500;600&display=swap');
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ background: #0a0a0a; font-family: 'Inter', sans-serif; padding: 12px; }}
            .assessment {{ background: #111111; border: 1px solid #2a2a2a; border-left: 4px solid {verdict_color}; padding: 24px 28px; }}
            .assessment h2 {{ font-family: 'Cormorant Garamond', serif; color: {verdict_color}; font-size: 1.3rem; margin-bottom: 16px; }}
            .assessment h2::before {{ content: '⚖ '; }}
            .assessment p, .assessment li {{ font-size: 13.5px; color: #ccc; line-height: 1.75; }}
            .assessment ul {{ padding-left: 20px; margin: 8px 0; }}
            .assessment strong {{ color: {verdict_color}; }}
            .assessment h3, .assessment h2:not(:first-child) {{ font-family: 'Cormorant Garamond', serif; color: #d4af37; font-size: 1rem; margin: 16px 0 8px; }}
            pre {{ white-space: pre-wrap; font-family: inherit; font-size: 13.5px; line-height: 1.75; color: #ccc; }}
            </style></head>
            <body><div class="assessment"><pre>{assessment}</pre></div></body></html>
            """, height=600, scrolling=True)

            st.warning("⚠️ This assessment is AI-generated for informational purposes only. Bail decisions rest with the court. Consult a qualified advocate.")

# ── Footer ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  ⚖️ Nyaya-Sahayak · Powered by Sarvam-M + PageIndex + LangExtract + PySpark<br>
  This is an informational tool. For legal advice, consult a qualified advocate.<br>
  BNS 2023 data sourced from the Gazette of India.
</div>
""", unsafe_allow_html=True)
