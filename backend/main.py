"""
FastAPI Backend for Healthcare Agentic AI System.
Provides REST API endpoints for the Streamlit frontend.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.orchestrator import process_query
from database.models import init_db, get_db
from database.crud import (
    log_query, get_or_create_user,
    update_agent_monitoring, get_recent_logs, get_agent_stats
)
from services.logger_service import logger

# Initialize database on startup
init_db()

app = FastAPI(
    title="Healthcare Agentic AI System",
    description="Multi-agent AI system for healthcare assistance",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request/Response Models ──────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str
    session_id: str = ""


class QueryResponse(BaseModel):
    session_id: str
    query: str
    response: str
    assigned_agent: str
    is_emergency: bool
    compliance_violated: bool
    compliance_notes: str
    timestamp: str


# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Healthcare AI System", "timestamp": datetime.utcnow().isoformat()}


@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Main endpoint to process healthcare queries.
    Routes through LangGraph multi-agent pipeline.
    """
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    logger.info(f"[API] New query | Session: {session_id} | Query: {request.query[:80]}")

    try:
        # Ensure user exists in DB
        get_or_create_user(db, session_id)

        # Process through LangGraph orchestrator
        result = process_query(request.query, session_id)

        # Log to database
        log_query(
            db=db,
            session_id=session_id,
            query=request.query,
            assigned_agent=result["assigned_agent"],
            response=result["final_response"],
            escalation_status=result["is_emergency"],
            compliance_violation=result["compliance_violated"],
            compliance_notes=result["compliance_notes"],
        )

        # Update agent monitoring stats
        update_agent_monitoring(
            db=db,
            agent_name=result["assigned_agent"],
            escalated=result["is_emergency"],
            compliance_violated=result["compliance_violated"],
            response_length=len(result["final_response"]),
        )

        return QueryResponse(
            session_id=session_id,
            query=request.query,
            response=result["final_response"],
            assigned_agent=result["assigned_agent"],
            is_emergency=result["is_emergency"],
            compliance_violated=result["compliance_violated"],
            compliance_notes=result["compliance_notes"],
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"[API Error] {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/logs")
def get_logs(limit: int = 20, db: Session = Depends(get_db)):
    """Retrieve recent query logs for monitoring dashboard."""
    logs = get_recent_logs(db, limit)
    return [
        {
            "id": log.id,
            "session_id": log.session_id,
            "timestamp": log.timestamp.isoformat(),
            "query": log.query[:100] + "..." if len(log.query) > 100 else log.query,
            "assigned_agent": log.assigned_agent,
            "escalation_status": log.escalation_status,
            "compliance_violation": log.compliance_violation,
            "compliance_notes": log.compliance_notes,
        }
        for log in logs
    ]


@app.get("/monitoring")
def get_monitoring(db: Session = Depends(get_db)):
    """Retrieve agent monitoring statistics."""
    stats = get_agent_stats(db)
    return [
        {
            "agent_name": s.agent_name,
            "query_count": s.query_count,
            "escalation_count": s.escalation_count,
            "compliance_violation_count": s.compliance_violation_count,
            "avg_response_length": s.avg_response_length,
        }
        for s in stats
    ]


@app.get("/sample-queries")
def get_sample_queries():
    """Return sample test queries for demonstration."""
    return {
        "appointment": [
            "I need to schedule an appointment with a cardiologist",
            "Can I reschedule my appointment from Monday to Wednesday?",
            "How do I cancel my upcoming appointment?",
        ],
        "prescription": [
            "I need a refill for my blood pressure medication",
            "How do I request a prescription renewal?",
            "What should I do if I missed a dose?",
        ],
        "report": [
            "My HbA1c is 7.2, what does that mean?",
            "Can you explain what eGFR means in my kidney function test?",
            "My cholesterol report shows LDL of 145, can you explain?",
        ],
        "insurance": [
            "Does my insurance cover mental health therapy?",
            "How do I file a claim for my recent hospital visit?",
            "What is a prior authorization and how do I get one?",
        ],
        "emergency": [
            "I have severe chest pain and my left arm is numb",
            "I can't breathe properly and feel dizzy",
            "I'm having thoughts of hurting myself",
        ],
    }
