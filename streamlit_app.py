"""
AEGIS — AI Banking Complaint Triage Agent
Streamlit Dashboard (Enhanced Version)

Run with:
    streamlit run streamlit_app.py
"""

import json
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AEGIS | AI Banking Triage",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CONSTANTS
# =========================================================

# NOTE: the backend (schemas.py / prompts.py) defines priority as
# P0 = Critical, P1 = High, P2 = Normal. Keep this in sync with that —
# a mismatch here means the badge silently falls back to a default
# style instead of correctly flagging a critical complaint.
PRIORITY_COLORS = {
    "P0": {"bg": "#fde8e8", "border": "#e53e3e", "text": "#c53030", "label": "Critical", "dot": "🔴"},
    "P1": {"bg": "#fff6e5", "border": "#dd8b00", "text": "#b06e00", "label": "High", "dot": "🟠"},
    "P2": {"bg": "#e9f9ee", "border": "#22a55a", "text": "#178a49", "label": "Normal", "dot": "🟢"},
}
PRIORITY_ORDER = ["P0", "P1", "P2"]
PRIORITY_CHART_COLORS = {"P0": "#e53e3e", "P1": "#dd8b00", "P2": "#22a55a"}

CATEGORY_ICONS = {
    "UPI": "📲",
    "CARD": "💳",
    "ACCOUNT": "🏦",
    "LOAN": "📄",
    "FRAUD": "🚨",
    "KYC": "🪪",
    "NET BANKING": "💻",
}

TOOL_ICONS = {
    "transaction_lookup": "🔍",
    "similar_complaint_search": "📚",
    "generate_acknowledgement": "✉️",
}

DEFAULT_API_URL = "http://127.0.0.1:8000"

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

:root {
    --aegis-bg: #f4f6fb;
    --aegis-surface: #ffffff;
    --aegis-border: #e3e7f0;
    --aegis-text: #1a2138;
    --aegis-muted: #6b7488;
    --aegis-accent: #2563eb;
    --aegis-accent-dark: #14335e;
}

.stApp {
    background-color: var(--aegis-bg);
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* ---------- Inputs ---------- */
.stTextArea textarea,
.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--aegis-surface) !important;
    color: var(--aegis-text) !important;
    border: 1.5px solid var(--aegis-border) !important;
    border-radius: 10px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.stTextArea textarea::placeholder,
.stTextInput input::placeholder {
    color: #9aa2b5 !important;
    opacity: 1 !important;
}

.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: var(--aegis-accent) !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
}

.stTextArea label,
.stTextInput label,
.stSelectbox label,
[data-testid="stWidgetLabel"] p {
    color: var(--aegis-text) !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    opacity: 1 !important;
}

/* ---------- Buttons ---------- */
.stButton button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: transform 0.12s ease, box-shadow 0.12s ease;
}

.stButton button[kind="primary"] {
    background-color: var(--aegis-accent) !important;
    border: none !important;
}

.stButton button[kind="primary"]:hover {
    background-color: #1d4ed8 !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
}

/* ---------- Animated header banner ---------- */
@keyframes aegisGradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.aegis-header {
    background: linear-gradient(120deg, #0f2545, #14335e, #2563eb, #14335e, #0f2545);
    background-size: 300% 300%;
    animation: aegisGradientShift 12s ease infinite;
    padding: 30px 32px;
    border-radius: 18px;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0px 8px 24px rgba(15, 37, 69, 0.25);
    position: relative;
    overflow: hidden;
}

.aegis-header h1 {
    margin: 0;
    font-size: 2.1rem;
    color: white;
    display: flex;
    align-items: center;
    gap: 10px;
}

.aegis-header p {
    margin-top: 6px;
    color: #cfe0ff;
    font-size: 0.95rem;
}

.aegis-header .badge-strip {
    margin-top: 14px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.aegis-header .mini-badge {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.25);
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    color: #e7efff;
}

/* ---------- Metric card ---------- */
.metric-card {
    background: var(--aegis-surface);
    padding: 18px 20px;
    border-radius: 14px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.06);
    border: 1px solid var(--aegis-border);
    height: 100%;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0px 10px 22px rgba(20, 51, 94, 0.12);
}

