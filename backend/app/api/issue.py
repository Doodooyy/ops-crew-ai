import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.schemas import (
    UserStats,
    Dossier,
    StickyNoteAdvice,
    DeliberateRequest,
    DeliberateResponse,
    DecideRequest,
    DecideResponse,
)
from app.crew.crew import orchestrator

router = APIRouter()


@router.post("/deliberate", response_model=DeliberateResponse)
def deliberate_issue(
    request: DeliberateRequest,
    session: Session = Depends(get_session),
):
    """POST /api/issue/deliberate
    Runs the CrewAI multi-agent panel (Penny, Barnaby, Sarge) on a client issue
    and persists their strict StickyNoteAdvice recommendations in SQLite.
    """
    dossier: Optional[Dossier] = None
    if request.dossier_id:
        dossier = session.get(Dossier, request.dossier_id)
        if not dossier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dossier with ID {request.dossier_id} not found."
            )
        # Update details if provided
        dossier.client_name = request.client_name or dossier.client_name
        dossier.title = request.title or dossier.title
        dossier.description = request.description or dossier.description
    else:
        dossier = Dossier(
            client_name=request.client_name or "Acme Corp",
            title=request.title,
            description=request.description,
            category=request.category or "dispute",
            priority=request.priority or "medium",
            status="pending",
        )
        session.add(dossier)
        session.commit()
        session.refresh(dossier)

    # Run CrewAI Multi-Agent Deliberation
    advice_list: List[StickyNoteAdvice] = orchestrator.deliberate(
        client_name=dossier.client_name,
        title=dossier.title,
        description=dossier.description,
    )

    # Save serialized sticky note notes to Dossier
    serialized_notes = json.dumps([note.model_dump() for note in advice_list])
    dossier.advice_notes = serialized_notes
    dossier.status = "deliberated"

    session.add(dossier)
    session.commit()
    session.refresh(dossier)

    return DeliberateResponse(
        dossier_id=dossier.id,
        client_name=dossier.client_name,
        title=dossier.title,
        description=dossier.description,
        status=dossier.status,
        advice_notes=advice_list,
    )


@router.post("/decide", response_model=DecideResponse)
def decide_issue(
    request: DecideRequest,
    session: Session = Depends(get_session),
):
    """POST /api/issue/decide
    Applies the user's stamp of approval (e.g. APPROVED, REJECTED, COMPROMISED)
    and selected agent advice to update the SQLite state for UserStats and Dossier.
    """
    dossier = session.get(Dossier, request.dossier_id)
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dossier with ID {request.dossier_id} not found."
        )

    if not dossier.advice_notes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This dossier has not been deliberated by the CrewAI agents yet."
        )

    # Parse advice notes
    raw_notes = json.loads(dossier.advice_notes)
    advice_map = {n["agent_name"].lower(): StickyNoteAdvice(**n) for n in raw_notes}

    chosen_key = request.chosen_agent.strip().lower()
    if chosen_key not in advice_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid agent '{request.chosen_agent}'. "
                f"Available agents: {[n['agent_name'] for n in raw_notes]}"
            )
        )

    applied_advice = advice_map[chosen_key]

    # Retrieve and update UserStats
    statement = select(UserStats).where(UserStats.id == 1)
    user_stats = session.exec(statement).first()
    if not user_stats:
        user_stats = UserStats(id=1, cash=5000.0, reputation=50, bandwidth=10, max_bandwidth=10)
        session.add(user_stats)
        session.commit()
        session.refresh(user_stats)

    # Apply impacts
    user_stats.cash = round(user_stats.cash + applied_advice.cash_impact, 2)
    user_stats.reputation = max(0, min(100, user_stats.reputation + applied_advice.rep_impact))
    user_stats.bandwidth = max(0, min(user_stats.max_bandwidth, user_stats.bandwidth + applied_advice.bandwidth_impact))
    user_stats.updated_at = datetime.utcnow().isoformat()

    # Update Dossier record
    dossier.chosen_agent = applied_advice.agent_name
    dossier.chosen_decision = applied_advice.advice_text
    dossier.stamp = request.stamp.upper()
    dossier.cash_impact = applied_advice.cash_impact
    dossier.rep_impact = applied_advice.rep_impact
    dossier.bandwidth_impact = applied_advice.bandwidth_impact
    dossier.status = "decided"
    dossier.decided_at = datetime.utcnow().isoformat()

    session.add(user_stats)
    session.add(dossier)
    session.commit()
    session.refresh(user_stats)
    session.refresh(dossier)

    return DecideResponse(
        success=True,
        dossier=dossier,
        user_stats=user_stats,
        applied_advice=applied_advice,
    )


@router.get("/dossiers", response_model=List[Dossier])
def list_dossiers(session: Session = Depends(get_session)):
    """Lists all dossiers tracked on the operations desk."""
    statement = select(Dossier).order_by(Dossier.id.desc())
    return session.exec(statement).all()
