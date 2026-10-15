from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.schemas import UserStats

router = APIRouter()

@router.get("/", response_model=UserStats)
def get_current_stats(session: Session = Depends(get_session)):
    """Fetch current user cash, reputation, and bandwidth metrics."""
    statement = select(UserStats).where(UserStats.id == 1)
    user = session.exec(statement).first()
    if not user:
        user = UserStats(
            id=1,
            username="Solo Operator",
            cash=5000.0,
            reputation=50,
            bandwidth=10,
            max_bandwidth=10,
            level=1
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    return user