.metric-card .label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--aegis-muted);
    margin-bottom: 6px;
}

.metric-card .value {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--aegis-text);
}

/* ---------- Priority badge ---------- */
.priority-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 18px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 1rem;
    border: 1.5px solid;
}

@keyframes aegisPulse {
    0%   { box-shadow: 0 0 0 0 rgba(229, 62, 62, 0.45); }
    70%  { box-shadow: 0 0 0 10px rgba(229, 62, 62, 0); }
    100% { box-shadow: 0 0 0 0 rgba(229, 62, 62, 0); }
}

.priority-badge.pulse {
    animation: aegisPulse 1.8s infinite;
}

/* ---------- Reasoning / info boxes ---------- */
.reason-box {
    background: #eef6ff;
    padding: 16px 18px;
    border-radius: 12px;
    border-left: 5px solid var(--aegis-accent);
    color: var(--aegis-text);
    line-height: 1.5;
}

.success-box {
    background: #ecfff1;
    padding: 16px 18px;
    border-radius: 12px;
    border-left: 5px solid #22a55a;
    color: var(--aegis-text);
    line-height: 1.5;
}

/* ---------- Section headers ---------- */
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--aegis-text);
    margin-top: 0.5rem;
    margin-bottom: 0.6rem;
}

/* ---------- Pipeline flow strip ---------- */
.pipeline-wrap {
    display: flex;
    align-items: stretch;
    gap: 6px;
    margin: 8px 0 4px 0;
}

.pipeline-step {
    flex: 1;
    background: var(--aegis-surface);
    border: 1.5px solid var(--aegis-border);
    border-radius: 12px;
    padding: 14px 10px;
    text-align: center;
    font-size: 0.85rem;
    color: var(--aegis-muted);
    font-weight: 600;
}

.pipeline-step.active {
    border-color: var(--aegis-accent);
    background: #eef6ff;
    color: var(--aegis-accent-dark);
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15);
}

.pipeline-arrow {
    align-self: center;
    color: var(--aegis-muted);
    font-size: 1.1rem;
    padding: 0 2px;
}

/* ---------- Reasoning trace timeline ---------- */
.trace-wrap {
    position: relative;
    padding-left: 26px;
}

.trace-wrap::before {
    content: "";
    position: absolute;
    left: 9px;
    top: 6px;
    bottom: 6px;
    width: 2px;
    background: linear-gradient(180deg, var(--aegis-accent), #b8cdf5);
}

.trace-step {
    position: relative;
    margin-bottom: 16px;
    background: var(--aegis-surface);
    border: 1px solid var(--aegis-border);
    border-radius: 10px;
    padding: 10px 14px;
    color: var(--aegis-text);
    font-size: 0.92rem;
    line-height: 1.45;
}

.trace-step::before {
    content: "";
    position: absolute;
    left: -22px;
    top: 16px;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--aegis-accent);
    border: 2px solid white;
    box-shadow: 0 0 0 2px var(--aegis-accent);
}

.trace-step .trace-index {
    display: inline-block;
    background: var(--aegis-accent);
    color: white;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 1px 8px;
    border-radius: 999px;
    margin-right: 8px;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background-color: #eef1f8;
    border-right: 1px solid var(--aegis-border);
}

section[data-testid="stSidebar"] * {
    color: var(--aegis-text) !important;
}

section[data-testid="stSidebar"] .stTextInput input {
    background-color: var(--aegis-surface) !important;
    border: 1.5px solid var(--aegis-border) !important;
}

section[data-testid="stSidebar"] hr {
    border-color: var(--aegis-border) !important;
}

.history-item {
    background: var(--aegis-surface);
    padding: 10px 12px;
    border-radius: 10px;
    margin-bottom: 8px;
    font-size: 0.82rem;
    border: 1px solid var(--aegis-border);
    box-shadow: 0px 1px 4px rgba(0,0,0,0.04);
    transition: transform 0.12s ease;
}

