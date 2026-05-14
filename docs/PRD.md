# Product Requirements Document (PRD)
# Healthcare Agentic AI System


---

## 1. Executive Summary

A healthcare provider receives 5,000+ patient inquiries daily related to appointments, prescriptions, lab results and insurance claims. Manual handling causes response delays, missed appointments and declining patient satisfaction. This PRD defines the requirements for an Agentic AI system that intelligently routes patient queries to specialized AI agents, enforces healthcare guardrails, and monitors every decision in real time.

---

## 2. Problem Statement

**How Might We** automate the routing and resolution of 5,000+ daily patient inquiries for a healthcare provider so that patients receive accurate, safe and timely responses without burdening clinical staff — while ensuring zero medical advice is given beyond approved guidelines?

---

## 3. Stakeholders & Pain Points

| Stakeholder | Pain Point | Risk if Unsolved |
|-------------|-----------|-----------------|
| Patient | Long wait times, no 24/7 support, confusing medical info | Missed appointments, delayed treatment, patient harm |
| Clinical Staff | Overwhelmed with non-clinical queries | Burnout, reduced time for actual patient care |
| Healthcare Organization | High operational cost, compliance risk | Legal liability, regulatory fines, reputation damage |
| Compliance Team | No audit trail, uncontrolled AI responses | HIPAA violations, data breaches |

---

## 4. Goals & Non-Goals

### Goals
- Automate routing of patient queries to specialized agents
- Enforce healthcare guardrails on every AI response
- Escalate emergencies to human staff immediately
- Log every decision, escalation and compliance event
- Provide real-time monitoring dashboard

### Non-Goals
- Replace licensed medical professionals
- Provide medical diagnosis or treatment plans
- Store or process Protected Health Information (PHI) beyond session scope
- Integrate with live EHR systems (future phase)

---

## 5. System Architecture

```
Patient Query
     │
     ▼
┌─────────────────────────────────────────┐
│         LangGraph Orchestrator           │
│  detect_intent → route_to_agent          │
│              ↓ (emergency?)              │
│         escalation_agent                 │
│              ↓                           │
│         apply_guardrails                 │
│              ↓                           │
│         finalize_response                │
└─────────────────────────────────────────┘
     │
     ▼
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│Appoint-  │Prescrip- │ Report   │Insurance │Escalation│
│ment      │tion      │Explain.  │  Agent   │  Agent   │
│ Agent    │ Agent    │ Agent    │          │          │
└──────────┴──────────┴──────────┴──────────┴──────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│         Compliance Agent                 │
│  Pattern Matching + LLM Review           │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│         SQLite Database                  │
│  query_logs | users | agent_monitoring   │
└─────────────────────────────────────────┘
```

---

## 6. Functional Requirements

### 6.1 Orchestrator (LangGraph)
- FR-01: Detect user intent using LLM classification
- FR-02: Route query to correct specialized agent
- FR-03: Detect emergency keywords before routing
- FR-04: Apply compliance checks on every response
- FR-05: Log all decisions to database

### 6.2 Specialized Agents
- FR-06: Appointment Agent — handle scheduling, rescheduling, cancellation
- FR-07: Prescription Agent — handle refill requests, medication info (no prescribing)
- FR-08: Report Explanation Agent — explain lab results in plain language (no diagnosis)
- FR-09: Insurance Agent — handle coverage, claims, billing queries
- FR-10: Escalation Agent — handle life-threatening emergencies with 911 directive
- FR-11: Compliance Agent — dual-layer check (pattern + LLM) on all responses

### 6.3 Guardrails
- FR-12: Block any response that prescribes medication or dosage
- FR-13: Block any response that diagnoses a medical condition
- FR-14: Trigger emergency escalation for defined critical keywords
- FR-15: Prevent sharing of patient data across sessions
- FR-16: Replace non-compliant responses with safe alternatives

### 6.4 Monitoring & Logging
- FR-17: Log every query with timestamp, agent, escalation status, compliance status
- FR-18: Track per-agent metrics: query count, escalation count, violation count
- FR-19: Provide real-time monitoring dashboard in UI
- FR-20: Expose monitoring API endpoint

---

## 7. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Response Time | < 5 seconds per query |
| Availability | 99.9% uptime |
| Scalability | Handle 5,000+ queries/day |
| Security | API keys in environment variables, never in code |
| Compliance | No PHI stored beyond session, no diagnosis/prescription |
| Auditability | 100% of queries logged with full metadata |

---

## 8. Emergency Escalation Triggers

The following keywords trigger immediate escalation to the Escalation Agent:

- chest pain, heart attack
- can't breathe, breathing problem, shortness of breath
- suicidal, suicide, want to die, kill myself
- severe bleeding, bleeding won't stop
- unconscious, not breathing, stroke, seizure
- overdose, poisoning, anaphylaxis

**Escalation Response:** Immediate 911 directive + calm safety guidance

---

## 9. Database Schema

### query_logs
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| session_id | VARCHAR | User session identifier |
| timestamp | DATETIME | Query timestamp |
| query | TEXT | Patient query |
| assigned_agent | VARCHAR | Agent that handled query |
| escalation_status | BOOLEAN | Emergency flag |
| response | TEXT | AI response |
| compliance_violation | BOOLEAN | Violation detected flag |
| compliance_notes | TEXT | Violation details |

### users
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| session_id | VARCHAR | Unique session |
| created_at | DATETIME | First interaction |
| last_active | DATETIME | Last interaction |

### agent_monitoring
| Column | Type | Description |
|--------|------|-------------|
| agent_name | VARCHAR | Agent identifier |
| query_count | INTEGER | Total queries handled |
| escalation_count | INTEGER | Emergency escalations |
| compliance_violation_count | INTEGER | Violations detected |
| avg_response_length | INTEGER | Average response chars |

---

## 10. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Query Resolution Rate | > 90% resolved without human | query_logs.escalation_status |
| Emergency Response Time | < 2 seconds for escalation | timestamp delta |
| Compliance Violation Rate | < 1% of all responses | compliance_violation / total |
| Agent Routing Accuracy | > 95% correct agent assigned | manual audit sample |
| System Uptime | > 99.9% | health check endpoint |

---

## 11. Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Model | Groq Llama 3.3 70B (via Groq API) |
| Orchestration | LangGraph |
| Backend | FastAPI (Python) |
| Frontend | Streamlit |
| Database | SQLite + SQLAlchemy |
| Logging | Python logging + rotating file handler |

---

## 12. Future Enhancements

- [ ] Integration with real EHR systems (Epic, Cerner)
- [ ] HIPAA-compliant data storage
- [ ] Voice input support
- [ ] Multi-language support
- [ ] Telemedicine video escalation
- [ ] Fine-tuned healthcare-specific model
- [ ] User authentication and patient profiles
- [ ] Advanced analytics dashboard

----
## 13. Conclusion

The Healthcare Agentic AI System demonstrates how multi-agent AI architecture can improve healthcare support operations while maintaining patient safety, compliance and scalability. By combining LangGraph orchestration, specialized healthcare agents, emergency escalation workflows and compliance guardrails, the system is able to automate patient query handling efficiently without replacing medical professionals.

The proposed solution reduces operational burden on healthcare staff, improves patient response time and ensures that critical healthcare scenarios are escalated safely to human intervention. Real-time monitoring, logging and compliance validation further enhance transparency, auditability and system reliability.

Built using FastAPI, Streamlit, LangGraph, Groq API and SQLite, the project provides a scalable and modular foundation for future healthcare AI systems. Future enhancements such as EHR integration, voice-based interaction and advanced analytics can further expand the system into a production-ready intelligent healthcare platform.

