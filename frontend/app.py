"""
Streamlit Frontend for Healthcare Agentic AI System.
Chatbot UI with escalation alerts and monitoring dashboard.
"""

import streamlit as st
import requests
import uuid
from datetime import datetime

BACKEND_URL = "https://healthcare-agentic-ai.up.railway.app"

st.set_page_config(
    page_title="Healthcare AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    /* Hide Streamlit components */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    [data-testid="stSidebar"] {display: none;}
    
    /* General Theme */
    .stApp {
        background-color: #050505;
        color: #e0e0e0;
    }
    
    /* Nav bar styling via column buttons */
    div[data-testid="column"] button {
        width: 100%;
        background-color: #000000;
        color: #00d2ff;
        border: 1px solid #0055ff;
        padding: 12px;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
        font-size: 16px;
    }
    div[data-testid="column"] button:hover {
        background-color: #0055ff;
        color: white;
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0, 85, 255, 0.4);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00d2ff !important;
        text-align: center;
    }
    
    /* Centered Content */
    .centered-card {
        background-color: #111;
        padding: 40px;
        border-radius: 15px;
        border: 1px solid #004080;
        box-shadow: 0 8px 32px rgba(0, 85, 255, 0.1);
        text-align: center;
        margin: 20px auto;
        max-width: 800px;
    }
    
    /* Metrics */
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin-top: 20px;
    }
    .metric-box {
        background: #000;
        border: 1px solid #0055ff;
        border-radius: 10px;
        padding: 20px;
        width: 45%;
    }
    .metric-val {
        font-size: 3rem;
        font-weight: bold;
        color: #00d2ff;
    }
    .metric-label {
        font-size: 1.2rem;
        color: #aaa;
    }
    
    /* WhatsApp / ChatGPT style chat bubbles */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
    }
    .user-msg {
        background-color: #0055ff;
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 15px 0 15px auto;
        width: fit-content;
        max-width: 75%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        font-size: 16px;
        line-height: 1.5;
    }
    .ai-msg {
        background-color: #1a1a1a;
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 15px auto 15px 0;
        width: fit-content;
        max-width: 75%;
        border: 1px solid #0055ff;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        font-size: 16px;
        line-height: 1.5;
    }
    .emergency-box {
        background-color: #ff0033;
        color: white;
        padding: 15px 25px;
        border-radius: 12px;
        font-weight: bold;
        margin: 15px auto;
        text-align: center;
        width: fit-content;
        max-width: 75%;
        animation: pulse 1.5s infinite;
        box-shadow: 0 0 15px rgba(255,0,51,0.5);
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 51, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(255, 0, 51, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 51, 0); }
    }
    
    .agent-badge {
        background: #004080;
        color: #00d2ff;
        padding: 3px 12px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: bold;
        display: block;
        width: fit-content;
        margin: 0 auto 10px auto;
        text-align: center;
    }
    
    .timestamp {
        font-size: 11px;
        color: #666;
        margin-top: 5px;
        text-align: right;
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
if "page" not in st.session_state:
    st.session_state.page = "Home"

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
    "Appointment": [
        "I need to schedule an appointment with a cardiologist",
        "Can I reschedule my appointment from Monday to Wednesday?",
        "How do I cancel my upcoming appointment?",
    ],
    "Prescription": [
        "I need a refill for my blood pressure medication",
        "How do I request a prescription renewal?",
    ],
    "Report": [
        "My HbA1c is 7.2, what does that mean?",
        "Can you explain what eGFR means in my kidney function test?",
    ],
    "Insurance": [
        "Does my insurance cover mental health therapy?",
        "How do I file a claim for my recent hospital visit?",
    ],
    "Emergency": [
        "I have severe chest pain and my left arm is numb",
        "I can't breathe properly and feel very dizzy",
    ],
}

# ── Navigation Bar ─────────────────────────────────────────────────────────────
st.write("") # Spacer
nav_cols = st.columns([1, 1, 1])

with nav_cols[0]:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()
with nav_cols[1]:
    if st.button("💬 Chatbot", use_container_width=True):
        st.session_state.page = "Chatbot"
        st.rerun()
with nav_cols[2]:
    if st.button("📊 Monitor Logs", use_container_width=True):
        st.session_state.page = "Monitor Logs"
        st.rerun()

st.markdown("<hr style='border: 1px solid #002244;'>", unsafe_allow_html=True)

# ── Page Routing ───────────────────────────────────────────────────────────────