.history-item:hover {
    transform: translateX(2px);
}

.footer {
    text-align: center;
    color: var(--aegis-muted);
    font-size: 13px;
    margin-top: 2rem;
}

</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# SESSION STATE
# =========================================================

if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: {timestamp, complaint, data}

if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API_URL

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_priority_toasted" not in st.session_state:
    st.session_state.last_priority_toasted = None

# =========================================================
# HELPERS
# =========================================================


def metric_card(label: str, value: str, col, icon: str = ""):
    prefix = f"{icon} " if icon else ""
    col.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{prefix}{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def priority_badge(priority: str):
    style = PRIORITY_COLORS.get(
        priority,
        {"bg": "#eef0f5", "border": "#8892a6", "text": "#4a5468", "label": priority, "dot": "⚪"},
    )
    pulse_class = "pulse" if priority == "P0" else ""
    st.markdown(
        f"""
        <div class="priority-badge {pulse_class}" style="background:{style['bg']};
             border-color:{style['border']}; color:{style['text']};">
            {style['dot']} {priority} — {style['label']}
        </div>
        """,
        unsafe_allow_html=True,
    )


def pipeline_flow(next_tool: str):
    steps = [
        ("📝", "Complaint\nReceived"),
        ("🧠", "Classified"),
        (TOOL_ICONS.get(next_tool, "🔧"), (next_tool or "tool").replace("_", " ").title()),
        ("✅", "Decision\nOutput"),
    ]
    html_parts = ['<div class="pipeline-wrap">']
    for i, (icon, label) in enumerate(steps):
        active_class = "active" if i in (2, 3) else ""
        html_parts.append(
            f'<div class="pipeline-step {active_class}">{icon}<br>{label}</div>'
        )
        if i < len(steps) - 1:
            html_parts.append('<div class="pipeline-arrow">➜</div>')
    html_parts.append("</div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)


def reasoning_trace_timeline(trace: list):
    html_parts = ['<div class="trace-wrap">']
    for i, step in enumerate(trace, start=1):
        html_parts.append(
            f'<div class="trace-step"><span class="trace-index">{i}</span>{step}</div>'
        )
    html_parts.append("</div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)


def build_gauge(score: float, title: str = "Similarity Confidence"):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=round(score * 100, 1),
            number={"suffix": "%"},
            title={"text": title, "font": {"size": 14}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#0078ff"},
                "steps": [
                    {"range": [0, 40], "color": "#fde8e8"},
                    {"range": [40, 70], "color": "#fff6e5"},
                    {"range": [70, 100], "color": "#e9f9ee"},
                ],
            },
        )
    )
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=10))
    return fig


def history_priority_chart():
    if not st.session_state.history:
        return None
    counts = pd.Series(
        [h["data"]["decision"]["priority"] for h in st.session_state.history]
    ).value_counts()
    df = counts.reset_index()
    df.columns = ["Priority", "Count"]
    fig = px.pie(
        df,
        names="Priority",
        values="Count",
        color="Priority",
        color_discrete_map=PRIORITY_CHART_COLORS,
        hole=0.55,
    )
    fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
    return fig


def history_category_chart():
    if not st.session_state.history:
        return None
    counts = pd.Series(
        [h["data"]["decision"]["category"] for h in st.session_state.history]
    ).value_counts()
    df = counts.reset_index()
    df.columns = ["Category", "Count"]
    fig = px.bar(df, x="Category", y="Count", color="Category", text="Count")
    fig.update_layout(
        height=260, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, xaxis_title="", yaxis_title=""
    )
    return fig


