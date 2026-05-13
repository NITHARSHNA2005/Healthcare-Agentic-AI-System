"""
Database models and initialization for Healthcare AI System.
Uses SQLAlchemy with SQLite for persistent storage.
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "healthcare.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """Stores patient/user information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)


class QueryLog(Base):
    """Logs every query processed by the system."""
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    query = Column(Text, nullable=False)
    assigned_agent = Column(String(50))
    escalation_status = Column(Boolean, default=False)
    response = Column(Text)
    compliance_violation = Column(Boolean, default=False)
    compliance_notes = Column(Text)


class AgentMonitoring(Base):
    """Tracks agent performance and usage metrics."""
    __tablename__ = "agent_monitoring"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_name = Column(String(50))
    query_count = Column(Integer, default=0)
    escalation_count = Column(Integer, default=0)
    compliance_violation_count = Column(Integer, default=0)
    avg_response_length = Column(Integer, default=0)


def init_db():
    """Initialize database and create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
