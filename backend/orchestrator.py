"""
LangGraph Orchestrator for Healthcare AI System.
Manages the multi-agent workflow with intent detection, routing,
guardrails, compliance checking, and logging.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

from agents.appointment_agent import appointment_agent
from agents.prescription_agent import prescription_agent
from agents.report_agent import report_explanation_agent
from agents.insurance_agent import insurance_agent
from agents.escalation_agent import escalation_agent, is_emergency
from agents.compliance_agent import compliance_agent
from services.llm_service import call_llm
from services.logger_service import logger


# ─── State Definition ────────────────────────────────────────────────────────

class HealthcareState(TypedDict):
    query: str
    session_id: str
    intent: str
    assigned_agent: str
    response: str
    is_emergency: bool
    compliance_violated: bool
    compliance_notes: str
    final_response: str


# ─── Node Functions ───────────────────────────────────────────────────────────

def detect_intent(state: HealthcareState) -> HealthcareState:
    """
    Node 1: Detect user intent and check for emergency.
    Routes to appropriate agent based on query content.
    """
    query = state["query"]
    logger.info(f"[Intent Detection] Query: {query[:80]}...")

    # Emergency check takes highest priority
    if is_emergency(query):
        logger.warning(f"[EMERGENCY DETECTED] Query: {query[:80]}")
        return {**state, "intent": "emergency", "is_emergency": True}

    # LLM-based intent classification
    intent_prompt = f"""Classify this healthcare query into exactly ONE category:
- appointment: scheduling, booking, rescheduling, cancelling appointments
- prescription: medication refills, prescription questions
- report: lab results, medical reports, test results explanation
- insurance: coverage, claims, billing, copay questions
- general: general health questions, other queries

Query: {query}

Reply with ONLY the category word (appointment/prescription/report/insurance/general):"""

    intent = call_llm(intent_prompt).strip().lower()

    # Validate intent
    valid_intents = ["appointment", "prescription", "report", "insurance", "general"]
    if intent not in valid_intents:
        intent = "general"

    logger.info(f"[Intent Detected] Intent: {intent}")
    return {**state, "intent": intent, "is_emergency": False}


def route_to_agent(state: HealthcareState) -> HealthcareState:
    """
    Node 2: Route query to the appropriate specialized agent.
    """
    intent = state["intent"]
    query = state["query"]

    agent_map = {
        "appointment": ("Appointment Agent", appointment_agent),
        "prescription": ("Prescription Agent", prescription_agent),
        "report": ("Report Explanation Agent", report_explanation_agent),
        "insurance": ("Insurance Agent", insurance_agent),
        "emergency": ("Escalation Agent", escalation_agent),
        "general": ("Appointment Agent", appointment_agent),  # Default fallback
    }

    agent_name, agent_func = agent_map.get(intent, agent_map["general"])
    logger.info(f"[Agent Routing] Assigned: {agent_name}")

    response = agent_func(query)
    return {**state, "assigned_agent": agent_name, "response": response}


def apply_guardrails(state: HealthcareState) -> HealthcareState:
    """
    Node 3: Apply healthcare guardrails to the response.
    Checks for compliance violations and replaces unsafe responses.
    """
    if state["is_emergency"]:
        # Emergency responses bypass compliance replacement but still log
        return {**state, "compliance_violated": False, "compliance_notes": ""}

    query = state["query"]
    response = state["response"]

    is_violated, notes, safe_response = compliance_agent(query, response)

    if is_violated:
        logger.warning(f"[Compliance Violation] Notes: {notes}")

    return {
        **state,
        "compliance_violated": is_violated,
        "compliance_notes": notes,
        "response": safe_response,
    }


def finalize_response(state: HealthcareState) -> HealthcareState:
    """
    Node 4: Finalize and format the response for the user.
    """
    response = state["response"]
    
    # Add compliance warning footer if violation was detected and corrected
    if state["compliance_violated"]:
        footer = "\n\n⚠️ Note: This response has been reviewed for healthcare compliance."
        response = response + footer

    logger.info(f"[Response Finalized] Agent: {state['assigned_agent']} | Emergency: {state['is_emergency']}")
    return {**state, "final_response": response}


# ─── Routing Logic ────────────────────────────────────────────────────────────

def should_escalate(state: HealthcareState) -> Literal["escalate", "route"]:
    """Conditional edge: check if emergency escalation is needed."""
    return "escalate" if state["is_emergency"] else "route"


# ─── Build LangGraph Workflow ─────────────────────────────────────────────────

def build_healthcare_graph() -> StateGraph:
    """Build and compile the LangGraph multi-agent workflow."""
    workflow = StateGraph(HealthcareState)

    # Add nodes
    workflow.add_node("detect_intent", detect_intent)
    workflow.add_node("route_to_agent", route_to_agent)
    workflow.add_node("escalation", lambda s: {**s, "assigned_agent": "Escalation Agent", "response": escalation_agent(s["query"])})
    workflow.add_node("apply_guardrails", apply_guardrails)
    workflow.add_node("finalize_response", finalize_response)

    # Set entry point
    workflow.set_entry_point("detect_intent")

    # Add edges
    workflow.add_conditional_edges(
        "detect_intent",
        should_escalate,
        {"escalate": "escalation", "route": "route_to_agent"},
    )
    workflow.add_edge("route_to_agent", "apply_guardrails")
    workflow.add_edge("escalation", "apply_guardrails")
    workflow.add_edge("apply_guardrails", "finalize_response")
    workflow.add_edge("finalize_response", END)

    return workflow.compile()


# Compiled graph instance (singleton)
healthcare_graph = build_healthcare_graph()


def process_query(query: str, session_id: str = "default") -> dict:
    """
    Main entry point to process a healthcare query through the LangGraph pipeline.
    Returns a dict with all state information.
    """
    initial_state: HealthcareState = {
        "query": query,
        "session_id": session_id,
        "intent": "",
        "assigned_agent": "",
        "response": "",
        "is_emergency": False,
        "compliance_violated": False,
        "compliance_notes": "",
        "final_response": "",
    }

    result = healthcare_graph.invoke(initial_state)
    return result