def history_timeline_chart():
    if len(st.session_state.history) < 2:
        return None
    df = pd.DataFrame(
        [
            {
                "time": h["timestamp"],
                "priority": h["data"]["decision"]["priority"],
                "category": h["data"]["decision"]["category"],
            }
            for h in st.session_state.history
        ]
    )
    df["order"] = range(1, len(df) + 1)
    fig = px.scatter(
        df,
        x="order",
        y="priority",
        color="priority",
        symbol="category",
        color_discrete_map=PRIORITY_CHART_COLORS,
        category_orders={"priority": PRIORITY_ORDER},
        hover_data=["time", "category"],
    )
    fig.update_traces(marker=dict(size=14, line=dict(width=1, color="white")))
    fig.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Complaint order (this session)",
        yaxis_title="",
    )
    return fig


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("## 🛡️ AEGIS")
    st.caption("AI Banking Complaint Triage Agent")

    st.divider()

    st.markdown("### ⚙️ Settings")
    st.session_state.api_url = st.text_input(
        "Backend API URL",
        value=st.session_state.api_url,
        help="FastAPI base URL, e.g. http://127.0.0.1:8000",
    )

    st.divider()

    st.markdown("### 📊 Session Stats")
    total = len(st.session_state.history)

    s1, s2 = st.columns(2)
    s1.metric("Analyzed", total)
    p0_count = sum(1 for h in st.session_state.history if h["data"]["decision"]["priority"] == "P0")
    s2.metric("Critical (P0)", p0_count)

    if total > 0:
        pie = history_priority_chart()
        if pie:
            st.plotly_chart(pie, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    st.markdown("### 🕘 Recent Analyses")
    if not st.session_state.history:
        st.caption("No complaints analyzed yet.")
    else:
        for i, entry in enumerate(reversed(st.session_state.history[-8:])):
            snippet = entry["complaint"][:50] + ("…" if len(entry["complaint"]) > 50 else "")
            pr = entry["data"]["decision"]["priority"]
            dot = PRIORITY_COLORS.get(pr, {}).get("dot", "⚪")
            cat = entry["data"]["decision"].get("category", "")
            cat_icon = CATEGORY_ICONS.get(cat, "")
            st.markdown(
                f"""
                <div class="history-item">
                    {dot} <b>{pr}</b> · {cat_icon} {cat} · {entry['timestamp']}<br>
                    {snippet}
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.session_state.last_priority_toasted = None
            st.rerun()

# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="aegis-header">
        <h1>🛡️ AEGIS</h1>
        <p>AI-powered banking complaint triage — classification, prioritization,
        tool execution, and explainable decisions in one workflow.</p>
        <div class="badge-strip">
            <span class="mini-badge">⚡ Gemini-powered</span>
            <span class="mini-badge">🔎 Full reasoning trace</span>
            <span class="mini-badge">🧩 Auto tool selection</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# INPUT FORM
# =========================================================

left, right = st.columns([2, 1])

with left:
    complaint = st.text_area(
        "📝 Customer Complaint",
        placeholder="Example:\nMoney deducted but receiver didn't receive payment.",
        height=180,
    )

with right:
    customer_name = st.text_input("👤 Customer Name", value="Customer")
    transaction_id = st.text_input("💳 Transaction ID", placeholder="TXN1002")
    st.write("")
    analyze_clicked = st.button("🚀 Analyze Complaint", use_container_width=True, type="primary")

st.divider()

# =========================================================
# ANALYSIS
# =========================================================

if analyze_clicked:
    if complaint.strip() == "":
        st.warning("Please enter a complaint before analyzing.")
        st.stop()

    payload = {
        "complaint": complaint,
        "transaction_id": transaction_id if transaction_id else None,
        "customer_name": customer_name,
    }

    try:
        with st.spinner("🤖 AEGIS is analyzing the complaint..."):
            response = requests.post(
                f"{st.session_state.api_url}/triage",
                json=payload,
                timeout=60,
            )

        if response.status_code != 200:
            st.error(f"Backend returned an error ({response.status_code}):\n\n{response.text}")
            st.stop()

        try:
            data = response.json()
        except ValueError:
            st.error("The backend did not return valid JSON. Check the API response format.")
            st.stop()

        if "decision" not in data:
            st.error("Malformed response: missing 'decision' field.")
            st.stop()

        st.session_state.last_result = data
        st.session_state.history.append(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "complaint": complaint,
                "data": data,
            }
        )

        priority = data["decision"].get("priority")
        if priority == "P0":
            st.toast("🚨 Critical complaint detected — immediate attention required!", icon="🚨")
        elif priority == "P1":
            st.toast("⚠️ High priority complaint logged.", icon="⚠️")
        else:
            st.toast("✅ Complaint triaged successfully.", icon="✅")

    except requests.exceptions.ConnectionError:
        st.error(
            "**Unable to connect to the FastAPI backend.**\n\n"
            f"Tried: `{st.session_state.api_url}/triage`\n\n"
            "Make sure it's running:\n```bash\nuvicorn app.main:app --reload\n```"
        )
        st.stop()

    except requests.exceptions.Timeout:
        st.error("The request timed out. The backend may be slow to respond or unreachable.")
        st.stop()

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        st.stop()

    except Exception as e:
        st.exception(e)
        st.stop()

# =========================================================
# RESULTS DISPLAY
# =========================================================

if st.session_state.last_result:

    data = st.session_state.last_result
    decision = data["decision"]
    category = decision.get("category", "—")
    priority = decision.get("priority", "P2")
    next_tool = decision.get("next_tool", "")
    cat_icon = CATEGORY_ICONS.get(category, "🏷️")

    st.success("Complaint processed successfully.")

    tab_overview, tab_reasoning, tab_data, tab_trace, tab_analytics = st.tabs(
        ["📌 Overview", "🧠 Reasoning", "💳 Transaction & Similar Cases", "🧭 Trace", "📈 Analytics"]
    )

    # -----------------------------------------------------
    # OVERVIEW TAB
    # -----------------------------------------------------
    with tab_overview:
        st.markdown('<div class="section-title">📌 Triage Summary</div>', unsafe_allow_html=True)

        top_left, top_right = st.columns([1, 2])
        with top_left:
            priority_badge(priority)

        c1, c2, c3, c4 = st.columns(4)
        metric_card("Category", category, c1, icon=cat_icon)
        metric_card("Priority", PRIORITY_COLORS.get(priority, {}).get("label", priority), c2,
                     icon=PRIORITY_COLORS.get(priority, {}).get("dot", ""))
        metric_card("Tool Selected", (next_tool or "—").replace("_", " ").title(), c3,
                     icon=TOOL_ICONS.get(next_tool, "🔧"))
        metric_card("Analyzed At", datetime.now().strftime("%H:%M:%S"), c4, icon="⏱️")

        st.write("")
        st.markdown('<div class="section-title">🔗 Decision Pipeline</div>', unsafe_allow_html=True)
        pipeline_flow(next_tool)

        st.write("")
        st.markdown('<div class="section-title">📧 Customer Acknowledgement</div>', unsafe_allow_html=True)
        st.code(data.get("acknowledgement", "No acknowledgement generated."), language="text")

    # -----------------------------------------------------
    # REASONING TAB
    # -----------------------------------------------------
    with tab_reasoning:
        r1, r2 = st.columns(2)
        with r1:
            st.markdown('<div class="section-title">🧠 AI Reasoning</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="reason-box">{decision.get("reasoning", "No reasoning provided.")}</div>',
                unsafe_allow_html=True,
            )
        with r2:
            st.markdown('<div class="section-title">✅ Why This Decision?</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="success-box">{decision.get("why", "No explanation provided.")}</div>',
                unsafe_allow_html=True,
            )

    # -----------------------------------------------------
    # TRANSACTION + SIMILAR CASES TAB
    # -----------------------------------------------------
    with tab_data:
        st.markdown('<div class="section-title">💳 Transaction Details</div>', unsafe_allow_html=True)

        tool_output = data.get("tool_output")
        if tool_output:
            if tool_output.get("found"):
                txn = tool_output["transaction"]

                a, b, c = st.columns(3)
                metric_card("Amount", f"₹{txn.get('amount', '—')}", a, icon="💰")
                metric_card("Status", txn.get("status", "—"), b, icon="📶")
                metric_card("Mode", txn.get("payment_mode", "—"), c, icon="🔁")

                st.write("")
                st.dataframe(pd.DataFrame([txn]), use_container_width=True, hide_index=True)
            else:
                st.warning("Transaction not found for the provided ID.")
        else:
            st.info("No transaction lookup was executed for this complaint.")

        st.divider()

        st.markdown('<div class="section-title">📚 Similar Historical Complaints</div>', unsafe_allow_html=True)

        similar_cases = data.get("similar_cases", [])
        if similar_cases:
            df_sim = pd.DataFrame(similar_cases)

            sim_left, sim_right = st.columns([2, 1])
            with sim_left:
                st.dataframe(df_sim, use_container_width=True, hide_index=True)

            with sim_right:
                if "similarity_score" in df_sim.columns:
                    avg_score = float(df_sim["similarity_score"].mean())
                    st.plotly_chart(
                        build_gauge(avg_score, "Avg. Similarity Score"),
                        use_container_width=True,
                        config={"displayModeBar": False},
                    )

            if {"similarity_score", "category"}.issubset(df_sim.columns):
                bar_fig = px.bar(
                    df_sim.sort_values("similarity_score", ascending=True),
                    x="similarity_score",
                    y="category",
                    orientation="h",
                    color="priority" if "priority" in df_sim.columns else None,
                    color_discrete_map=PRIORITY_CHART_COLORS,
                    labels={"similarity_score": "Similarity Score", "category": "Category"},
                )
                bar_fig.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=10))
                st.plotly_chart(bar_fig, use_container_width=True)
        else:
            st.info("No similar complaints found in the historical dataset.")

    # -----------------------------------------------------
    # REASONING TRACE TAB
    # -----------------------------------------------------
    with tab_trace:
        st.markdown('<div class="section-title">🧭 Agent Reasoning Trace</div>', unsafe_allow_html=True)
        trace = data.get("reasoning_trace") or []
        if trace:
            reasoning_trace_timeline(trace)
        else:
            st.info("No reasoning trace was returned for this decision.")

    # -----------------------------------------------------
    # ANALYTICS TAB
    # -----------------------------------------------------
    with tab_analytics:
        if len(st.session_state.history) > 1:
            st.markdown('<div class="section-title">📈 Session Analytics</div>', unsafe_allow_html=True)
            chart_left, chart_right = st.columns(2)

            with chart_left:
                st.caption("Priority Distribution")
                pie = history_priority_chart()
                if pie:
                    st.plotly_chart(pie, use_container_width=True)

            with chart_right:
                st.caption("Category Distribution")
                bar = history_category_chart()
                if bar:
                    st.plotly_chart(bar, use_container_width=True)

            st.caption("Priority Over Time (this session)")
            timeline = history_timeline_chart()
            if timeline:
                st.plotly_chart(timeline, use_container_width=True)
        else:
            st.info("Analyze at least two complaints in this session to unlock analytics.")

    st.divider()

    # -----------------------------------------------------
    # DOWNLOAD REPORT
    # -----------------------------------------------------
    dl_col1, dl_col2 = st.columns([1, 3])
    with dl_col1:
        report = {
            "generated_at": datetime.now().isoformat(),
            "customer_name": customer_name,
            "complaint": complaint,
            "result": data,
        }
        st.download_button(
            label="📥 Download Report (JSON)",
            data=json.dumps(report, indent=2),
            file_name=f"aegis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )

else:
    st.info("👆 Enter a complaint above and click **Analyze Complaint** to get started.")

# =========================================================
# FOOTER
# =========================================================

st.divider()
st.markdown(
    """
    <div class="footer">
        <b>AEGIS AI Banking Triage Agent</b><br>
        Built using FastAPI • Gemini AI • Streamlit • Scikit-learn • Plotly
    </div>
    """,
    unsafe_allow_html=True,
)
