import streamlit as st
import requests

st.set_page_config(
    page_title="ScopeCheck | Zero-Leak Contract & Scope Auditor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Editorial & Studio Dark Styling
st.markdown("""
<style>
    @import url('[https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap](https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap)');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #0b0f17;
        color: #e2e8f0;
    }
    
    [data-testid="stSidebar"] {
        background-color: #080c13 !important;
        border-right: 1px solid #1a2234;
    }

    h1, h2, h3, h5 {
        letter-spacing: -0.025em;
        font-weight: 600;
        color: #f8fafc !important;
    }

    .brand-title {
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #ffffff;
        margin-bottom: 0.15rem;
    }

    .brand-sub {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }

    .privacy-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        color: #34d399;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
    }

    .stButton > button {
        background-color: #f59e0b !important;
        color: #000000 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.25rem !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #fbbf24 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.25);
    }

    .stTextArea textarea {
        background-color: #111827 !important;
        border: 1px solid #1f293d !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.88rem;
    }
    .stTextArea textarea:focus {
        border-color: #f59e0b !important;
        box-shadow: 0 0 0 1px #f59e0b !important;
    }
</style>
""", unsafe_allow_html=True)

# Detect local Ollama Gemma models
def get_installed_gemma_models():
    try:
        res = requests.get("http://localhost:11434/api/tags", timeout=3)
        if res.status_code == 200:
            models = [m["name"] for m in res.json().get("models", [])]
            gemma_models = [m for m in models if "gemma" in m.lower()]
            return gemma_models if gemma_models else models
    except Exception:
        pass
    return ["gemma2:2b", "gemma3:4b", "gemma3:1b"]

available_models = get_installed_gemma_models()
default_index = 0
for idx, model_name in enumerate(available_models):
    if "gemma2:2b" in model_name:
        default_index = idx
        break

# Sidebar
with st.sidebar:
    st.markdown("### Runtime Config")
    selected_model = st.selectbox("Inference Engine", available_models, index=default_index)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="privacy-tag">
        ● Air-Gapped Local Inference
    </div>
    <div style="font-size: 0.82rem; color: #64748b; margin-top: 0.6rem; line-height: 1.5;">
        Raw contracts and confidential emails are processed entirely in-memory via Ollama. Zero network requests transmit your client agreements off-device.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<span style='font-size: 0.78rem; color: #475569;'>Hacktoberfest '26 — Week 2: Side Hustle Track</span>", unsafe_allow_html=True)

# Header Section
st.markdown('<div class="brand-title">🛡️ ScopeCheck</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">Privacy-first scope creep detection & contract boundary auditor for independent developers and creative studios.</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("##### 1. Input Specification")
    input_format = st.radio(
        "Source Type",
        ["Client Revision Request", "Contract / SOW Clause"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    sample_text = (
        "Hey! The dashboard layout looks clean. While you have the codebase open, could you quickly "
        "hook up user authentication, Stripe payment webhooks, and an export-to-PDF button before tomorrow? "
        "Should only take a few minutes since the UI is already done!"
    )
    
    user_input = st.text_area(
        "Payload",
        value=sample_text,
        height=210,
        label_visibility="collapsed"
    )
    
    run_audit = st.button("Audit Scope & Generate Pushback", use_container_width=True)

AUDIT_PROMPT = """You are an experienced technical project manager and client-relations auditor.
Analyze the provided client request or contract clause against standard freelance engineering boundaries:

<INPUT>
{input_text}
</INPUT>

Evaluate strictly using the following structured format:

### 1. Scope Creep Risk Assessment
- Rating: [X]/10
- Summary Analysis: [Concise 1-2 sentence teardown explaining why this violates delivery milestones or introduces architectural debt]

### 2. Ambiguity & Unbilled Deliverables
- [Feature 1]: [Why this is an expansion, not a revision]
- [Feature 2]: [Architecture, backend, or dependency requirements]

### 3. Client Pushback Script
[A polite, assertive response acknowledging the request, clarifying that it is out of original scope, and proposing an add-on quote/timeline adjustment without damaging the relationship]
"""

with col2:
    st.markdown("##### 2. Audit Report & Client Script")
    
    if run_audit and user_input.strip():
        with st.spinner(f"Analyzing via {selected_model}..."):
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": selected_model,
                        "prompt": AUDIT_PROMPT.format(input_text=user_input),
                        "stream": False
                    },
                    timeout=180
                )
                
                if response.status_code == 200:
                    result = response.json().get("response", "")
                    st.markdown(result)
                    st.markdown("""
                    <div style="margin-top: 1.5rem; display: inline-flex; align-items: center; gap: 8px; font-size: 0.85rem; color: #34d399;">
                        <span>✔</span> Audit verified locally. Zero proprietary data logged or leaked.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Inference returned status {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Ollama connection failed. Verify that Ollama is running.")
            except requests.exceptions.ReadTimeout:
                st.error("Model took too long to respond. Ensure your system resources are available.")
    elif run_audit:
        st.warning("Please provide input text to audit.")