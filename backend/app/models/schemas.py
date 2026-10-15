from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, Field as PydanticField


# ---------------------------------------------------------------------------
# Strict Pydantic Models for CrewAI Agent Output ("Sticky Note" Advice)
# ---------------------------------------------------------------------------

class StickyNoteAdvice(BaseModel):
    """Structured Sticky Note recommendation produced by an agent."""
    agent_name: str = PydanticField(
        description="The persona providing advice: 'Penny', 'Barnaby', or 'Sarge'"
    )
    advice_text: str = PydanticField(
        description="Crisp 1-3 sentence strategic recommendation formatted as a desk sticky note"
    )
    cash_impact: float = PydanticField(
        description="Estimated net cash flow impact in dollars (can be positive or negative)"
    )
    rep_impact: int = PydanticField(
        description="Estimated reputation score change points (e.g., -15 to +15)"
    )
    bandwidth_impact: int = PydanticField(
        description="Estimated bandwidth overhead/recovery in units (e.g., -3 to +3)"
    )


# ---------------------------------------------------------------------------
# SQLModel Database Tables
# ---------------------------------------------------------------------------

class UserStats(SQLModel, table=True):
    """Tracks core solopreneur business metrics: Cash Flow, Reputation, and Bandwidth."""
    __tablename__ = "user_stats"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(default="Solo Operator")
    cash: float = Field(default=5000.0, description="Available liquid cash flow ($)")
    reputation: int = Field(default=50, description="Reputation score (0-100)")
    bandwidth: int = Field(default=10, description="Available operational bandwidth units")
    max_bandwidth: int = Field(default=10, description="Maximum total bandwidth capacity")
    level: int = Field(default=1, description="Company operational tier")
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Dossier(SQLModel, table=True):
    """Tracks client issues, agent sticky notes, user stamps, and final decisions."""
    __tablename__ = "dossiers"

    id: Optional[int] = Field(default=None, primary_key=True)
    client_name: str = Field(default="Acme Corp")
    title: str = Field(index=True)
    description: str
    category: str = Field(default="client_dispute")  # dispute | pricing | scope_creep | rush_order
    priority: str = Field(default="medium")          # low | medium | high | urgent
    status: str = Field(default="pending")           # pending | deliberated | decided

    # JSON-encoded list of StickyNoteAdvice
    advice_notes: Optional[str] = Field(
        default=None, 
        description="JSON array storing StickyNoteAdvice objects from Penny, Barnaby, and Sarge"
    )

    # User's final stamp and chosen path
    chosen_agent: Optional[str] = Field(default=None)   # "Penny" | "Barnaby" | "Sarge"
    chosen_decision: Optional[str] = Field(default=None) # Brief note of selected course
    stamp: Optional[str] = Field(default=None)           # "APPROVED" | "REJECTED" | "COMPROMISED"

    # Applied impacts after user decision
    cash_impact: float = Field(default=0.0)
    rep_impact: int = Field(default=0)
    bandwidth_impact: int = Field(default=0)

    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    decided_at: Optional[str] = Field(default=None)


# ---------------------------------------------------------------------------
# API Request & Response Schemas
# ---------------------------------------------------------------------------

class DeliberateRequest(BaseModel):
    dossier_id: Optional[int] = None
    client_name: Optional[str] = "Acme Corp"
    title: str = PydanticField(..., description="Summary of the client dilemma")
    description: str = PydanticField(..., description="Detailed description of the issue")
    category: Optional[str] = "dispute"
    priority: Optional[str] = "medium"


class DeliberateResponse(BaseModel):
    dossier_id: int
    title: str
    description: str
    client_name: str
    status: str
    advice_notes: List[StickyNoteAdvice]


class DecideRequest(BaseModel):
    dossier_id: int
    chosen_agent: str = PydanticField(..., description="Penny | Barnaby | Sarge")
    stamp: str = PydanticField(default="APPROVED", description="APPROVED | REJECTED | COMPROMISED")
    custom_notes: Optional[str] = None


class DecideResponse(BaseModel):
    success: bool
    dossier: Dossier
    user_stats: UserStats
    applied_advice: StickyNoteAdvice
