"""
AEGIS — AI Banking Complaint Triage Agent
Streamlit Dashboard (Full Featured Version)

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

PRIORITY_COLORS = {
    "P1": {"bg": "#fde8e8", "border": "#e53e3e", "text": "#c53030", "label": "Critical"},
    "P2": {"bg": "#fff6e5", "border": "#dd8b00", "text": "#b06e00", "label": "High"},
    "P3": {"bg": "#e9f9ee", "border": "#22a55a", "text": "#178a49", "label": "Normal"},
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

/* ---------- Page background ---------- */
.stApp {
    background-color: var(--aegis-bg);
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* ---------- Force readable, consistent inputs regardless of ---------- */
/* ---------- the viewer's light/dark browser or OS setting  ---------- */

.stTextArea textarea,
.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--aegis-surface) !important;
    color: var(--aegis-text) !important;
    border: 1.5px solid var(--aegis-border) !important;
    border-radius: 10px !important;
}

.stTextArea textarea::placeholder,
.stTextInput input::placeholder {
    color: #9aa2b5 !important;
    opacity: 1 !important;
}

.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: var(--aegis-accent) !important;
    box-shadow: 0 0 0 1px var(--aegis-accent) !important;
}

/* Widget labels (Customer Complaint, Customer Name, etc.) */
.stTextArea label,
.stTextInput label,
.stSelectbox label,
[data-testid="stWidgetLabel"] p {
    color: var(--aegis-text) !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    opacity: 1 !important;
}

/* Buttons */
.stButton button {
    border-radius: 10px !important;
    font-weight: 600 !important;
}

.stButton button[kind="primary"] {
    background-color: var(--aegis-accent) !important;
    border: none !important;
}

.stButton button[kind="primary"]:hover {
    background-color: #1d4ed8 !important;
}

/* Header banner */
.aegis-header {
    background: linear-gradient(135deg, #0f2545 0%, #14335e 55%, #2563eb 130%);
    padding: 28px 32px;
    border-radius: 18px;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0px 8px 24px rgba(15, 37, 69, 0.25);
}

.aegis-header h1 {
    margin: 0;
    font-size: 2rem;
    color: white;
}

.aegis-header p {
    margin-top: 6px;
    color: #cfe0ff;
    font-size: 0.95rem;
}

/* Generic metric card */
.metric-card {
    background: var(--aegis-surface);
    padding: 18px 20px;
    border-radius: 14px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.06);
    border: 1px solid var(--aegis-border);
    height: 100%;
}

.metric-card .label {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--aegis-muted);
    margin-bottom: 6px;
}

.metric-card .value {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--aegis-text);
}

/* Priority badge */
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

/* Reasoning / info boxes */
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

/* Section headers */
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--aegis-text);
    margin-top: 0.5rem;
    margin-bottom: 0.6rem;
}

/* ---------- Sidebar: light surface, dark text, accent header ---------- */
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

# =========================================================
# HELPERS
# =========================================================


def metric_card(label: str, value: str, col):
    col.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def priority_badge(priority: str):
    style = PRIORITY_COLORS.get(
        priority, {"bg": "#eef0f5", "border": "#8892a6", "text": "#4a5468", "label": priority}
    )
    st.markdown(
        f"""
        <div class="priority-badge" style="background:{style['bg']};
             border-color:{style['border']}; color:{style['text']};">
            🔴 {priority} — {style['label']}
        </div>
        """
        if priority == "P1"
        else f"""
        <div class="priority-badge" style="background:{style['bg']};
             border-color:{style['border']}; color:{style['text']};">
            {"🟠" if priority == "P2" else "🟢"} {priority} — {style['label']}
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    color_map = {"P1": "#e53e3e", "P2": "#dd8b00", "P3": "#22a55a"}
    fig = px.pie(
        df,
        names="Priority",
        values="Count",
        color="Priority",
        color_discrete_map=color_map,
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
    st.markdown(f"**Total analyzed:** {total}")

    if total > 0:
        p1_count = sum(1 for h in st.session_state.history if h["data"]["decision"]["priority"] == "P1")
        st.markdown(f"**Critical (P1):** {p1_count}")

        pie = history_priority_chart()
        if pie:
            st.plotly_chart(pie, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    st.markdown("### 🕘 Recent Analyses")
    if not st.session_state.history:
        st.caption("No complaints analyzed yet.")
    else:
        for i, entry in enumerate(reversed(st.session_state.history[-8:])):
            idx = len(st.session_state.history) - 1 - i
            snippet = entry["complaint"][:50] + ("…" if len(entry["complaint"]) > 50 else "")
            pr = entry["data"]["decision"]["priority"]
            st.markdown(
                f"""
                <div class="history-item">
                    <b>{pr}</b> · {entry['timestamp']}<br>
                    {snippet}
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
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

    st.success("Complaint processed successfully.")
    st.divider()

    # -----------------------------------------------------
    # TRIAGE SUMMARY
    # -----------------------------------------------------
    st.markdown('<div class="section-title">📌 Triage Summary</div>', unsafe_allow_html=True)

    top_left, top_right = st.columns([1, 2])
    with top_left:
        priority_badge(decision.get("priority", "P3"))

    c1, c2, c3, c4 = st.columns(4)
    metric_card("Category", decision.get("category", "—"), c1)
    metric_card("Priority", decision.get("priority", "—"), c2)
    metric_card("Tool Selected", decision.get("next_tool", "—"), c3)
    metric_card("Analyzed At", datetime.now().strftime("%H:%M:%S"), c4)

    st.write("")

    # -----------------------------------------------------
    # REASONING
    # -----------------------------------------------------
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

    st.divider()

    # -----------------------------------------------------
    # TRANSACTION DETAILS
    # -----------------------------------------------------
    st.markdown('<div class="section-title">💳 Transaction Details</div>', unsafe_allow_html=True)

    tool_output = data.get("tool_output")
    if tool_output:
        if tool_output.get("found"):
            txn = tool_output["transaction"]

            a, b, c = st.columns(3)
            metric_card("Amount", f"₹{txn.get('amount', '—')}", a)
            metric_card("Status", txn.get("status", "—"), b)
            metric_card("Mode", txn.get("payment_mode", "—"), c)

            st.write("")
            st.dataframe(pd.DataFrame([txn]), use_container_width=True, hide_index=True)
        else:
            st.warning("Transaction not found for the provided ID.")
    else:
        st.info("No transaction lookup was executed for this complaint.")

    st.divider()

    # -----------------------------------------------------
    # SIMILAR COMPLAINTS
    # -----------------------------------------------------
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
                color_discrete_map={"P1": "#e53e3e", "P2": "#dd8b00", "P3": "#22a55a"},
                labels={"similarity_score": "Similarity Score", "category": "Category"},
            )
            bar_fig.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(bar_fig, use_container_width=True)
    else:
        st.info("No similar complaints found in the historical dataset.")

    st.divider()

    # -----------------------------------------------------
    # ACKNOWLEDGEMENT
    # -----------------------------------------------------
    st.markdown('<div class="section-title">📧 Customer Acknowledgement</div>', unsafe_allow_html=True)
    st.code(data.get("acknowledgement", "No acknowledgement generated."), language="text")

    # -----------------------------------------------------
    # REASONING TRACE
    # -----------------------------------------------------
    if data.get("reasoning_trace"):
        st.divider()
        st.markdown('<div class="section-title">🧭 Agent Reasoning Trace</div>', unsafe_allow_html=True)
        for i, step in enumerate(data["reasoning_trace"], start=1):
            st.write(f"**{i}.** ➡️ {step}")

    st.divider()

    # -----------------------------------------------------
    # SESSION ANALYTICS (from history)
    # -----------------------------------------------------
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
