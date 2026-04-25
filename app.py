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
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wdth,wght@0,62.5..100,100..900;1,62.5..100,100..900&family=Noto+Sans+Devanagari:wght@100..900&family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ═══════════════════════════════════════════════════════════
   KEYFRAME ANIMATIONS
═══════════════════════════════════════════════════════════ */
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 22px rgba(245,158,11,0.12), 0 0 70px rgba(245,158,11,0.04); }
    50%       { box-shadow: 0 0 38px rgba(245,158,11,0.28), 0 0 100px rgba(245,158,11,0.09); }
}
@keyframes float-in {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes stat-pop {
    0%   { transform: scale(0.90); opacity: 0; }
    100% { transform: scale(1);    opacity: 1; }
}

/* ═══════════════════════════════════════════════════════════
   RESET & BASE
═══════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #050d1a !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', 'Noto Sans', 'Noto Sans Devanagari', sans-serif !important;
}

[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070f1e 0%, #0a1628 100%) !important;
    border-right: 1px solid rgba(245,158,11,0.07) !important;
}

/* ═══════════════════════════════════════════════════════════
   HERO BANNER
═══════════════════════════════════════════════════════════ */
.hero {
    position: relative;
    overflow: hidden;
    border-radius: 24px;
    padding: 3rem 2.5rem 2.4rem;
    text-align: center;
    margin-bottom: 1.8rem;
    background: linear-gradient(140deg,
        #060f1f 0%,
        #0d1a33 28%,
        #150d2a 58%,
        #060f1f 100%);
    border: 1px solid rgba(245,158,11,0.20);
    animation: pulse-glow 5s ease-in-out infinite;
}

/* Radial spotlights */
.hero::before {
    content: '';
    position: absolute; inset: 0;
    background:
        radial-gradient(ellipse 72% 55% at 50% -8%,  rgba(245,158,11,0.17) 0%, transparent 65%),
        radial-gradient(ellipse 38% 28% at 12% 110%, rgba(124,58,237,0.10) 0%, transparent 60%),
        radial-gradient(ellipse 38% 28% at 88% 110%, rgba(245,158,11,0.07) 0%, transparent 60%);
    pointer-events: none;
}

/* Animated shimmer top edge */
.hero::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(245,158,11,0.0) 15%,
        rgba(245,158,11,0.85) 48%,
        rgba(253,230,138,1.0) 52%,
        rgba(245,158,11,0.85) 55%,
        rgba(245,158,11,0.0) 85%,
        transparent 100%);
    background-size: 200% auto;
    animation: shimmer 3.5s linear infinite;
}

.hero-inner { position: relative; z-index: 1; }

.hero-emblem {
    font-size: 3.2rem;
    line-height: 1;
    margin-bottom: .65rem;
    display: block;
    filter: drop-shadow(0 0 22px rgba(245,158,11,0.55));
}

