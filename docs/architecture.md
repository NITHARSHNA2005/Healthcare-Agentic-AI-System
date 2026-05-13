# Healthcare AI System - Architecture

## System Architecture

```
User (Browser)
     │
     ▼
┌─────────────────────────────────┐
│   Streamlit Frontend (Port 8501) │
│   - Chat Interface               │
│   - Monitoring Dashboard         │
│   - Query Logs                   │
└────────────────┬────────────────┘
                 │ HTTP REST
                 ▼
┌─────────────────────────────────┐
│   FastAPI Backend (Port 8000)    │
│   - /query endpoint              │
│   - /logs endpoint               │
│   - /monitoring endpoint         │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              LangGraph Orchestrator                   │
│                                                       │
│  [detect_intent] → [route_to_agent] → [guardrails]  │
│        │                                    │         │
│        └──── [escalation] ─────────────────┘         │
│                                    │                  │
│                          [finalize_response]          │
└─────────────────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐ ┌────────┐ ┌────────────┐
│Appoint-│ │Prescr- │ │  Report    │
│ment    │ │iption  │ │Explanation │
│Agent   │ │Agent   │ │  Agent     │
└────────┘ └────────┘ └────────────┘
    ▼            ▼            ▼
┌────────┐ ┌────────┐ ┌────────────┐
│Insur-  │ │Escala- │ │Compliance  │
│ance    │ │tion    │ │  Agent     │
│Agent   │ │Agent   │ │            │
└────────┘ └────────┘ └────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│   SQLite Database                │
│   - query_logs                   │
│   - users                        │
│   - agent_monitoring             │
└─────────────────────────────────┘
```

## LangGraph Workflow

1. **detect_intent** - Classifies query intent, checks for emergencies
2. **route_to_agent** - Routes to specialized agent based on intent
3. **escalation** - Handles emergency situations (bypasses normal routing)
4. **apply_guardrails** - Compliance checking via pattern matching + LLM
5. **finalize_response** - Formats final response for user

## Agent Responsibilities

| Agent | Handles |
|-------|---------|
| Appointment Agent | Scheduling, rescheduling, cancellations |
| Prescription Agent | Refill requests, medication info (no prescribing) |
| Report Explanation Agent | Lab results, medical terminology |
| Insurance Agent | Coverage, claims, billing |
| Escalation Agent | Emergencies, life-threatening situations |
| Compliance Agent | Guardrail enforcement, violation detection |
