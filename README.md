# 🏥 Healthcare Agentic AI System

A production-grade multi-agent AI system for healthcare assistance, built with Python, FastAPI, Streamlit, LangGraph, and Google Gemini 1.5 Flash.

---

## 🚀 Features

- **Multi-Agent Architecture** — 6 specialized AI agents for different healthcare domains
- **LangGraph Orchestration** — Intelligent routing with state management
- **Emergency Escalation** — Automatic detection and escalation for life-threatening queries
- **Healthcare Guardrails** — AI never prescribes medicine or diagnoses diseases
- **Compliance Checking** — Dual-layer compliance (pattern matching + LLM review)
- **Real-time Monitoring** — Agent performance dashboard
- **Persistent Logging** — SQLite database for all interactions
- **Clean UI** — Streamlit chatbot with escalation alerts

---

## 🏗️ Project Structure

```
Health-care-Agentic AI System/
├── backend/
│   ├── main.py              # FastAPI application
│   └── orchestrator.py      # LangGraph multi-agent orchestrator
├── frontend/
│   └── app.py               # Streamlit UI
├── agents/
│   ├── appointment_agent.py
│   ├── prescription_agent.py
│   ├── report_agent.py
│   ├── insurance_agent.py
│   ├── escalation_agent.py
│   └── compliance_agent.py
├── services/
│   ├── gemini_service.py    # Gemini API wrapper
│   └── logger_service.py    # Logging configuration
├── database/
│   ├── models.py            # SQLAlchemy models
│   └── crud.py              # Database operations
├── logs/                    # Application logs
├── docs/                    # Documentation
├── .env                     # Environment variables
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+
- Google Gemini API Key

### Step 1: Clone / Navigate to project
```bash
cd "Health-care-Agentic AI System"
```

### Step 2: Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure environment
The `.env` file is already configured. To use your own API key:
```
GEMINI_API_KEY=your_api_key_here
```

### Step 5: Start the system

**Terminal 1 — Backend:**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```bash
streamlit run frontend/app.py --server.port 8501
```

### Access the application
- **Chat UI:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## 🤖 Agents

| Agent | Intent | Description |
|-------|--------|-------------|
| Appointment Agent | `appointment` | Schedule, reschedule, cancel appointments |
| Prescription Agent | `prescription` | Medication refills, prescription guidance |
| Report Explanation Agent | `report` | Explain lab results and medical terminology |
| Insurance Agent | `insurance` | Coverage, claims, billing questions |
| Escalation Agent | `emergency` | Life-threatening emergency handling |
| Compliance Agent | `all` | Guardrail enforcement on all responses |

---

## 🔄 LangGraph Workflow

```
Query → detect_intent → [emergency?] → escalation → apply_guardrails → finalize
                      ↓
                   route_to_agent → apply_guardrails → finalize
```

---

## 🛡️ Healthcare Guardrails

1. **No Prescribing** — AI never prescribes medications or dosages
2. **No Diagnosing** — AI never diagnoses medical conditions
3. **Emergency Escalation** — Triggers for: chest pain, heart attack, breathing issues, suicidal thoughts, severe bleeding
4. **Privacy Protection** — Never requests sensitive personal information
5. **Dual Compliance Check** — Pattern matching + LLM-based review

---

## 🧪 Sample Test Queries

**Appointments:**
- "I need to schedule an appointment with a cardiologist"
- "Can I reschedule my appointment from Monday to Wednesday?"

**Prescriptions:**
- "I need a refill for my blood pressure medication"
- "How do I request a prescription renewal?"

**Medical Reports:**
- "My HbA1c is 7.2, what does that mean?"
- "Can you explain what eGFR means in my kidney function test?"

**Insurance:**
- "Does my insurance cover mental health therapy?"
- "How do I file a claim for my recent hospital visit?"

**Emergency (triggers escalation):**
- "I have severe chest pain and my left arm is numb"
- "I can't breathe properly and feel dizzy"

---

## 📊 Database Schema

### query_logs
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| session_id | VARCHAR | User session |
| timestamp | DATETIME | Query time |
| query | TEXT | User query |
| assigned_agent | VARCHAR | Agent used |
| escalation_status | BOOLEAN | Emergency flag |
| response | TEXT | AI response |
| compliance_violation | BOOLEAN | Violation flag |
| compliance_notes | TEXT | Violation details |

### users
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| session_id | VARCHAR | Unique session |
| created_at | DATETIME | First seen |
| last_active | DATETIME | Last activity |

### agent_monitoring
| Column | Type | Description |
|--------|------|-------------|
| agent_name | VARCHAR | Agent identifier |
| query_count | INTEGER | Total queries |
| escalation_count | INTEGER | Emergency count |
| compliance_violation_count | INTEGER | Violations |
| avg_response_length | INTEGER | Avg chars |

---

## 🔮 Future Enhancements

- [ ] User authentication and patient profiles
- [ ] Integration with real EHR systems (Epic, Cerner)
- [ ] Voice input support
- [ ] Multi-language support
- [ ] HIPAA compliance audit trail
- [ ] Integration with appointment scheduling APIs
- [ ] Telemedicine video call escalation
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Fine-tuned healthcare-specific model

---

## ⚠️ Disclaimer

This system is for demonstration purposes only. It does not replace professional medical advice. Always consult a qualified healthcare provider for medical decisions.

---

## 📄 License

MIT License — Free to use for educational and portfolio purposes.
