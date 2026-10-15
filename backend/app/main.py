from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import issue, stats
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLModel SQLite database tables and seed state
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(issue.router, prefix="/api/issue", tags=["Client Issues & Deliberation"])
app.include_router(stats.router, prefix="/api/stats", tags=["User Stats & Cash Flow"])

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