.hero h1 {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -1.5px;
    line-height: 1.05;
    margin-bottom: .45rem;
    background: linear-gradient(120deg, #f59e0b 0%, #fde68a 40%, #f8b84e 70%, #f59e0b 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s linear infinite;
}

.hero .tagline {
    color: #94a3b8;
    font-size: 1.08rem;
    font-weight: 400;
    letter-spacing: .3px;
    margin-bottom: .7rem;
}

.hero .subtitle {
    display: inline-flex;
    flex-wrap: wrap;
    gap: .4rem;
    justify-content: center;
    margin-top: .4rem;
}

.hero .pill {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 999px;
    padding: .25rem .9rem;
    font-size: .79rem;
    color: #64748b;
    letter-spacing: .3px;
    backdrop-filter: blur(6px);
}

/* ═══════════════════════════════════════════════════════════
   PREMIUM STAT CARDS  (replaces st.metric)
═══════════════════════════════════════════════════════════ */
.stat-card {
    background: rgba(10,20,38,0.78);
    border: 1px solid rgba(245,158,11,0.13);
    border-radius: 16px;
    padding: 1.1rem 1.2rem 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    transition: border-color .25s ease, transform .25s ease, box-shadow .25s ease;
    animation: stat-pop .5s ease forwards;
}
.stat-card:hover {
    border-color: rgba(245,158,11,0.38);
    transform: translateY(-3px);
    box-shadow: 0 14px 36px rgba(0,0,0,0.38), 0 0 0 1px rgba(245,158,11,0.09);
}
.stat-icon {
    width: 46px; height: 46px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.35rem;
    flex-shrink: 0;
}
.stat-icon.amber  { background: rgba(245,158,11,0.12); box-shadow: 0 0 18px rgba(245,158,11,0.14); }
.stat-icon.violet { background: rgba(124,58,237,0.12); box-shadow: 0 0 18px rgba(124,58,237,0.14); }
.stat-icon.green  { background: rgba(34,197,94,0.10);  box-shadow: 0 0 18px rgba(34,197,94,0.12); }
.stat-icon.blue   { background: rgba(59,130,246,0.10); box-shadow: 0 0 18px rgba(59,130,246,0.12); }
.stat-body  { display: flex; flex-direction: column; gap: .12rem; min-width: 0; }
.stat-value {
    font-size: 1.6rem; font-weight: 800;
    color: #f59e0b; line-height: 1; letter-spacing: -0.5px;
}
.stat-label {
    font-size: .70rem; color: #4b5e7a;
    text-transform: uppercase; letter-spacing: .9px; font-weight: 600;
}

/* Language card */
.lang-card {
    background: rgba(10,20,38,0.78);
    border: 1px solid rgba(245,158,11,0.13);
    border-radius: 16px;
    padding: .9rem 1.3rem;
    display: flex; align-items: center; gap: .8rem;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    color: #94a3b8; font-size: .88rem; letter-spacing: .2px;
}
.lang-card .lang-icon {
    font-size: 1.4rem;
    filter: drop-shadow(0 0 10px rgba(245,158,11,0.45));
}
.lang-card strong { color: #f59e0b; font-weight: 600; }

/* ═══════════════════════════════════════════════════════════
   GLASS CARDS
═══════════════════════════════════════════════════════════ */
.card {
    position: relative;
    background: rgba(9,18,34,0.84);
    border: 1px solid rgba(245,158,11,0.12);
    border-radius: 16px;
    padding: 1.5rem 1.65rem;
    margin-bottom: 1.1rem;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    transition: border-color .22s ease, box-shadow .22s ease, transform .22s ease;
    animation: float-in .4s ease both;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute; inset: 0;
    border-radius: inherit;
    background: linear-gradient(135deg,
        rgba(245,158,11,0.04) 0%,
        transparent 50%,
        rgba(124,58,237,0.025) 100%);
    pointer-events: none;
}
.card:hover {
    border-color: rgba(245,158,11,0.35);
    transform: translateY(-2px);
    box-shadow: 0 12px 44px rgba(0,0,0,0.42), 0 0 0 1px rgba(245,158,11,0.07);
}
.card h4 {
    color: #f59e0b;
    font-size: 1.02rem;
    font-weight: 700;
    margin-bottom: .55rem;
    letter-spacing: .1px;
    display: flex;
    align-items: center;
    gap: .55rem;
}
.card h4::before {
    content: '';
    flex-shrink: 0;
    display: inline-block;
    width: 3px; height: 1.1em;
    background: linear-gradient(180deg, #f59e0b, #92400e);
    border-radius: 2px;
}
.card p { color: #94a3b8; font-size: .9rem; line-height: 1.65; }

/* ═══════════════════════════════════════════════════════════
   COMPARISON TABLE
═══════════════════════════════════════════════════════════ */
.compare-table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
.compare-table th {
    background: rgba(245,158,11,0.09);
    color: #f59e0b;
    padding: .75rem 1rem;
    text-align: left;
    font-size: .82rem; font-weight: 700;
    letter-spacing: .5px; text-transform: uppercase;
    border-bottom: 1px solid rgba(245,158,11,0.16);
}
.compare-table td {
    padding: .75rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #cbd5e1; font-size: .88rem; vertical-align: top;
}
.compare-table tr:hover td { background: rgba(245,158,11,0.032); }

/* ═══════════════════════════════════════════════════════════
   TAGS
═══════════════════════════════════════════════════════════ */
.tag-bns {
    display: inline-flex; align-items: center; gap: .3rem;
    background: rgba(34,197,94,0.11); color: #4ade80;
    border: 1px solid rgba(34,197,94,0.24);
    padding: 3px 11px; border-radius: 999px; font-size: .78rem; font-weight: 600;
}
.tag-ipc {
    display: inline-flex; align-items: center; gap: .3rem;
    background: rgba(239,68,68,0.11); color: #f87171;
    border: 1px solid rgba(239,68,68,0.24);
    padding: 3px 11px; border-radius: 999px; font-size: .78rem; font-weight: 600;
}
.tag-new {
    display: inline-flex; align-items: center; gap: .3rem;
    background: rgba(124,58,237,0.11); color: #a78bfa;
    border: 1px solid rgba(124,58,237,0.24);
    padding: 3px 11px; border-radius: 999px; font-size: .78rem; font-weight: 600;
}

/* ═══════════════════════════════════════════════════════════
   SCHEME BADGES  (category-coded)
═══════════════════════════════════════════════════════════ */
.scheme-badge {
    display: inline-block; padding: 3px 10px; border-radius: 999px;
    font-size: .72rem; font-weight: 600; margin-right: .3rem; border: 1px solid;
}
.scheme-badge.cat-agriculture { background:rgba(34,197,94,0.11);  color:#4ade80; border-color:rgba(34,197,94,0.26); }
.scheme-badge.cat-social      { background:rgba(124,58,237,0.11); color:#a78bfa; border-color:rgba(124,58,237,0.26); }
.scheme-badge.cat-education   { background:rgba(59,130,246,0.11); color:#60a5fa; border-color:rgba(59,130,246,0.26); }
.scheme-badge.cat-health      { background:rgba(239,68,68,0.11);  color:#f87171; border-color:rgba(239,68,68,0.26); }
.scheme-badge.cat-housing     { background:rgba(249,115,22,0.11); color:#fb923c; border-color:rgba(249,115,22,0.26); }
.scheme-badge.cat-finance     { background:rgba(245,158,11,0.11); color:#f59e0b; border-color:rgba(245,158,11,0.26); }
.scheme-badge.cat-women       { background:rgba(236,72,153,0.11); color:#f472b6; border-color:rgba(236,72,153,0.26); }
.scheme-badge.cat-legal       { background:rgba(20,184,166,0.11); color:#2dd4bf; border-color:rgba(20,184,166,0.26); }
.scheme-badge.cat-default     { background:rgba(245,158,11,0.09); color:#f59e0b; border-color:rgba(245,158,11,0.20); }

/* ═══════════════════════════════════════════════════════════
   SCHEME CARDS
═══════════════════════════════════════════════════════════ */
.scheme-card {
    position: relative;
    background: linear-gradient(135deg,
        rgba(9,18,34,0.92) 0%,
        rgba(15,10,30,0.88) 100%);
    border: 1px solid rgba(124,58,237,0.18);
    border-radius: 15px;
    padding: 1.2rem 1.35rem;
    margin-bottom: .9rem;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    transition: border-color .22s ease, transform .22s ease, box-shadow .22s ease;
    overflow: hidden;
}
.scheme-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(124,58,237,0.45), transparent);
}
.scheme-card:hover {
    border-color: rgba(124,58,237,0.42);
    transform: translateY(-2px);
    box-shadow: 0 10px 32px rgba(0,0,0,0.42), 0 0 22px rgba(124,58,237,0.07);
}
.scheme-card .sc-title   { color: #c4b5fd; font-weight: 700; font-size: .97rem; }
.scheme-card .sc-benefit {
    color: #4ade80; font-size: .85rem; margin: .38rem 0;
    display: flex; align-items: center; gap: .4rem;
}
.scheme-card .sc-eligibility { color: #64748b; font-size: .82rem; line-height: 1.55; }

/* ═══════════════════════════════════════════════════════════
   CHAT BUBBLES
═══════════════════════════════════════════════════════════ */
.msg-user {
    background: linear-gradient(135deg, rgba(109,40,217,0.26) 0%, rgba(124,58,237,0.18) 100%);
    border: 1px solid rgba(124,58,237,0.36);
    border-radius: 18px 18px 4px 18px;
    padding: .92rem 1.15rem;
    margin: .6rem 0 .6rem 18%;
    color: #ddd6fe; font-size: .93rem; line-height: 1.62;
    backdrop-filter: blur(8px);
    animation: float-in .3s ease;
}
.msg-bot {
    background: rgba(9,18,34,0.90);
    border: 1px solid rgba(245,158,11,0.16);
    border-radius: 18px 18px 18px 4px;
    padding: .92rem 1.15rem;
    margin: .6rem 18% .6rem 0;
    color: #cbd5e1; font-size: .93rem; line-height: 1.70;
    backdrop-filter: blur(8px);
    box-shadow:
        0 0 0 1px rgba(245,158,11,0.05),
        0 4px 22px rgba(0,0,0,0.32),
        0 0 32px rgba(245,158,11,0.055);
    animation: float-in .35s ease;
    transition: box-shadow .25s ease;
}
.msg-bot:hover {
    box-shadow:
        0 0 0 1px rgba(245,158,11,0.12),
        0 8px 30px rgba(0,0,0,0.42),
        0 0 44px rgba(245,158,11,0.10);
}
.msg-bot strong { color: #fbbf24; }

/* ═══════════════════════════════════════════════════════════
   TAB BAR
═══════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: rgba(6,13,27,0.92);
    border-radius: 14px;
    padding: 5px;
    border: 1px solid rgba(245,158,11,0.11);
    backdrop-filter: blur(12px);
}
.stTabs [data-baseweb="tab"] {
    color: #3d5068 !important;
    border-radius: 10px !important;
    padding: .55rem 1.3rem !important;
    font-size: .87rem !important;
    font-weight: 500 !important;
    letter-spacing: .15px;
    transition: color .2s ease, background .2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #94a3b8 !important;
    background: rgba(255,255,255,0.035) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(180,83,9,0.28), rgba(217,119,6,0.20)) !important;
    color: #fbbf24 !important;
    box-shadow: 0 0 0 1px rgba(245,158,11,0.20), 0 2px 12px rgba(245,158,11,0.10) !important;
}

/* ═══════════════════════════════════════════════════════════
   INPUT FIELDS
═══════════════════════════════════════════════════════════ */
.stTextInput input,
.stTextArea textarea,
.stSelectbox select,
div[data-baseweb="select"] > div,
.stNumberInput input {
    background: rgba(6,15,28,0.88) !important;
    border: 1px solid rgba(245,158,11,0.16) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    transition: border-color .2s ease, box-shadow .2s ease !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: rgba(245,158,11,0.62) !important;
    box-shadow:
        0 0 0 3px rgba(245,158,11,0.07),
        0 0 18px rgba(245,158,11,0.10) !important;
    outline: none !important;
}

/* ═══════════════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════════════ */
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #92400e 0%, #b45309 45%, #d97706 100%) !important;
    color: #fff8e7 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: .9rem !important;
    letter-spacing: .3px;
    padding: .58rem 1.5rem !important;
    transition: all .22s ease !important;
    position: relative; overflow: hidden;
}
.stButton > button::after,
.stFormSubmitButton > button::after {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.07) 0%, transparent 55%);
    pointer-events: none;
}
.stButton > button:hover,
.stFormSubmitButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow:
        0 7px 26px rgba(245,158,11,0.36),
        0 0 0 1px rgba(245,158,11,0.22) !important;
}
.stButton > button:active,
.stFormSubmitButton > button:active { transform: translateY(0) !important; }

[data-testid="stDownloadButton"] button {
    background: rgba(9,18,34,0.92) !important;
    border: 1px solid rgba(245,158,11,0.28) !important;
    color: #f59e0b !important;
    box-shadow: none !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: rgba(245,158,11,0.10) !important;
    transform: translateY(-2px) !important;
}

/* ═══════════════════════════════════════════════════════════
   SPINNER / DIVIDER
═══════════════════════════════════════════════════════════ */
.stSpinner > div { border-top-color: #f59e0b !important; }
hr { border: none !important; border-top: 1px solid rgba(245,158,11,0.07) !important; margin: 1.4rem 0 !important; }

/* ═══════════════════════════════════════════════════════════
   NATIVE STREAMLIT METRICS  (fallback styling)
═══════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: rgba(9,18,34,0.84);
    border: 1px solid rgba(245,158,11,0.13);
    border-radius: 14px; padding: 1rem 1.2rem;
    backdrop-filter: blur(12px);
}
[data-testid="metric-container"] label {
    color: #475569 !important; font-size: .70rem !important;
    text-transform: uppercase; letter-spacing: .9px; font-weight: 600 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f59e0b !important; font-weight: 800 !important; font-size: 1.6rem !important;
}

/* ═══════════════════════════════════════════════════════════
   MISC COMPONENTS
═══════════════════════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: rgba(9,18,34,0.82) !important;
    border: 1px solid rgba(245,158,11,0.11) !important;
    border-radius: 10px !important; color: #94a3b8 !important;
}
.stCheckbox label { color: #94a3b8 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(5,13,26,0.8); }
::-webkit-scrollbar-thumb { background: rgba(245,158,11,0.22); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(245,158,11,0.42); }

/* ═══════════════════════════════════════════════════════════
   FOOTER
═══════════════════════════════════════════════════════════ */
.footer {
    text-align: center; color: #1e2d45; font-size: .76rem;
    margin-top: 2.5rem; padding-top: 1.2rem;
    border-top: 1px solid rgba(255,255,255,0.04);
    letter-spacing: .3px;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-inner">
    <span class="hero-emblem">⚖️</span>
    <h1>न्याय-सहायक</h1>
    <div class="tagline">Nyaya-Sahayak &nbsp;·&nbsp; AI-Powered Indian Legal Assistant</div>
    <div class="subtitle">
      <span class="pill">BNS 2023</span>
      <span class="pill">IPC Comparison</span>
      <span class="pill">Government Schemes</span>
      <span class="pill">Hindi &amp; English</span>
      <span class="pill">22+ Languages</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stats Row ────────────────────────────────────────────────────────────────────
col_lang, col_stat1, col_stat2, col_stat3, col_stat4 = st.columns([2,1,1,1,1])
with col_lang:
    st.markdown("""
    <div class="lang-card">
        <span class="lang-icon">🌐</span>
        <div>
            <strong>Multilingual</strong><br>
            <span style="font-size:.8rem; color:#475569;">Type in any Indian language</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    lang_code = "auto"
with col_stat1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon amber">🗣️</div>
        <div class="stat-body">
            <span class="stat-value">22+</span>
            <span class="stat-label">Languages</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_stat2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon violet">📜</div>
        <div class="stat-body">
            <span class="stat-value">358</span>
            <span class="stat-label">BNS Sections</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_stat3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon green">🔄</div>
        <div class="stat-body">
            <span class="stat-value">300+</span>
            <span class="stat-label">IPC→BNS Maps</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_stat4:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon blue">🏛️</div>
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
    from nyaya_sahayak.rag_engine import get_engine
    return get_engine()

@st.cache_resource(show_spinner="Loading comparison engine…")
def load_comparator():
    from nyaya_sahayak.comparator import get_comparator
    return get_comparator()

@st.cache_resource(show_spinner="Loading cache…")
def load_cache():
    from nyaya_sahayak.cache import QueryCache
    return QueryCache()

@st.cache_resource(show_spinner="Loading scheme database…")
def load_checker():
    from nyaya_sahayak.scheme_checker import get_checker
    return get_checker()

# ── Tabs ─────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Legal Chatbot",
    "⚖️ IPC vs BNS Compare",
    "🔄 Section Translator",
    "🏛️ Scheme Checker",
    "📋 FIR Generator",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LEGAL CHATBOT
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="card">
      <h4>💬 Ask any legal question about BNS or IPC</h4>
      <p>Ask in Hindi or English. Answers include section references and practical advice.</p>
    </div>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_summary" not in st.session_state:
        st.session_state.chat_summary = ""
    if "recent_turns" not in st.session_state:
        st.session_state.recent_turns = []
    if "turn_count" not in st.session_state:
        st.session_state.turn_count = 0

    # Display history
    for role, msg in st.session_state.chat_history:
        css_cls = "msg-user" if role == "user" else "msg-bot"
        icon = "👤" if role == "user" else "⚖️"
        st.markdown(f'<div class="{css_cls}">{icon} {msg}</div>', unsafe_allow_html=True)

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
                        language="auto",
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
            from nyaya_sahayak.llm_client import summarize_conversation
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
      <h4>⚖️ Scenario-based IPC vs BNS Comparison</h4>
      <p>Describe a legal scenario and get a side-by-side comparison of old IPC and new BNS provisions.</p>
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

    if st.button("🔍 Compare IPC vs BNS", key="cmp_btn"):
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

                c_bns, c_ipc = st.columns(2)
                with c_bns:
                    st.markdown('<span class="tag-bns">✅ BNS 2023</span>', unsafe_allow_html=True)
                    if bns_r:
                        for r in bns_r:
                            st.markdown(f"""
                            <div class="card">
                              <h4>{r.get('title','BNS Section')}</h4>
                              <p>{r.get('text','')[:400]}</p>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.info("No specific BNS sections found via index.")

                with c_ipc:
                    st.markdown('<span class="tag-ipc">📜 IPC 1860</span>', unsafe_allow_html=True)
                    if ipc_r:
                        for r in ipc_r:
                            st.markdown(f"""
                            <div class="card">
                              <h4>{r.get('title','IPC Section')}</h4>
                              <p>{r.get('text','')[:400]}</p>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.info("IPC index not yet built. Run pipeline to extract IPC text.")

                st.markdown("---")
                st.markdown("### 🤖 AI Analysis")
                st.markdown(f'<div class="msg-bot">⚖️ {result["llm_analysis"]}</div>', unsafe_allow_html=True)

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

    # Quick lookup table
    st.markdown("#### 📋 Common IPC → BNS Mappings")
    try:
        comp = load_comparator()
        df = comp.get_full_mapping_df()
        df_display = df[df["bns_section"] != "NEW"][
            ["ipc_section","ipc_name","bns_section","bns_name","category","note"]
        ].rename(columns={
            "ipc_section":"IPC §","ipc_name":"IPC Offence",
            "bns_section":"BNS §","bns_name":"BNS Offence",
            "category":"Category","note":"Key Change"
        })
        st.dataframe(
            df_display,
            use_container_width=True,
            height=300,
            hide_index=True,
        )
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
                    from nyaya_sahayak.llm_client import chat as llm_chat
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
      <h4>🏛️ Government Scheme Eligibility Checker</h4>
      <p>Fill in your profile and discover which of 3400+ central and state government schemes you qualify for.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("scheme_form"):
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            age = st.number_input("Age", 10, 100, 30)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        with r1c2:
            income = st.number_input("Annual Income (LPA ₹)", 0.0, 50.0, 2.0, step=0.5)
            caste = st.selectbox("Category", ["General","OBC","SC","ST"])
        with r1c3:
            location = st.selectbox("Location", ["Urban", "Rural"])
            occupation = st.selectbox("Occupation", ["Farmer","Student","Salaried","Self-employed","Unemployed","Business"])

        r2c1, r2c2, r2c3, r2c4 = st.columns(4)
        with r2c1: is_bpl = st.checkbox("BPL Card Holder")
        with r2c2: has_disability = st.checkbox("Differently-abled")
        with r2c3: is_survivor = st.checkbox("Violence Survivor")
        with r2c4: needs_legal = st.checkbox("Needs Legal Aid")

        r3c1, r3c2, r3c3 = st.columns(3)
        with r3c1: has_land = st.checkbox("Has Agricultural Land")
        with r3c2: has_girl = st.checkbox("Has Girl Child (< 10 yrs)")
        with r3c3: no_lpg = st.checkbox("No LPG Connection")

        scheme_submit = st.form_submit_button("🔍 Find Matching Schemes", use_container_width=True)

    if "scheme_profile" not in st.session_state:
        st.session_state.scheme_profile = None
    if "scheme_matched" not in st.session_state:
        st.session_state.scheme_matched = []

    if scheme_submit:
        profile = {
            "age": age,
            "gender": gender.lower(),
            "annual_income_lpa": income,
            "caste": caste.lower(),
            "location": location.lower(),
            "occupation": occupation.lower(),
            "is_bpl": is_bpl,
            "has_disability": has_disability,
            "is_violence_survivor": is_survivor,
            "needs_legal_aid": needs_legal,
            "has_agricultural_land": has_land,
            "has_girl_child": has_girl,
            "no_lpg": no_lpg,
        }

        with st.spinner("Matching schemes…"):
            try:
                checker = load_checker()
                result = checker.check_eligibility(profile, language="auto")
            except Exception as e:
                st.error(f"Error: {e}")
                result = None

        if result:
            st.session_state.scheme_profile = profile
            st.session_state.scheme_matched = result.get("matched_schemes", [])
            matched = result["matched_schemes"]
            st.success(f"Found **{result['total_matched']}** potentially eligible schemes. Showing top {len(matched)}.")

            # Category → CSS class mapping
            CAT_CLASS = {
                "agriculture": "cat-agriculture", "farmer": "cat-agriculture",
                "social": "cat-social", "welfare": "cat-social",
                "education": "cat-education", "scholarship": "cat-education",
                "health": "cat-health", "medical": "cat-health",
                "housing": "cat-housing", "shelter": "cat-housing",
                "finance": "cat-finance", "financial": "cat-finance", "insurance": "cat-finance",
                "women": "cat-women", "gender": "cat-women",
                "legal": "cat-legal", "aid": "cat-legal",
            }

            # Scheme cards
            for scheme in matched:
                cat = scheme.get("category", "")
                benefit = scheme.get("benefit", "")
                url = scheme.get("url", "")
                score = scheme.get("_score", 0)
                level = scheme.get("level", "")
                tags = scheme.get("tags", "")
                level_color = "#4ade80" if level == "Central" else "#60a5fa"

                cat_class = "cat-default"
                for key, cls in CAT_CLASS.items():
                    if key in cat.lower():
                        cat_class = cls
                        break

                st.markdown(f"""
                <div class="scheme-card">
                  <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div style="flex:1;">
                      <span class="sc-title">{scheme['name']}</span><br>
                      <span class="scheme-badge {cat_class}">{cat}</span>
                      <span style="background:rgba(255,255,255,0.05); color:{level_color}; padding:2px 8px; border-radius:20px; font-size:.72rem; margin-left:.3rem; border:1px solid rgba(255,255,255,0.08);">{level}</span>
                      <div class="sc-benefit" style="margin-top:.4rem;">💰 {benefit[:200]}</div>
                      <div class="sc-eligibility" style="margin-top:.3rem;">{scheme.get('description','')[:130]}…</div>
                      {f'<div style="color:#334155; font-size:.75rem; margin-top:.3rem;">🏷️ {tags[:100]}</div>' if tags else ''}
                    </div>
                    <div style="text-align:right; min-width:80px; padding-left:.8rem;">
                      <span style="color:#f59e0b; font-size:.8rem; font-weight:600;">⭐ {score}pts</span><br>
                      {f"<a href='{url}' target='_blank' style='color:#a78bfa; font-size:.78rem; text-decoration:none;'>🔗 Apply</a>" if url else ""}
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### 🤖 AI Guide")
            st.markdown(f'<div class="msg-bot">⚖️ {result["explanation"]}</div>', unsafe_allow_html=True)

    # Follow-up Q&A using stored profile + matched schemes as context
    if st.session_state.scheme_profile and st.session_state.scheme_matched:
        st.markdown("---")
        st.markdown("#### 💬 Ask a follow-up about your schemes")
        with st.form("scheme_followup_form", clear_on_submit=True):
            followup_q = st.text_input(
                "Follow-up question…",
                placeholder="e.g. How do I apply for MGNREGA? / Am I eligible even if I work part-time?",
                label_visibility="collapsed",
            )
            followup_submit = st.form_submit_button("Ask ➤", use_container_width=True)

        if followup_submit and followup_q.strip():
            with st.spinner("Thinking…"):
                try:
                    from nyaya_sahayak.llm_client import chat as llm_chat, ANSWER_SYSTEM_PROMPT_EN
                    profile_text = "\n".join(f"- {k}: {v}" for k, v in st.session_state.scheme_profile.items())
                    schemes_text = "\n".join(
                        f"- {s['name']} (score: {s.get('_score', 0)}): {s.get('benefit', '')}"
                        for s in st.session_state.scheme_matched
                    )
                    followup_message = f"""[USER PROFILE]
{profile_text}

[MATCHED GOVERNMENT SCHEMES]
{schemes_text}

---

User Question: {followup_q}"""
                    followup_answer = llm_chat(
                        [{"role": "user", "content": followup_message}],
                        language="auto",
                        max_tokens=600,
                        _system_override=ANSWER_SYSTEM_PROMPT_EN,
                    )
                except Exception as e:
                    followup_answer = f"⚠️ Error: {e}"
            st.markdown(f'<div class="msg-bot">⚖️ {followup_answer}</div>', unsafe_allow_html=True)

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
                    from nyaya_sahayak.llm_client import generate_fir
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
            st.markdown(
                f'<div class="msg-bot" style="font-family: monospace; white-space: pre-wrap;">{fir_draft}</div>',
                unsafe_allow_html=True,
            )
            st.download_button(
                label="⬇️ Download FIR Draft (.txt)",
                data=fir_draft,
                file_name=f"FIR_Draft_{fir_name.replace(' ', '_')}_{incident_date}.txt",
                mime="text/plain",
            )
            st.warning("⚠️ This is an AI-generated draft for reference only. Review with a qualified advocate before submission.")

# ── Footer ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  ⚖️ Nyaya-Sahayak · Powered by Sarvam-M + PageIndex + LangExtract + PySpark<br>
  This is an informational tool. For legal advice, consult a qualified advocate.<br>
  BNS 2023 data sourced from the Gazette of India.
</div>
""", unsafe_allow_html=True)