if st.session_state.page == "Home":
    st.markdown("""
    <style>
        /* Force Center Expander headers only on Home Page */
        div[data-testid="stExpander"] details summary {
            position: relative;
            justify-content: center !important;
        }
        div[data-testid="stExpander"] details summary > div, 
        div[data-testid="stExpander"] details summary > span {
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
        }
        div[data-testid="stExpander"] details summary p {
            font-weight: bold;
            font-size: 1.1rem;
            text-align: center !important;
            margin: 0 !important;
            width: 100% !important;
        }
        div[data-testid="stExpander"] details summary svg {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='centered-card'>
        <h1>🏥 Healthcare AI Experience Platform</h1>
        <p style='color: #aaa; font-size: 1.1rem; margin-top: 15px;'>
            A powerful, intelligent multi-agent healthcare assistant designed to streamline patient queries. 
            From scheduling appointments and explaining medical reports to handling emergencies with immediate escalations.
        </p>
        <div class='metric-container'>
            <div class='metric-box'>
                <div class='metric-val'>{}</div>
                <div class='metric-label'>Total Queries Processed</div>
            </div>
            <div class='metric-box' style='border-color: #ff0033;'>
                <div class='metric-val' style='color: #ff0033;'>{}</div>
                <div class='metric-label'>Emergencies Handled</div>
            </div>
        </div>
    </div>
    """.format(st.session_state.total_queries, st.session_state.emergency_count), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Try it out section
    st.markdown("<h3>💡 Quick Start</h3>", unsafe_allow_html=True)
    
    categories = list(SAMPLE_QUERIES.keys())
    col1, spacer, col2 = st.columns([4, 1, 4])
    
    # First 4 categories in 2 columns
    for i in range(4):
        category = categories[i]
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            with st.expander(category):
                for q in SAMPLE_QUERIES[category]:
                    if st.button(q, key=q, use_container_width=True):
                        st.session_state.prefill = q
                        st.session_state.page = "Chatbot"
                        st.rerun()
                        
    # 5th category (Emergency) centered below
    st.write("") # Spacer
    center_col = st.columns([1, 2, 1])[1]
    with center_col:
        with st.expander(categories[4]):
            for q in SAMPLE_QUERIES[categories[4]]:
                if st.button(q, key=q, use_container_width=True):
                    st.session_state.prefill = q
                    st.session_state.page = "Chatbot"
                    st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("🚀 START CHATTING", type="primary"):
        st.session_state.page = "Chatbot"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Status
    st.markdown("<br><div style='text-align: center;'>", unsafe_allow_html=True)
    if backend_status():
        st.markdown("<span style='color: #00ff00;'>🟢 System Online & Ready</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span style='color: #ff0000;'>🔴 Backend Offline - Please start the server</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


elif st.session_state.page == "Chatbot":
    st.markdown("<h2>💬 Healthcare Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888;'>Powered by Multi-Agent System | Type your query below</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    
    # Clear chat button
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()

    # Display chat history
    if not st.session_state.chat_history:
        st.markdown("""
        <div style='text-align:center; padding:40px; color:#555;'>
            <h3 style='color: #555 !important;'>👋 Hello! I'm your Healthcare AI</h3>
            <p>I can help with appointments, prescriptions, reports, and insurance.</p>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class='user-msg'>
                {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            agent = msg.get("agent", "AI")
            
            if msg.get("is_emergency"):
                st.markdown(f"""
                <div class='emergency-box'>
                    🚨 EMERGENCY ESCALATION DETECTED ({agent})
                </div>
                """, unsafe_allow_html=True)

            meta = f"🕐 {msg.get('timestamp', '')}"
            if msg.get("compliance_violated"):
                meta += " | ⚠️ Compliance reviewed"

            st.markdown(f"""
            <div class='ai-msg'>
                <div class='agent-badge'>{agent}</div>
                <div>{msg['content'].replace(chr(10), '<br>')}</div>
                <div class='timestamp'>{meta}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div><br><br>", unsafe_allow_html=True)

    # ── Input form ─────────────────────────────────────────────────────────────
    prefill_val = st.session_state.pop("prefill", "")

    # Put form at the bottom
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Message",
            value=prefill_val,
            placeholder="Type your healthcare question here...",
            height=70,
            label_visibility="collapsed",
        )
        send_btn = st.form_submit_button("📤 Send Message", use_container_width=True)

    if send_btn:
        if not user_input.strip():
            st.warning("Please type a message before sending.")
        else:
            # Save user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input.strip(),
            })

            with st.spinner("⏳ Processing..."):
                result, error = send_query(user_input.strip())

            if error:
                st.error(error)
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


elif st.session_state.page == "Monitor Logs":
    st.markdown("<h2>📊 System Monitoring & Logs</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

    st.markdown("<h3>Live Agent Metrics</h3>", unsafe_allow_html=True)
    data = get_monitoring()
    
    if not data:
        st.info("No data available yet — please interact with the Chatbot first!")
    else:
        total_q = sum(d["query_count"] for d in data)
        total_e = sum(d["escalation_count"] for d in data)
        total_v = sum(d["compliance_violation_count"] for d in data)

        st.markdown(f"""
        <div class='metric-container'>
            <div class='metric-box' style='width: 30%;'>
                <div class='metric-val'>{total_q}</div>
                <div class='metric-label'>Total Queries</div>
            </div>
            <div class='metric-box' style='width: 30%; border-color: #ff0033;'>
                <div class='metric-val' style='color: #ff0033;'>{total_e}</div>
                <div class='metric-label'>Total Escalations</div>
            </div>
            <div class='metric-box' style='width: 30%; border-color: #ffaa00;'>
                <div class='metric-val' style='color: #ffaa00;'>{total_v}</div>
                <div class='metric-label'>Compliance Issues</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        for agent in data:
            with st.expander(f"{agent['agent_name']}  —  {agent['query_count']} queries"):
                a, b, c, d = st.columns(4)
                a.metric("Queries", agent["query_count"])
                b.metric("Escalations", agent["escalation_count"])
                c.metric("Violations", agent["compliance_violation_count"])
                d.metric("Avg Length", f"{agent['avg_response_length']} chars")

    st.markdown("<hr style='border: 1px solid #002244;'><br>", unsafe_allow_html=True)
    st.markdown("<h3>📋 Recent Query Logs</h3>", unsafe_allow_html=True)
    
    logs = get_logs()
    if not logs:
        st.info("No logs available yet.")
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

