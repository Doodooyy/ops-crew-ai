"""CrewAI Orchestrator for OpsCrew AI.

Coordinates the 3 distinct personas (Penny, Barnaby, Sarge) to deliberate
on client issues and output strict StickyNoteAdvice models.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from app.models.schemas import StickyNoteAdvice
from app.crew.agents import (
    create_penny_profit_maximizer,
    create_barnaby_client_success,
    create_sarge_risk_watchdog,
)
from app.crew.tasks import create_sticky_note_task

logger = logging.getLogger("ops_crew.orchestrator")

try:
    from crewai import Crew, Process
except ImportError:
    Crew = None
    Process = None


class CrewOrchestrator:
    """Manages multi-agent deliberation on client dossiers."""

    def __init__(self, llm=None):
        self.llm = llm

    def _fallback_deliberation(
        self, client_name: str, title: str, description: str
    ) -> List[StickyNoteAdvice]:
        """Provides high-fidelity, persona-aligned advice when LLM keys are absent or offline."""
        logger.info("Using persona simulation fallback for deliberation.")
        return [
            StickyNoteAdvice(
                agent_name="Penny",
                advice_text=(
                    f"Invoice {client_name} an immediate +$600 change-order surcharge for '{title}'. "
                    "Do not deliver a single additional line of work until payment clears into our operating ledger."
                ),
                cash_impact=600.0,
                rep_impact=-6,
                bandwidth_impact=-1,
            ),
            StickyNoteAdvice(
                agent_name="Barnaby",
                advice_text=(
                    f"Offer {client_name} a complimentary priority consultation and absorb the revision costs gracefully. "
                    "A personalized executive apology will disarm their frustration and secure their 5-star renewal."
                ),
                cash_impact=-150.0,
                rep_impact=14,
                bandwidth_impact=-2,
            ),
            StickyNoteAdvice(
                agent_name="Sarge",
                advice_text=(
                    f"Strictly enforce the signed Statement of Work for '{title}'. "
                    "Reject out-of-scope demands and freeze new requests to shield our operational bandwidth from burnout."
                ),
                cash_impact=0.0,
                rep_impact=-3,
                bandwidth_impact=2,
            ),
        ]

    def deliberate(
        self, client_name: str, title: str, description: str
    ) -> List[StickyNoteAdvice]:
        """Runs Penny, Barnaby, and Sarge on the issue, returning 3 strict StickyNoteAdvice objects."""
        # Check if OpenAI or alternative LLM API key is present
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key or Crew is None:
            return self._fallback_deliberation(client_name, title, description)

        try:
            penny = create_penny_profit_maximizer(self.llm)
            barnaby = create_barnaby_client_success(self.llm)
            sarge = create_sarge_risk_watchdog(self.llm)

            penny_task = create_sticky_note_task(penny, client_name, title, description)
            barnaby_task = create_sticky_note_task(barnaby, client_name, title, description)
            sarge_task = create_sticky_note_task(sarge, client_name, title, description)

            crew = Crew(
                agents=[penny, barnaby, sarge],
                tasks=[penny_task, barnaby_task, sarge_task],
                process=Process.sequential,
                verbose=True,
            )

            crew.kickoff()

            results: List[StickyNoteAdvice] = []
            for t in [penny_task, barnaby_task, sarge_task]:
                if hasattr(t, "output") and t.output and hasattr(t.output, "pydantic") and t.output.pydantic:
                    results.append(t.output.pydantic)
                else:
                    logger.warning(f"Task output for agent {t.agent.role} did not contain pydantic output.")

            # If all 3 were parsed, return them; otherwise fill in via fallback
            if len(results) == 3:
                return results
            else:
                return self._fallback_deliberation(client_name, title, description)

        except Exception as exc:
            logger.error(f"Error during CrewAI execution: {exc}. Falling back to persona deliberation.")
            return self._fallback_deliberation(client_name, title, description)


orchestrator = CrewOrchestrator()
