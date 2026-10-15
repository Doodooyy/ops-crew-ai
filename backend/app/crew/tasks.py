"""CrewAI Task Definitions for OpsCrew AI.

Ensures tasks return strict Pydantic models representing 'Sticky Note' advice.
"""

from typing import Optional
from app.models.schemas import StickyNoteAdvice

try:
    from crewai import Task
except ImportError:
    Task = None


def create_sticky_note_task(agent, client_name: str, issue_title: str, issue_description: str) -> "Task":
    """Creates a task configured with output_pydantic=StickyNoteAdvice."""
    if Task is None:
        raise RuntimeError("CrewAI is not installed in the current environment.")

    return Task(
        description=(
            f"You are evaluating a critical client issue for our operations desk.\n\n"
            f"Client: {client_name}\n"
            f"Issue Title: {issue_title}\n"
            f"Dossier Brief: {issue_description}\n\n"
            f"Analyze this situation strictly from your persona's vantage point.\n"
            "Deliver a concise 1 to 2 sentence recommendation styled as an executive desk sticky note.\n"
            "Estimate the quantitative operational impact of following your recommendation:\n"
            "- cash_impact (in dollars, e.g. +750.0, -200.0, or 0.0)\n"
            "- rep_impact (reputation score delta between -20 and +20)\n"
            "- bandwidth_impact (bandwidth units delta between -4 and +4)\n\n"
            "Set agent_name exactly to your persona name ('Penny', 'Barnaby', or 'Sarge')."
        ),
        expected_output=(
            "A structured StickyNoteAdvice object containing: agent_name, advice_text, "
            "cash_impact, rep_impact, and bandwidth_impact."
        ),
        agent=agent,
        output_pydantic=StickyNoteAdvice,
    )
