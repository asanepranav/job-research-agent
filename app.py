import streamlit as st
import os
from dotenv import load_dotenv
from agent import run_agent

load_dotenv()

st.set_page_config(
    page_title="Job Research Agent",
    page_icon="🤖",
    layout="wide",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: #0a0a10; color: #e8e6df; }

    .main-title {
        font-family: 'Space Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: #c4b5fd;
        letter-spacing: -1px;
    }
    .subtitle { color: #555; font-size: 0.9rem; margin-bottom: 2rem; }

    .step-card {
        background: #12121a;
        border: 1px solid #1e1e30;
        border-left: 3px solid #7c3aed;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 8px 0;
        font-family: 'Space Mono', monospace;
        font-size: 0.8rem;
    }
    .step-thought { border-left-color: #6366f1; color: #a5b4fc; }
    .step-action  { border-left-color: #10b981; color: #6ee7b7; }
    .step-obs     { border-left-color: #f59e0b; color: #fcd34d; font-size: 0.75rem; color: #888; font-family: 'DM Sans', sans-serif; }

    .final-card {
        background: #12121a;
        border: 1px solid #2e2e45;
        border-radius: 10px;
        padding: 20px 24px;
        margin-top: 16px;
        line-height: 1.8;
        color: #d4d0c8;
    }
    .tag {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-family: 'Space Mono', monospace;
        margin: 2px;
    }
    .tag-purple { background: #c4b5fd22; color: #c4b5fd; border: 1px solid #c4b5fd44; }
    .tag-green  { background: #6ee7b722; color: #6ee7b7; border: 1px solid #6ee7b744; }
    .tag-amber  { background: #fcd34d22; color: #fcd34d; border: 1px solid #fcd34d44; }

    div[data-testid="stSidebar"] { background: #07070d; border-right: 1px solid #1a1a28; }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #12121a !important;
        color: #e8e6df !important;
        border: 1px solid #2e2e40 !important;
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .stButton > button {
        background: #7c3aed !important;
        color: #fff !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Space Mono', monospace !important;
        padding: 0.6rem 2rem !important;
        font-size: 0.9rem !important;
        width: 100% !important;
    }
    .stButton > button:hover { background: #6d28d9 !important; }
    .status-ok { color: #6ee7b7; font-weight: 500; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "running" not in st.session_state:
    st.session_state.running = False

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="main-title">🤖 Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Autonomous job research</div>', unsafe_allow_html=True)

    st.markdown("**API Keys**")

    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    tavily_key = st.text_input("Tavily API Key", type="password", placeholder="tvly-...")

    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key

    if groq_key and tavily_key:
        st.markdown('<div class="status-ok">✓ Both keys set</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="font-size:0.72rem;color:#444;font-family:'Space Mono',monospace;line-height:2">
    agent tools<br>
    ✓ search_jobs<br>
    ✓ search_company<br>
    ✓ extract_skills<br>
    ✓ draft_outreach_email<br><br>
    framework<br>
    ✓ LangChain ReAct<br>
    ✓ Groq LLaMA 3.1<br>
    ✓ Tavily Search
    </div>
    """, unsafe_allow_html=True)

# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🤖 Job Research Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Tell the agent what you\'re looking for. It searches, researches, and drafts emails — autonomously.</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    role = st.text_input(
        "Target role",
        placeholder="Data Scientist, ML Engineer, Data Analyst...",
        value="Data Scientist"
    )
    location = st.text_input(
        "Location",
        placeholder="Pune, Mumbai, Bangalore, Remote...",
        value="Pune, India"
    )

with col2:
    background = st.text_area(
        "Your background (2-3 lines)",
        placeholder="BE in AI-DS, built RAG chatbots with LangChain and HuggingFace, know Python, SQL, ML...",
        height=103,
        value="BE in AI-DS graduate. Built RAG chatbots using LangChain, HuggingFace, FAISS. Skilled in Python, SQL, and ML. Looking for entry-level DS/ML roles."
    )

st.markdown("---")

# Quick role presets
st.markdown('<span style="font-size:0.78rem;color:#555">Quick presets:</span>', unsafe_allow_html=True)
pcols = st.columns(4)
presets = ["Data Scientist", "ML Engineer", "Data Analyst", "NLP Engineer"]
for i, p in enumerate(presets):
    if pcols[i].button(p, key=f"preset_{i}"):
        st.session_state["role_input"] = p

run_btn = st.button("🚀 Run Agent", disabled=not (groq_key and tavily_key))

if not (groq_key and tavily_key):
    st.caption("Enter both API keys in the sidebar to run the agent.")

# ── Run agent ──────────────────────────────────────────────────────────────────
if run_btn and role and background:
    st.session_state.result = None
    with st.spinner("Agent is running... this takes 30-60 seconds"):
        try:
            result = run_agent(role, location, background)
            st.session_state.result = result
        except Exception as e:
            st.error(f"Agent error: {str(e)}")

# ── Display results ────────────────────────────────────────────────────────────
if st.session_state.result:
    result = st.session_state.result

    # Agent thought process
    steps = result.get("steps", [])
    if steps:
        st.markdown("### Agent thought process")
        st.markdown(f'<span class="tag tag-purple">{len(steps)} steps taken</span>', unsafe_allow_html=True)

        for i, step in enumerate(steps, 1):
            tool_name = step.get("tool", "unknown")
            tool_input = step.get("input", "")
            observation = step.get("output", "")

            st.markdown(f'<div class="step-card step-action">⚡ Action: <strong>{tool_name}</strong> ← {str(tool_input)[:120]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="step-card step-obs">📥 Observation: {str(observation)[:300]}...</div>', unsafe_allow_html=True)

    # Final answer
    st.markdown("### Final report")
    final = result.get("final_answer", "")
    st.markdown(f'<div class="final-card">{final.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

    # Action buttons
    st.markdown("---")
    bcols = st.columns(3)
    bcols[0].download_button(
        "📥 Download report",
        data=final,
        file_name=f"job_research_{role.replace(' ', '_')}.txt",
        mime="text/plain"
    )
    if bcols[1].button("🔄 Run again"):
        st.session_state.result = None
        st.rerun()
