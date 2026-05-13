"""
Streamlit Frontend for Healthcare Agentic AI System.
Chatbot UI with escalation alerts and monitoring dashboard.
"""

import streamlit as st
import requests
import uuid
from datetime import datetime

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Healthcare AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .emergency-box {
        background-color: #ff4444;
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-weight: bold;
        margin: 8px 0;
    }
    .user-msg {
        background-color: #dbeafe;
        padding: 12px 16px;
        border-radius: 12px 12px 2px 12px;
        margin: 6px 0;
        text-align: right;
    }
    .ai-msg {
        background-color: #f0fdf4;
        padding: 12px 16px;
        border-radius: 12px 12px 12px 2px;
        margin: 6px 0;
        border-left: 4px solid #16a34a;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "emergency_count" not in st.session_state:
    st.session_state.emergency_count = 0


# ── Helpers ────────────────────────────────────────────────────────────────────
def send_query(query: str):
    try:
        res = requests.post(
            f"{BACKEND_URL}/query",
            json={"query": query, "session_id": st.session_state.session_id},
            timeout=60,
        )
        if res.status_code == 200:
            return res.json(), None
        return None, f"Backend error {res.status_code}: {res.text}"
    except requests.exceptions.ConnectionError:
        return None, "❌ Cannot connect to backend. Is the FastAPI server running on port 8000?"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


def backend_status():
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=3)
        return r.status_code == 200
    except:
        return False


def get_monitoring():
    try:
        r = requests.get(f"{BACKEND_URL}/monitoring", timeout=10)
        return r.json() if r.status_code == 200 else []
    except:
        return []


def get_logs():
    try:
        r = requests.get(f"{BACKEND_URL}/logs?limit=15", timeout=10)
        return r.json() if r.status_code == 200 else []
    except:
        return []


AGENT_COLORS = {
    "Appointment Agent": "#2563eb",
    "Prescription Agent": "#7c3aed",
    "Report Explanation Agent": "#059669",
    "Insurance Agent": "#d97706",
    "Escalation Agent": "#dc2626",
}

SAMPLE_QUERIES = {
    "🗓️ Appointment": [
        "I need to schedule an appointment with a cardiologist",
        "Can I reschedule my appointment from Monday to Wednesday?",
        "How do I cancel my upcoming appointment?",
    ],
    "💊 Prescription": [
        "I need a refill for my blood pressure medication",
        "How do I request a prescription renewal?",
    ],
    "🧪 Report": [
        "My HbA1c is 7.2, what does that mean?",
        "Can you explain what eGFR means in my kidney function test?",
    ],
    "🏥 Insurance": [
        "Does my insurance cover mental health therapy?",
        "How do I file a claim for my recent hospital visit?",
    ],
    "🚨 Emergency": [
        "I have severe chest pain and my left arm is numb",
        "I can't breathe properly and feel very dizzy",
    ],
}


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏥 Healthcare AI")
    st.caption(f"Session: `{st.session_state.session_id[:8]}...`")
    st.divider()

    col1, col2 = st.columns(2)
    col1.metric("Queries", st.session_state.total_queries)
    col2.metric("🚨 Alerts", st.session_state.emergency_count)
    st.divider()

    st.subheader("💡 Sample Queries")
    for category, queries in SAMPLE_QUERIES.items():
        with st.expander(category):
            for q in queries:
                if st.button(q[:50], key=q, use_container_width=True):
                    st.session_state["prefill"] = q
                    st.rerun()

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.total_queries = 0
        st.session_state.emergency_count = 0
        st.rerun()

    st.divider()
    if backend_status():
        st.success("🟢 Backend Connected")
    else:
        st.error("🔴 Backend Offline")


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Monitoring", "📋 Logs"])


