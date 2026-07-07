import streamlit as st
import requests
import pandas as pd
import plotly.express as px
# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="AEGIS AI Banking Triage",
    page_icon="🛡️",
    layout="wide"
)

# -----------------------------
# CUSTOM CSS
# -----------------------------

st.markdown("""
<style>

.main{
    background-color:#f5f7fb;
}

.block-container{
    padding-top:2rem;
}

.metric-card{
    background:white;
    padding:20px;
    border-radius:15px;
    box-shadow:0px 2px 10px rgba(0,0,0,0.08);
}

.reason-box{
    background:#eef6ff;
    padding:15px;
    border-radius:12px;
    border-left:5px solid #0078ff;
}

.success-box{
    background:#ecfff1;
    padding:15px;
    border-radius:12px;
    border-left:5px solid green;
}

.footer{
    text-align:center;
    color:gray;
    font-size:13px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------

st.title("🛡️ AEGIS")
st.subheader("AI Powered Banking Complaint Triage Agent")

st.write(
"""
Analyze banking complaints using **Gemini AI**, automatically classify priority,
perform intelligent tool calling and generate customer acknowledgements.
"""
)

st.divider()

# -----------------------------
# INPUT SECTION
# -----------------------------

left, right = st.columns([2,1])

with left:

    complaint = st.text_area(
        "📝 Customer Complaint",
        placeholder="Example:\nMoney deducted but receiver didn't receive payment.",
        height=180
    )

with right:

    customer_name = st.text_input(
        "👤 Customer Name",
        value="Customer"
    )

    transaction_id = st.text_input(
        "💳 Transaction ID",
        placeholder="TXN1002"
    )

st.divider()

# -----------------------------
# BUTTON
# -----------------------------

if st.button("🚀 Analyze Complaint", use_container_width=True):

    if complaint.strip() == "":
        st.warning("Please enter a complaint.")
        st.stop()

    payload = {

        "complaint": complaint,

        "transaction_id":
        transaction_id if transaction_id else None,

        "customer_name":
        customer_name

    }

    try:

        with st.spinner("🤖 AEGIS is thinking..."):

            response = requests.post(
                "http://127.0.0.1:8000/triage",
                json=payload,
                timeout=60
            )

        if response.status_code != 200:

            st.error(response.text)
            st.stop()

        data = response.json()

        st.success("Complaint processed successfully!")

        st.divider()

        # =====================================
        # TRIAGE SUMMARY
        # =====================================

        st.header("📌 Triage Summary")

        c1, c2, c3 = st.columns(3)

        category = data["decision"]["category"]
        priority = data["decision"]["priority"]
        tool = data["decision"]["next_tool"]

        c1.metric("Category", category)

        c2.metric("Priority", priority)

        c3.metric("Tool Selected", tool)

        # =====================================
        # REASONING
        # =====================================

        st.subheader("🧠 AI Reasoning")

        st.info(data["decision"]["reasoning"])

        st.subheader("✅ Why this Decision?")

        st.success(data["decision"]["why"])

        # =====================================
        # TRANSACTION
        # =====================================

        st.divider()

        st.header("💳 Transaction Details")

        if data["tool_output"]:

            transaction = data["tool_output"]

            if transaction["found"]:

                txn = transaction["transaction"]

                a,b,c = st.columns(3)

                a.metric("Amount", f"₹{txn['amount']}")

                b.metric("Status", txn["status"])

                c.metric("Mode", txn["payment_mode"])

                st.dataframe(
                    pd.DataFrame([txn]),
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.warning("Transaction not found.")

        else:

            st.info("No transaction lookup executed.")

        # =====================================
        # SIMILAR COMPLAINTS
        # =====================================

        st.divider()

        st.header("📚 Similar Historical Complaints")

        if len(data["similar_cases"]) > 0:

            df = pd.DataFrame(data["similar_cases"])

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No similar complaints found.")

        # =====================================
        # ACKNOWLEDGEMENT
        # =====================================

        st.divider()

        st.header("📧 Customer Acknowledgement")

        st.code(
            data["acknowledgement"],
            language="text"
        )

        # =====================================
        # REASONING TRACE
        # =====================================

        if "reasoning_trace" in data:

            st.divider()

            st.header("🧭 Agent Reasoning Trace")

            for step in data["reasoning_trace"]:

                st.write("➡️", step)

    except requests.exceptions.ConnectionError:

        st.error(
            "Unable to connect to FastAPI.\n\n"
            "Start the backend using:\n\n"
            "uvicorn app.main:app --reload"
        )

    except requests.exceptions.Timeout:

        st.error("Request timed out.")

    except Exception as e:

        st.exception(e)

# -----------------------------
# FOOTER
# -----------------------------

st.divider()

st.markdown(
"""
<div class="footer">

<b>AEGIS AI Banking Triage Agent</b><br>

Built using FastAPI • Gemini AI • Streamlit • Scikit-Learn

</div>
""",
unsafe_allow_html=True
)