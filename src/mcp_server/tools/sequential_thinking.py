"""Sequential Thinking MCP - Multi-step reasoning for complex problems."""

from __future__ import annotations

import json
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime


class ThinkingSession:
    """Represents a sequential thinking session."""

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.steps = []
        self.current_step = 0

    def add_step(self, thought: str, action: Optional[str] = None,
                 observation: Optional[str] = None, confidence: float = 1.0) -> dict:
        """Add a thinking step."""
        step = {
            "step": self.current_step + 1,
            "timestamp": datetime.now().isoformat(),
            "thought": thought,
            "action": action,
            "observation": observation,
            "confidence": confidence,
            "revisable": True,
        }
        self.steps.append(step)
        self.current_step += 1
        return step

    def revise_step(self, step_num: int, new_thought: str, reason: str) -> dict:
        """Revise a previous thinking step."""
        if 0 <= step_num < len(self.steps):
            old_thought = self.steps[step_num]["thought"]
            self.steps[step_num]["thought"] = new_thought
            self.steps[step_num]["revision_reason"] = reason
            self.steps[step_num]["original"] = old_thought
            return {"success": True, "step": self.steps[step_num]}
        return {"success": False, "error": "Step not found"}

    def get_summary(self) -> dict:
        """Get thinking summary."""
        return {
            "session_id": self.session_id,
            "total_steps": len(self.steps),
            "current_step": self.current_step,
            "steps": self.steps,
        }


# Global storage for sessions (in production, use proper storage)
_sessions: Dict[str, ThinkingSession] = {}


def create_session() -> dict:
    """Create a new thinking session."""
    session = ThinkingSession()
    _sessions[session.session_id] = session
    return {"session_id": session.session_id, "message": "Session created"}


def think(
    session_id: str,
    thought: str,
    action: Optional[str] = None,
    observation: Optional[str] = None,
    confidence: float = 1.0,
) -> dict:
    """Add a thinking step to session."""
    if session_id not in _sessions:
        session = ThinkingSession(session_id)
        _sessions[session_id] = session

    step = _sessions[session_id].add_step(thought, action, observation, confidence)
    return {"step": step, "session_id": session_id}


def revise(
    session_id: str,
    step: int,
    new_thought: str,
    reason: str,
) -> dict:
    """Revise a previous step."""
    if session_id not in _sessions:
        return {"success": False, "error": "Session not found"}

    return _sessions[session_id].revise_step(step, new_thought, reason)


def get_session(session_id: str) -> dict:
    """Get session summary."""
    if session_id not in _sessions:
        return {"error": "Session not found"}

    return _sessions[session_id].get_summary()


def list_sessions() -> dict:
    """List all active sessions."""
    return {
        "sessions": [
            {"session_id": sid, "steps": len(s.session.steps)}
            for sid, s in _sessions.items()
        ]
    }


def delete_session(session_id: str) -> dict:
    """Delete a session."""
    if session_id in _sessions:
        del _sessions[session_id]
        return {"success": True, "message": "Session deleted"}
    return {"success": False, "error": "Session not found"}


def chain_think(
    thoughts: List[str],
    context: Optional[Dict] = None,
) -> dict:
    """
    Create a chain of thoughts.

    Args:
        thoughts: List of thought strings to process sequentially
        context: Optional context dict to pass through

    Returns:
        dict with all steps and final conclusion
    """
    session = ThinkingSession()
    _sessions[session.session_id] = session

    results = []
    for i, thought in enumerate(thoughts):
        step = session.add_step(
            thought=thought,
            action=f"step_{i + 1}",
            confidence=1.0 if i == len(thoughts) - 1 else 0.8,
        )
        results.append(step)

    return {
        "session_id": session.session_id,
        "chain_length": len(thoughts),
        "steps": results,
        "conclusion": thoughts[-1] if thoughts else "",
        "context": context,
    }


def analyze_problem(
    problem: str,
    approach: str = "decompose",
) -> dict:
    """
    Analyze a problem using structured thinking.

    Approaches: decompose, hypothesize, compare, evaluate
    """
    session = ThinkingSession()
    _sessions[session.session_id] = session

    if approach == "decompose":
        session.add_step(
            thought=f"Understanding the problem: {problem[:100]}...",
            action="understand",
        )
        session.add_step(
            thought="Breaking down into components...",
            action="decompose",
        )
        session.add_step(
            thought="Identifying key factors and constraints...",
            action="identify",
        )
        session.add_step(
            thought="Synthesizing solution approach...",
            action="synthesize",
        )
    elif approach == "hypothesize":
        session.add_step(
            thought=f"Initial hypothesis for: {problem[:100]}...",
            action="hypothesis_1",
        )
        session.add_step(
            thought="Testing against known constraints...",
            action="test",
        )
        session.add_step(
            thought="Refining based on observations...",
            action="refine",
        )
    elif approach == "compare":
        session.add_step(
            thought=f"Comparing alternatives for: {problem[:100]}...",
            action="compare",
        )
        session.add_step(
            thought="Evaluating trade-offs...",
            action="evaluate",
        )
        session.add_step(
            thought="Selecting optimal approach...",
            action="select",
        )
    else:
        session.add_step(
            thought=f"Systematic analysis of: {problem[:100]}...",
            action="analyze",
        )
        session.add_step(
            thought="Drawing conclusions...",
            action="conclude",
        )

    return session.get_summary()


def extract_insights(session_id: str) -> dict:
    """Extract key insights from a thinking session."""
    if session_id not in _sessions:
        return {"error": "Session not found"}

    session = _sessions[session_id]
    insights = []

    for step in session.steps:
        if step.get("action"):
            insights.append({
                "step": step["step"],
                "action": step["action"],
                "insight": step["thought"][:200],
            })

    return {
        "session_id": session_id,
        "insights": insights,
        "total_steps": len(session.steps),
    }