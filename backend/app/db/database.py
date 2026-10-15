from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session, select
from app.config import settings
from app.models.schemas import UserStats, Dossier

def get_engine():
    db_path = Path(settings.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sqlite_url = f"sqlite:///{db_path}"
    # check_same_thread=False allows FastAPI worker threads to safely share connection pool
    return create_engine(sqlite_url, connect_args={"check_same_thread": False})

engine = get_engine()

def init_db():
    """Initializes SQLite database and tables via SQLModel, ensuring seed UserStats exists."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
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

def get_session():
    """FastAPI dependency for database session management."""
    with Session(engine) as session:
        yield session
