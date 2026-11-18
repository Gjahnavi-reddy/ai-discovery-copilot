"""
Cynbit AI Discovery Copilot — Streamlit Web Application.

Brand-aligned corporate technology dashboard for Cynbit Technologies (cynbit.in).
Palette:
- Main background: #F4F8F8
- Card background: #FFFFFF
- Secondary background: #EAF2F3
- Primary brand teal: #00666B
- Secondary teal: #4B969B
- Pale aqua decorative accent: #B4D5D8
- Warm peach accent: #FFD9A8
- Primary text: #1A2021
- Secondary text: #637477
- Border: #DCE6E7
"""

import sys
import os
import json
from datetime import datetime, timezone
import streamlit as st

# Ensure root path is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import (
    CYNBIT_SERVICE_REGISTRY,
    CynbitServiceCategory,
    GROUNDING_FACTS_ASSUMPTIONS_RECOMMENDATIONS,
)
from src.models.schemas import InquiryInput, PipelineResult, ScoreBreakdown
from src.data.sample_inquiries import BENCHMARK_INQUIRIES, get_benchmark_by_id
from src.core.engine import DiscoveryCopilotEngine
from src.pdf_generator import generate_discovery_pdf_bytes

# Page configuration
st.set_page_config(
    page_title="Cynbit AI Discovery Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Cynbit Brand Styling
st.markdown("""
<style>
    /* Global Application Canvas */
    html, body, [data-testid="stAppViewContainer"], .main {
        background-color: #F4F8F8 !important;
        color: #1A2021 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Sidebar Container Styling */
    [data-testid="stSidebar"] {
        background-color: #EAF2F3 !important;
        border-right: 1px solid #DCE6E7 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #DCE6E7 !important;
    }

    /* Sidebar Text & Label High Contrast */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stWidgetLabel,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] span,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] div,
    [data-testid="stSidebar"] label[data-baseweb="label"],
    [data-testid="stSidebar"] label[data-baseweb="label"] * {
        color: #1A2021 !important;
        font-weight: 600 !important;
        font-size: 0.84rem !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label,
    [data-testid="stSidebar"] div[role="radiogroup"] label p,
    [data-testid="stSidebar"] div[role="radiogroup"] label span,
    [data-testid="stSidebar"] div[role="radiogroup"] label div,
    [data-testid="stSidebar"] div[role="radiogroup"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] div[role="radiogroup"] [data-testid="stMarkdownContainer"] span {
        color: #1A2021 !important;
        font-weight: 500 !important;
        font-size: 0.84rem !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] [data-checked="true"] > div {
        background-color: #00666B !important;
        border-color: #00666B !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"],
    [data-testid="stSidebar"] div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] div[data-baseweb="select"] div[role="combobox"],
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div[role="combobox"],
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [aria-haspopup="listbox"] {
        background-color: #FFFFFF !important;
        border: 1px solid #DCE6E7 !important;
        border-radius: 8px !important;
        color: #1A2021 !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] *,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] * {
        color: #1A2021 !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] svg {
        fill: #00666B !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="input"],
    [data-testid="stSidebar"] div[data-baseweb="input"] > div,
    [data-testid="stSidebar"] div[data-baseweb="input"] input,
    [data-testid="stSidebar"] [data-testid="stTextInput"] input,
    [data-testid="stSidebar"] [data-testid="stTextInput"] div[data-baseweb="input"] > div {
        background-color: #FFFFFF !important;
        color: #1A2021 !important;
        border: 1px solid #DCE6E7 !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="input"] button svg {
        fill: #637477 !important;
    }

    [data-testid="stSidebar"] [data-testid="stExpander"],
    [data-testid="stSidebar"] details {
        background-color: #FFFFFF !important;
        border: 1px solid #DCE6E7 !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary,
    [data-testid="stSidebar"] details summary,
    [data-testid="stSidebar"] [data-testid="stExpander"] summary p,
    [data-testid="stSidebar"] [data-testid="stExpander"] summary span,
    [data-testid="stSidebar"] [data-testid="stExpander"] summary * {
        color: #1A2021 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary svg {
        fill: #00666B !important;
        color: #00666B !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"],
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] p,
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] span,
    [data-testid="stSidebar"] [data-testid="stExpanderDetails"] * {
        color: #1A2021 !important;
    }

    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] p[data-testid="stCaption"] {
        color: #637477 !important;
        font-size: 0.76rem !important;
    }

    [data-testid="stSidebar"] [data-testid="stTooltipHoverTarget"] svg,
    [data-testid="stSidebar"] .stTooltipIcon svg {
        fill: #637477 !important;
        color: #637477 !important;
    }

    /* Main Area Widget Label Contrast */
    label,
    .stWidgetLabel,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {
        color: #1A2021 !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
    }

    /* Dropdown Menus */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
        border: 1px solid #DCE6E7 !important;
        color: #1A2021 !important;
    }
    div[data-baseweb="menu"] li,
    ul[data-baseweb="menu"] li,
    div[data-baseweb="menu"] li *,
    ul[data-baseweb="menu"] li * {
        color: #1A2021 !important;
        background-color: #FFFFFF !important;
    }
    div[data-baseweb="menu"] li:hover,
    ul[data-baseweb="menu"] li:hover,
    div[data-baseweb="menu"] li[aria-selected="true"],
    ul[data-baseweb="menu"] li[aria-selected="true"] {
        background-color: #EAF2F3 !important;
        color: #00666B !important;
    }

    /* Headers & Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #1A2021 !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
    }

    /* Buttons */
    .stButton > button[kind="primary"], .stButton > button[type="primary"] {
        background-color: #00666B !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.3rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 3px rgba(0, 102, 107, 0.15) !important;
    }
    .stButton > button[kind="primary"]:hover, .stButton > button[type="primary"]:hover {
        background-color: #004D51 !important;
        box-shadow: 0 3px 8px rgba(0, 102, 107, 0.25) !important;
    }

    .stButton > button:not([kind="primary"]):not([type="primary"]), .stDownloadButton > button {
        background-color: #FFFFFF !important;
        color: #00666B !important;
        border: 1px solid #DCE6E7 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:not([kind="primary"]):not([type="primary"]):hover, .stDownloadButton > button:hover {
        background-color: #EAF2F3 !important;
        border-color: #4B969B !important;
        color: #004D51 !important;
    }

    /* Form Inputs & Textareas */
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #DCE6E7 !important;
        border-radius: 8px !important;
        color: #1A2021 !important;
    }
    div[data-baseweb="input"]:focus-within > div, div[data-baseweb="textarea"]:focus-within > div {
        border-color: #00666B !important;
        box-shadow: 0 0 0 1px #00666B !important;
    }

    /* Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px !important;
        border-bottom: 1px solid #DCE6E7 !important;
        background-color: transparent !important;
        padding-bottom: 2px !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #637477 !important;
        font-weight: 600 !important;
        border-radius: 6px 6px 0 0 !important;
        padding: 8px 16px !important;
        background-color: transparent !important;
        border: none !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #00666B !important;
        background-color: #EAF2F3 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #00666B !important;
        font-weight: 700 !important;
        background-color: transparent !important;
        border-bottom: 3px solid #00666B !important;
    }

    /* Progress Indicators */
    .stProgress > div > div > div > div {
        background-color: #00666B !important;
        border-radius: 4px !important;
    }
    .stProgress > div > div {
        background-color: #DCE6E7 !important;
        border-radius: 4px !important;
    }

    /* Sliders */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #00666B !important;
        border-color: #00666B !important;
    }

    /* Custom Corporate Components */
    .cynbit-header-container {
        background: linear-gradient(135deg, #FFFFFF 0%, #EAF2F3 100%);
        border: 1px solid #DCE6E7;
        border-radius: 12px;
        padding: 1.4rem 1.8rem;
        margin-bottom: 1.3rem;
        box-shadow: 0 1px 4px rgba(0, 102, 107, 0.04);
    }
    .cynbit-brand-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #EAF2F3;
        border: 1px solid #B4D5D8;
        color: #00666B;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
    }
    .cynbit-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #00666B;
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.2;
    }
    .cynbit-subtitle {
        font-size: 0.92rem;
        color: #637477;
        margin-top: 0.35rem;
        margin-bottom: 0;
        line-height: 1.4;
    }

    .cynbit-kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #DCE6E7;
        border-radius: 10px;
        padding: 1rem 0.75rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
        min-height: 122px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .cynbit-kpi-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #637477;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 3px;
    }
    .cynbit-kpi-val {
        font-size: 1.65rem;
        font-weight: 800;
        color: #00666B;
        line-height: 1.1;
        margin: 2px 0;
    }
    .cynbit-kpi-sub {
        font-size: 0.74rem;
        color: #637477;
        margin-top: 2px;
    }

    .badge-tier1 {
        background-color: #EAF2F3;
        color: #00666B;
        border: 1px solid #B4D5D8;
        padding: 4px 10px;
        border-radius: 16px;
        font-weight: 700;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-tier2 {
        background-color: #FFD9A8;
        color: #1A2021;
        border: 1px solid #F2C388;
        padding: 4px 10px;
        border-radius: 16px;
        font-weight: 700;
        font-size: 0.78rem;
        display: inline-block;
    }
    .badge-tier3 {
        background-color: #EAF2F3;
        color: #637477;
        border: 1px solid #DCE6E7;
        padding: 4px 10px;
        border-radius: 16px;
        font-weight: 700;
        font-size: 0.78rem;
        display: inline-block;
    }

    .cynbit-action-banner {
        background-color: #EAF2F3;
        border: 1px solid #B4D5D8;
        border-left: 4px solid #00666B;
        border-radius: 8px;
        padding: 0.85rem 1.15rem;
        margin-bottom: 1.25rem;
    }
    .cynbit-action-title {
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #00666B;
        letter-spacing: 0.05em;
        margin-bottom: 2px;
    }
    .cynbit-action-text {
        font-size: 0.92rem;
        color: #1A2021;
        font-weight: 500;
        margin: 0;
    }

    .cynbit-chip {
        background-color: #EAF2F3;
        color: #00666B;
        border: 1px solid #DCE6E7;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 2px 4px 2px 0;
    }
    .cynbit-section-card {
        background-color: #FFFFFF;
        border: 1px solid #DCE6E7;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize Streamlit session state variables."""
    if "current_result" not in st.session_state:
        st.session_state.current_result = None
    if "inquiry_text" not in st.session_state:
        st.session_state.inquiry_text = BENCHMARK_INQUIRIES[0]["inquiry_text"]
    if "client_name" not in st.session_state:
        st.session_state.client_name = BENCHMARK_INQUIRIES[0]["client_name"]
    if "company_name" not in st.session_state:
        st.session_state.company_name = BENCHMARK_INQUIRIES[0]["company_name"]
    if "submission_channel" not in st.session_state:
        st.session_state.submission_channel = BENCHMARK_INQUIRIES[0]["submission_channel"]
    if "selected_preset_id" not in st.session_state:
        st.session_state.selected_preset_id = BENCHMARK_INQUIRIES[0]["id"]
    if "edited_email_body" not in st.session_state:
        st.session_state.edited_email_body = ""


init_session_state()

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="padding-bottom: 0.4rem;">
        <div style="font-size: 0.7rem; font-weight: 700; color: #4B969B; text-transform: uppercase; letter-spacing: 0.08em;">Official Solutions Studio</div>
        <div style="font-size: 1.25rem; font-weight: 800; color: #00666B; letter-spacing: -0.02em; margin: 2px 0;">⚡ CYNBIT TECHNOLOGIES</div>
        <div style="font-size: 0.85rem; font-weight: 600; color: #1A2021;">AI Discovery Copilot <span style="font-size: 0.7rem; background: #B4D5D8; color: #00666B; padding: 2px 6px; border-radius: 10px; font-weight: 700;">v1.0.0</span></div>
        <div style="font-size: 0.74rem; color: #637477; margin-top: 3px;">Lead Qualification & Project Scoping Assistant</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#00666B !important; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;'>1. Benchmark Inquiries</div>", unsafe_allow_html=True)
    preset_options = {f"{item['id']}: {item['case_name']}": item["id"] for item in BENCHMARK_INQUIRIES}
    selected_preset_label = st.selectbox(
        "Load Diverse Evaluation Case:",
        options=list(preset_options.keys()),
        index=0,
        help="Select any of the 10 benchmark test inquiries covering complex AI, full-stack, cloud, edge cases, and missing data."
    )

    selected_id = preset_options[selected_preset_label]
    if selected_id != st.session_state.selected_preset_id:
        preset_data = get_benchmark_by_id(selected_id)
        if preset_data:
            st.session_state.selected_preset_id = selected_id
            st.session_state.inquiry_text = preset_data["inquiry_text"]
            st.session_state.client_name = preset_data["client_name"]
            st.session_state.company_name = preset_data["company_name"]
            st.session_state.submission_channel = preset_data["submission_channel"]
            st.session_state.current_result = None
            st.rerun()

    st.divider()

    st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#00666B !important; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;'>2. Cognitive Engine</div>", unsafe_allow_html=True)
    engine_mode = st.radio(
        "Execution Mode:",
        options=["Deterministic Local Heuristic (Offline)", "Google Gemini LLM (API Key)"],
        index=0,
        help="Deterministic mode runs locally with zero external API calls in <5ms. Gemini LLM mode connects to Google Gemini."
    )

    api_key_input = ""
    if "Gemini" in engine_mode:
        api_key_input = st.text_input(
            "Gemini API Key:",
            type="password",
            value=os.environ.get("GEMINI_API_KEY", ""),
            help="Provide your Google Gemini API key or set GEMINI_API_KEY in your environment."
        )

    st.divider()

    with st.expander("ℹ️ Grounding & Governance"):
        st.markdown("**Verified Cynbit Services (cynbit.in):**")
        for s in CynbitServiceCategory:
            if s != CynbitServiceCategory.OUT_OF_SCOPE:
                st.markdown(f"- <span style='font-size:0.85rem; color:#00666B; font-weight:600;'>{s.value}</span>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Methodology Note:**")
        st.caption(
            "Qualification scores are calculated via a transparent, auditable heuristic rubric. "
            "Unknown parameters (e.g. missing budget) are treated neutrally (65.0) rather than penalized."
        )


# ==========================================
# MAIN INTERFACE
# ==========================================
st.markdown("""
<div class="cynbit-header-container">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
        <div>
            <div class="cynbit-brand-badge">
                <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:#00666B;"></span>
                Enterprise Discovery • Verified cynbit.in Domain
            </div>
            <h1 class="cynbit-title">Cynbit AI Discovery Copilot</h1>
            <p class="cynbit-subtitle">AI-powered lead qualification, technical specification extraction, gap analysis, and discovery brief synthesis.</p>
        </div>
        <div style="text-align: right;">
            <div style="background: #FFFFFF; border: 1px solid #DCE6E7; padding: 6px 12px; border-radius: 8px; display: inline-block;">
                <div style="font-size: 0.68rem; font-weight: 700; color: #637477; text-transform: uppercase; letter-spacing: 0.04em;">Headquarters</div>
                <div style="font-size: 0.85rem; font-weight: 700; color: #00666B;">Jaipur, Rajasthan, India</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Input Card
with st.expander("📝 Incoming Customer Project Inquiry Form", expanded=(st.session_state.current_result is None)):
    col_c1, col_c2, col_c3 = st.columns([1.5, 1.5, 1.2])
    with col_c1:
        client_name = st.text_input("Client Contact Name", value=st.session_state.client_name)
    with col_c2:
        company_name = st.text_input("Client Organization", value=st.session_state.company_name)
    with col_c3:
        channel = st.selectbox(
            "Submission Channel",
            ["Web Contact Form", "Direct Email", "RFP Portal", "Referral", "LinkedIn Inbound"],
            index=0
        )

    inquiry_text = st.text_area(
        "Raw Unstructured Inquiry Text:",
        value=st.session_state.inquiry_text,
        height=130,
        help="Paste raw email or form submission text here."
    )

    run_col1, run_col2 = st.columns([1.2, 4])
    with run_col1:
        execute_button = st.button("🚀 Run Discovery Copilot", type="primary", use_container_width=True)

if execute_button or st.session_state.current_result is None:
    inq_payload = InquiryInput(
        inquiry_text=inquiry_text,
        client_name=client_name or "Prospective Client",
        company_name=company_name or "Unspecified Organization",
        submission_channel=channel
    )

    prefer_det = ("Deterministic" in engine_mode)
    engine = DiscoveryCopilotEngine(
        api_key=api_key_input if api_key_input else None,
        prefer_deterministic=prefer_det
    )

    with st.spinner("Analyzing inquiry against Cynbit service taxonomy, extracting specs, and scoring viability..."):
        pipeline_result = engine.execute_pipeline(inq_payload)
        st.session_state.current_result = pipeline_result
        st.session_state.edited_email_body = pipeline_result.response_draft.full_email_body


result: PipelineResult = st.session_state.current_result
brief = result.brief
score = brief.lead_score
specs = brief.extracted_specs
gaps = brief.missing_info

# ==========================================
# EXECUTIVE KPI METRIC CARDS
# ==========================================
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"""
    <div class="cynbit-kpi-card">
        <div class="cynbit-kpi-label">Lead Qualification</div>
        <div class="cynbit-kpi-val">{score.total_score} <span style="font-size: 0.95rem; font-weight: 500; color: #637477;">/ 100</span></div>
        <div class="cynbit-kpi-sub">Explainable Rubric</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    if "Tier 1" in score.tier:
        badge_html = f"<span class='badge-tier1'>{score.tier}</span>"
    elif "Tier 2" in score.tier:
        badge_html = f"<span class='badge-tier2'>{score.tier}</span>"
    else:
        badge_html = f"<span class='badge-tier3'>{score.tier}</span>"
    st.markdown(f"""
    <div class="cynbit-kpi-card">
        <div class="cynbit-kpi-label">Triage Priority</div>
        <div style="margin: 6px 0;">{badge_html}</div>
        <div class="cynbit-kpi-sub">Zero Auto-Rejections</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    cat_short = brief.classification.primary_category.value
    st.markdown(f"""
    <div class="cynbit-kpi-card">
        <div class="cynbit-kpi-label">Primary Vertical</div>
        <div style="font-size: 0.86rem; font-weight: 700; color: #1A2021; margin: 4px 0; line-height: 1.25;">{cat_short}</div>
        <div class="cynbit-kpi-sub">Confidence: {brief.classification.confidence * 100:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    eng_tag = "Deterministic Local" if result.engine_used == "deterministic_fallback" else "Gemini 2.5 Flash"
    eng_icon = "⚡" if result.engine_used == "deterministic_fallback" else "🤖"
    st.markdown(f"""
    <div class="cynbit-kpi-card">
        <div class="cynbit-kpi-label">Cognitive Engine</div>
        <div style="font-size: 0.90rem; font-weight: 700; color: #00666B; margin: 4px 0;">{eng_icon} {eng_tag}</div>
        <div class="cynbit-kpi-sub">Latency: {result.processing_time_ms} ms</div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    b_tag = "Stated" if specs.budget.is_specified else "Neutral / Unstated"
    b_color = "#00666B" if specs.budget.is_specified else "#637477"
    t_tag = specs.timeline.urgency_level.title() if specs.timeline.is_specified else "Unstated"
    st.markdown(f"""
    <div class="cynbit-kpi-card">
        <div class="cynbit-kpi-label">Budget & Schedule</div>
        <div style="font-size: 0.80rem; font-weight: 700; color: {b_color}; margin-top: 2px;">Budget: {b_tag}</div>
        <div style="font-size: 0.78rem; font-weight: 600; color: #1A2021;">Timeline: {t_tag}</div>
        <div class="cynbit-kpi-sub">Refinement #2 Applied</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Recommended Action Banner (REFINEMENT #3)
st.markdown(f"""
<div class="cynbit-action-banner">
    <div class="cynbit-action-title">Recommended Solutions Team Action</div>
    <div class="cynbit-action-text">{score.recommended_human_action}</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# INTERACTIVE WORKSPACE TABS
# ==========================================
tab_brief, tab_score, tab_specs, tab_questions, tab_response, tab_export = st.tabs([
    "📋 Discovery Brief",
    "📊 Explainable Scoring",
    "🔍 Extracted Specs & Gaps",
    "❓ Clarification Questions",
    "✉️ Customer Response Draft",
    "💾 Export & Reporting"
])

# -------------------------------------------------------------
# TAB 1: Discovery Brief
# -------------------------------------------------------------
with tab_brief:
    col_b1, col_b2 = st.columns([2, 1])
    with col_b1:
        st.markdown("""
        <div class="cynbit-section-card">
            <div style="font-size: 0.78rem; font-weight: 700; color: #4B969B; text-transform: uppercase; letter-spacing: 0.05em;">Section 1</div>
            <h4 style="margin: 2px 0 8px 0; color: #00666B;">Executive Discovery Summary</h4>
        </div>
        """, unsafe_allow_html=True)
        st.info(brief.executive_summary)

        st.markdown("""
        <div class="cynbit-section-card" style="margin-top: 1rem;">
            <div style="font-size: 0.78rem; font-weight: 700; color: #4B969B; text-transform: uppercase; letter-spacing: 0.05em;">Section 2</div>
            <h4 style="margin: 2px 0 8px 0; color: #00666B;">Recommended Solution Architecture</h4>
        </div>
        """, unsafe_allow_html=True)
        st.write(brief.recommended_cynbit_architecture)

        st.markdown("#### Service Classification Details")
        st.write(f"**Primary Category:** `{brief.classification.primary_category.value}`")
        st.write(f"**Classification Rationale:** {brief.classification.rationale}")
        if brief.classification.secondary_categories:
            st.write("**Secondary Disciplines Detected:**")
            for sec in brief.classification.secondary_categories:
                st.markdown(f"- <span class='cynbit-chip'>{sec.value}</span>", unsafe_allow_html=True)

    with col_b2:
        st.markdown("""
        <div class="cynbit-section-card">
            <div style="font-size: 0.78rem; font-weight: 700; color: #4B969B; text-transform: uppercase; letter-spacing: 0.05em;">Practice Offerings</div>
            <h4 style="margin: 2px 0 8px 0; color: #00666B;">Cynbit Service Deliverables</h4>
        </div>
        """, unsafe_allow_html=True)
        for item in brief.recommended_cynbit_services:
            st.markdown(f"- {item}")

        st.markdown("""
        <div class="cynbit-section-card" style="margin-top: 1rem;">
            <div style="font-size: 0.78rem; font-weight: 700; color: #4B969B; text-transform: uppercase; letter-spacing: 0.05em;">Execution Plan</div>
            <h4 style="margin: 2px 0 8px 0; color: #00666B;">Suggested Next Steps</h4>
        </div>
        """, unsafe_allow_html=True)
        for step in brief.suggested_next_steps:
            st.markdown(f"- {step}")

# -------------------------------------------------------------
# TAB 2: Explainable Scoring
# -------------------------------------------------------------
with tab_score:
    st.markdown("""
    <div class="cynbit-section-card">
        <div style="font-size: 0.78rem; font-weight: 700; color: #4B969B; text-transform: uppercase; letter-spacing: 0.05em;">Scoring Methodology</div>
        <h4 style="margin: 2px 0 4px 0; color: #00666B;">Transparent 4-Factor Heuristic Qualification Rubric</h4>
        <div style="font-size: 0.85rem; color: #637477;">Auditable multi-dimensional heuristic evaluation — NOT an uncalibrated black-box ML model.</div>
    </div>
    """, unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(f"**1. Technical Alignment (Weight: 35%) — `{score.technical_fit_score:.1f} / 100`**")
        st.progress(score.technical_fit_score / 100.0)
        st.caption(score.scoring_explanation[0] if len(score.scoring_explanation) > 0 else "")

        st.markdown(f"**2. Scope & Requirement Clarity (Weight: 30%) — `{score.scope_clarity_score:.1f} / 100`**")
        st.progress(score.scope_clarity_score / 100.0)
        st.caption(score.scoring_explanation[1] if len(score.scoring_explanation) > 1 else "")

    with col_s2:
        st.markdown(f"**3. Budget Viability (Weight: 20%) — `{score.budget_viability_score:.1f} / 100`**")
        st.progress(score.budget_viability_score / 100.0)
        st.caption(score.scoring_explanation[2] if len(score.scoring_explanation) > 2 else "")

        st.markdown(f"**4. Timeline Readiness (Weight: 15%) — `{score.timeline_readiness_score:.1f} / 100`**")
        st.progress(score.timeline_readiness_score / 100.0)
        st.caption(score.scoring_explanation[3] if len(score.scoring_explanation) > 3 else "")

    st.divider()

    st.markdown("#### 🛠️ Human-in-the-Loop Score Recalibration")
    st.caption("Solutions Architects can adjust sub-scores based on discovery discussions to see instant live tier recalculation:")

    adj_col1, adj_col2, adj_col3, adj_col4 = st.columns(4)
    with adj_col1:
        adj_tech = st.slider("Tech Alignment", 0.0, 100.0, float(score.technical_fit_score), step=5.0)
    with adj_col2:
        adj_scope = st.slider("Scope Clarity", 0.0, 100.0, float(score.scope_clarity_score), step=5.0)
    with adj_col3:
        adj_budget = st.slider("Budget Viability", 0.0, 100.0, float(score.budget_viability_score), step=5.0)
    with adj_col4:
        adj_timeline = st.slider("Timeline Readiness", 0.0, 100.0, float(score.timeline_readiness_score), step=5.0)

    recalculated = (adj_tech * 0.35) + (adj_scope * 0.30) + (adj_budget * 0.20) + (adj_timeline * 0.15)
    recalculated = round(recalculated, 1)

    rec_tier = "Tier 1: High Priority Discovery" if recalculated >= 75.0 else ("Tier 2: Discovery & Scoping Required" if recalculated >= 50.0 else "Tier 3: Exploratory / Advisory Review")
    rec_badge = f"<span class='badge-tier1'>{rec_tier}</span>" if "Tier 1" in rec_tier else (f"<span class='badge-tier2'>{rec_tier}</span>" if "Tier 2" in rec_tier else f"<span class='badge-tier3'>{rec_tier}</span>")
    
    st.markdown(f"""
    <div style="background:#EAF2F3; border:1px solid #B4D5D8; border-radius:8px; padding:0.8rem 1rem; margin-top:0.5rem; display:flex; align-items:center; justify-content:space-between;">
        <div><b>Recalculated Score:</b> <span style="font-size:1.2rem; font-weight:800; color:#00666B;">{recalculated}</span> / 100</div>
        <div><b>Adjusted Triage:</b> {rec_badge}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔬 Predictive ML vs. Heuristic Methodology (Internship Defense Guide)"):
        st.markdown("""
        **Why is this currently an explainable heuristic rather than a predictive ML model?**
        - **Cold-Start Reality:** A genuine supervised machine learning model (e.g., XGBoost, Logistic Regression, or GBDT) requires historical training labels: *Which past leads actually converted into closed-won contracts? What was their final margin and delivery success?*
        - **Risk of Premature ML:** Training a model without historical sales outcome data produces arbitrary or biased outputs. A transparent, weighted heuristic rubric provides 100% explainability, zero hallucination, and auditable governance.
        
        **What dataset would Cynbit need to train a genuine predictive ML model in the future?**
        1. **Feature Store ($X$):**
           - Extracted parameters (domain, tech stack count, stated budget range, timeline in weeks).
           - Client archetype (seed startup, SMB, enterprise, domain industry).
           - Inquiry quality metrics (token length, ambiguity count, specification density).
        2. **Ground Truth Target ($y$):**
           - Binary `converted_to_deal` (0 or 1).
           - Continuous `deal_size_usd` and `project_gross_margin_pct`.
           - `sales_cycle_days`.
        3. **Minimum Sample Size:** Approximately 300 to 1,000 verified historical CRM interactions.
        """)

# -------------------------------------------------------------
# TAB 3: Extracted Specs & Gaps
# -------------------------------------------------------------
with tab_specs:
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown("""
        <div class="cynbit-section-card">
            <div style="font-size: 0.78rem; font-weight: 700; color: #4B969B; text-transform: uppercase; letter-spacing: 0.05em;">Technical Scope</div>
            <h4 style="margin: 2px 0 8px 0; color: #00666B;">Core Technical Deliverables</h4>
        </div>
        """, unsafe_allow_html=True)
        if specs.core_requirements:
            for req in specs.core_requirements:
                st.markdown(f"- {req}")
        else:
            st.caption("No explicit deliverables detected; inquiry is highly unstructured.")

        st.markdown("""
        <div class="cynbit-section-card" style="margin-top: 1rem;">
            <div style="font-size: 0.78rem; font-weight: 700; color: #4B969B; text-transform: uppercase; letter-spacing: 0.05em;">Architecture</div>
            <h4 style="margin: 2px 0 8px 0; color: #00666B;">Detected & Suggested Tech Stack</h4>
        </div>
        """, unsafe_allow_html=True)
        if specs.suggested_tech_stack:
            chips_html = "".join([f"<span class='cynbit-chip'>{t}</span>" for t in specs.suggested_tech_stack])
            st.markdown(chips_html, unsafe_allow_html=True)
        else:
            st.caption("No specific technologies detected.")

        st.markdown("#### Client Archetype")
        st.write(f"- **Organization Scale:** `{specs.client_type.title()}`")
        st.write(f"- **Industry Domain:** `{specs.domain_industry}`")

    with col_e2:
        st.markdown("""
        <div class="cynbit-section-card">
            <div style="font-size: 0.78rem; font-weight: 700; color: #4B969B; text-transform: uppercase; letter-spacing: 0.05em;">Commercials & Constraints</div>
            <h4 style="margin: 2px 0 8px 0; color: #00666B;">Financial & Delivery Schedule Specs</h4>
        </div>
        """, unsafe_allow_html=True)
        st.write(f"**Budget Parameter:** `{specs.budget.raw_budget or 'Unspecified'}`")
        st.caption(f"Notes: {specs.budget.feasibility_notes}")

        st.write(f"**Timeline Parameter:** `{specs.timeline.raw_timeline or 'Unspecified'}` ({specs.timeline.urgency_level.title()})")
        st.caption(f"Notes: {specs.timeline.feasibility_notes}")

        st.markdown("""
        <div class="cynbit-section-card" style="margin-top: 1rem;">
            <div style="font-size: 0.78rem; font-weight: 700; color: #4B969B; text-transform: uppercase; letter-spacing: 0.05em;">Gaps & Risk Analysis</div>
            <h4 style="margin: 2px 0 8px 0; color: #00666B;">Identified Omissions & Ambiguities</h4>
        </div>
        """, unsafe_allow_html=True)
        if gaps.missing_fields:
            st.markdown("**Omitted Standard Parameters:**")
            for m in gaps.missing_fields:
                st.markdown(f"- ⚠️ {m}")
        if gaps.ambiguities:
            st.markdown("**Ambiguous Terminology:**")
            for a in gaps.ambiguities:
                st.markdown(f"- ❓ {a}")
        if gaps.technical_risks:
            st.markdown("**Identified Delivery Risks:**")
            for r in gaps.technical_risks:
                st.markdown(f"- 🚨 {r}")

# -------------------------------------------------------------
# TAB 4: Clarification Questions
# -------------------------------------------------------------
with tab_questions:
    st.markdown("""
    <div class="cynbit-section-card">
        <div style="font-size: 0.78rem; font-weight: 700; color: #4B969B; text-transform: uppercase; letter-spacing: 0.05em;">Scoping Preparation</div>
        <h4 style="margin: 2px 0 4px 0; color: #00666B;">Targeted Technical Discovery Clarification Questions</h4>
        <div style="font-size: 0.85rem; color: #637477;">Precision questions formulated to de-risk architecture and delivery during initial discovery touch.</div>
    </div>
    """, unsafe_allow_html=True)

    for q in brief.clarification_questions:
        chip_class = "cynbit-priority-chip-high" if q.priority == "high" else ("cynbit-priority-chip-medium" if q.priority == "medium" else "cynbit-priority-chip-low")
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #DCE6E7; border-radius:10px; padding:1rem; margin-bottom:0.75rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <div style="font-size:0.85rem; font-weight:700; color:#00666B;">Question {q.id} — {q.topic}</div>
                <div><span class='{chip_class}'>{q.priority.upper()} Priority</span></div>
            </div>
            <div style="font-size:0.95rem; font-weight:500; color:#1A2021; margin-bottom:6px;">{q.question}</div>
            <div style="font-size:0.8rem; color:#637477;"><b>Architectural Justification:</b> {q.justification}</div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 5: Customer Response Draft
# -------------------------------------------------------------
with tab_response:
    st.markdown("""
    <div class="cynbit-section-card">
        <div style="font-size: 0.78rem; font-weight: 700; color: #4B969B; text-transform: uppercase; letter-spacing: 0.05em;">Communication Layer</div>
        <h4 style="margin: 2px 0 4px 0; color: #00666B;">Personalized Customer Response Draft (Human-in-the-Loop)</h4>
        <div style="font-size: 0.85rem; color: #637477;">Review, edit, and approve before sending to prospective client.</div>
    </div>
    """, unsafe_allow_html=True)

    st.text_input("Subject Line:", value=result.response_draft.subject_line)
    
    edited_email = st.text_area(
        "Email Body (Editable):",
        value=st.session_state.edited_email_body,
        height=260
    )
    st.session_state.edited_email_body = edited_email

    col_btn1, col_btn2 = st.columns([1.3, 4])
    with col_btn1:
        st.download_button(
            "📋 Download Email (.txt)",
            data=edited_email,
            file_name=f"cynbit_response_{brief.inquiry_id}.txt",
            mime="text/plain",
            use_container_width=True
        )

# -------------------------------------------------------------
# TAB 6: Export & Reporting
# -------------------------------------------------------------
with tab_export:
    st.markdown("""
    <div class="cynbit-section-card">
        <div style="font-size: 0.78rem; font-weight: 700; color: #4B969B; text-transform: uppercase; letter-spacing: 0.05em;">Governance & Audit</div>
        <h4 style="margin: 2px 0 4px 0; color: #00666B;">Export & Multi-Format Audit Artifacts</h4>
        <div style="font-size: 0.85rem; color: #637477;">Generate structured outputs for CRM synchronization, team handoff, and executive presentations.</div>
    </div>
    """, unsafe_allow_html=True)

    exp_col1, exp_col2, exp_col3 = st.columns(3)

    # 1. JSON Export
    with exp_col1:
        st.markdown("""
        <div class="cynbit-section-card" style="text-align:center;">
            <div style="font-size:1.8rem; margin-bottom:4px;">📦</div>
            <div style="font-size:0.95rem; font-weight:700; color:#00666B;">Discovery Packet</div>
            <div style="font-size:0.75rem; color:#637477; margin-bottom:10px;">Full Structured JSON Schema</div>
        </div>
        """, unsafe_allow_html=True)
        json_data = result.model_dump_json(indent=2)
        st.download_button(
            "⬇️ Download JSON Data",
            data=json_data,
            file_name=f"cynbit_discovery_{brief.inquiry_id}.json",
            mime="application/json",
            use_container_width=True
        )

    # 2. Markdown Brief
    with exp_col2:
        st.markdown("""
        <div class="cynbit-section-card" style="text-align:center;">
            <div style="font-size:1.8rem; margin-bottom:4px;">📄</div>
            <div style="font-size:0.95rem; font-weight:700; color:#00666B;">Discovery Brief</div>
            <div style="font-size:0.75rem; color:#637477; margin-bottom:10px;">Formatted Markdown Document</div>
        </div>
        """, unsafe_allow_html=True)
        md_content = f"""# Cynbit Discovery Brief — {brief.inquiry_id}
**Client:** {brief.client_name} ({brief.company_name})  
**Primary Vertical:** {brief.classification.primary_category.value}  
**Lead Score:** {score.total_score}/100 ({score.tier})  
**Generated:** {brief.generated_at}  

## Executive Summary
{brief.executive_summary}

## Recommended Architecture
{brief.recommended_cynbit_architecture}

## Extracted Deliverables
""" + "\n".join([f"- {r}" for r in specs.core_requirements]) + f"""

## Clarification Questions
""" + "\n".join([f"- [{q.priority.upper()}] {q.question}" for q in brief.clarification_questions])
        
        st.download_button(
            "⬇️ Download Brief (.md)",
            data=md_content,
            file_name=f"cynbit_brief_{brief.inquiry_id}.md",
            mime="text/markdown",
            use_container_width=True
        )

    # 3. PDF Brief
    with exp_col3:
        st.markdown("""
        <div class="cynbit-section-card" style="text-align:center;">
            <div style="font-size:1.8rem; margin-bottom:4px;">📊</div>
            <div style="font-size:0.95rem; font-weight:700; color:#00666B;">Executive PDF</div>
            <div style="font-size:0.75rem; color:#637477; margin-bottom:10px;">Publication-Ready ReportLab PDF</div>
        </div>
        """, unsafe_allow_html=True)
        pdf_bytes = generate_discovery_pdf_bytes(brief)
        st.download_button(
            "⬇️ Download PDF Report",
            data=pdf_bytes,
            file_name=f"cynbit_brief_{brief.inquiry_id}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.divider()
    st.markdown("#### Live JSON Audit Trail")
    st.json(result.model_dump())