# ── Tab 1: Chat ────────────────────────────────────────────────────────────────
with tab1:
    st.title("🏥 Healthcare AI Assistant")
    st.caption("Powered by Groq Llama 3.3 70B | Multi-Agent System")

    st.info(
        "⚕️ **Disclaimer**: This AI provides general health information only. "
        "Always consult a qualified healthcare provider for medical decisions. "
        "For emergencies call **911** immediately."
    )

    # Display chat history
    if not st.session_state.chat_history:
        st.markdown("""
        <div style='text-align:center; padding:50px; color:#888;'>
            <h3>👋 Hello! I'm your Healthcare AI Assistant</h3>
            <p>Ask me about appointments, prescriptions, medical reports, or insurance.</p>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class='user-msg'>
                <strong>You</strong><br>{msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            agent = msg.get("agent", "AI")
            color = AGENT_COLORS.get(agent, "#333")

            if msg.get("is_emergency"):
                st.markdown(f"""
                <div class='emergency-box'>
                    🚨 EMERGENCY DETECTED — {agent}
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class='ai-msg'>
                <span style='background:{color};color:white;padding:2px 10px;border-radius:10px;font-size:12px;'>
                    🤖 {agent}
                </span><br><br>
                {msg['content'].replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)

            meta = f"🕐 {msg.get('timestamp', '')}"
            if msg.get("compliance_violated"):
                meta += " &nbsp;|&nbsp; ⚠️ Compliance reviewed"
            st.caption(meta)
            st.divider()

    # ── Input form ─────────────────────────────────────────────────────────────
    prefill_val = st.session_state.pop("prefill", "")

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Message",
            value=prefill_val,
            placeholder="Type your healthcare question here...",
            height=90,
            label_visibility="collapsed",
        )
        send_btn = st.form_submit_button("📤 Send", use_container_width=True, type="primary")

    if send_btn:
        if not user_input.strip():
            st.warning("Please type a message before sending.")
        else:
            # Save user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input.strip(),
            })

            with st.spinner("⏳ AI agents are processing your query..."):
                result, error = send_query(user_input.strip())

            if error:
                st.error(error)
                # Remove the user message we just added since it failed
                st.session_state.chat_history.pop()
            elif result:
                st.session_state.total_queries += 1
                if result.get("is_emergency"):
                    st.session_state.emergency_count += 1

                ts = ""
                try:
                    ts = datetime.fromisoformat(result["timestamp"]).strftime("%H:%M:%S")
                except:
                    ts = datetime.now().strftime("%H:%M:%S")

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result.get("response", "No response received."),
                    "agent": result.get("assigned_agent", "AI"),
                    "is_emergency": result.get("is_emergency", False),
                    "compliance_violated": result.get("compliance_violated", False),
                    "timestamp": ts,
                })

            st.rerun()


# ── Tab 2: Monitoring ──────────────────────────────────────────────────────────
with tab2:
    st.title("📊 Agent Monitoring Dashboard")
    if st.button("🔄 Refresh", key="refresh_monitoring"):
        st.rerun()

    data = get_monitoring()
    if not data:
        st.info("No data yet — send some queries in the Chat tab first!")
    else:
        total_q = sum(d["query_count"] for d in data)
        total_e = sum(d["escalation_count"] for d in data)
        total_v = sum(d["compliance_violation_count"] for d in data)

        c1, c2, c3 = st.columns(3)
        c1.metric("📨 Total Queries", total_q)
        c2.metric("🚨 Escalations", total_e)
        c3.metric("⚠️ Violations", total_v)
        st.divider()

        for agent in data:
            color = AGENT_COLORS.get(agent["agent_name"], "#333")
            with st.expander(f"🤖 {agent['agent_name']}  —  {agent['query_count']} queries"):
                a, b, c, d = st.columns(4)
                a.metric("Queries", agent["query_count"])
                b.metric("Escalations", agent["escalation_count"])
                c.metric("Violations", agent["compliance_violation_count"])
                d.metric("Avg Length", f"{agent['avg_response_length']} chars")


# ── Tab 3: Logs ────────────────────────────────────────────────────────────────
with tab3:
    st.title("📋 Recent Query Logs")
    if st.button("🔄 Refresh", key="refresh_logs"):
        st.rerun()

    logs = get_logs()
    if not logs:
        st.info("No logs yet — send some queries in the Chat tab first!")
    else:
        for log in logs:
            icon = "🚨" if log["escalation_status"] else "✅"
            with st.expander(
                f"{icon} [{log['timestamp'][:19]}]  {log['assigned_agent']}  —  {log['query'][:55]}..."
            ):
                c1, c2 = st.columns(2)
                c1.write(f"**Agent:** {log['assigned_agent']}")
                c1.write(f"**Emergency:** {'🚨 Yes' if log['escalation_status'] else 'No'}")
                c2.write(f"**Compliance:** {'⚠️ Violation' if log['compliance_violation'] else '✅ OK'}")
                c2.write(f"**Session:** `{log['session_id'][:8]}...`")
                st.write(f"**Query:** {log['query']}")
                if log.get("compliance_notes"):
                    st.warning(f"Notes: {log['compliance_notes']}")
