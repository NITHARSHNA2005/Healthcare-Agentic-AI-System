"""
CRUD operations for Healthcare AI System database.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from .models import User, QueryLog, AgentMonitoring


def get_or_create_user(db: Session, session_id: str) -> User:
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        user = User(session_id=session_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_active = datetime.utcnow()
        db.commit()
    return user


def log_query(
    db: Session,
    session_id: str,
    query: str,
    assigned_agent: str,
    response: str,
    escalation_status: bool = False,
    compliance_violation: bool = False,
    compliance_notes: str = "",
) -> QueryLog:
    log = QueryLog(
        session_id=session_id,
        query=query,
        assigned_agent=assigned_agent,
        response=response,
        escalation_status=escalation_status,
        compliance_violation=compliance_violation,
        compliance_notes=compliance_notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def update_agent_monitoring(db: Session, agent_name: str, escalated: bool, compliance_violated: bool, response_length: int):
    record = db.query(AgentMonitoring).filter(AgentMonitoring.agent_name == agent_name).first()
    if not record:
        record = AgentMonitoring(agent_name=agent_name)
        db.add(record)

    record.query_count = (record.query_count or 0) + 1
    if escalated:
        record.escalation_count = (record.escalation_count or 0) + 1
    if compliance_violated:
        record.compliance_violation_count = (record.compliance_violation_count or 0) + 1
    prev = record.avg_response_length or 0
    record.avg_response_length = (prev + response_length) // 2
    db.commit()


def get_recent_logs(db: Session, limit: int = 20):
    return db.query(QueryLog).order_by(QueryLog.timestamp.desc()).limit(limit).all()


def get_agent_stats(db: Session):
    return db.query(AgentMonitoring).all()
