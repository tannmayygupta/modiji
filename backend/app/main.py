"""
PM Internship Recommendation Engine — FastAPI Application Entry Point.

Run with: uvicorn app.main:app --reload --port 8000
Docs at:  http://localhost:8000/docs
"""
import os
import sys

# Inject root directory into python path so we can import 'ml' from the sibling folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.session import Base, engine
from app.api.v1 import auth, candidates, internships, recommendations, interactions, admin, resume, digilocker, documents

settings = get_settings()


def create_tables():
    """Create all database tables (dev only — use Alembic in production)."""
    Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "AI-powered recommendation engine for the PM Internship Scheme. "
        "Matches candidates with internship opportunities using hybrid "
        "content-based and collaborative filtering with affirmative action scoring."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — Fully permissive for local development. 
# We use Bearer tokens in headers, so allow_credentials=True is not required.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables and load ML models on startup."""
    create_tables()
    print(f">> {settings.PROJECT_NAME} started successfully")
    print(f">> API docs at http://localhost:8000/docs")


# ── Register API Routers ─────────────────────────────────

app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"],
)

app.include_router(
    candidates.router,
    prefix=f"{settings.API_V1_PREFIX}/candidates",
    tags=["Candidates"],
)

app.include_router(
    internships.router,
    prefix=f"{settings.API_V1_PREFIX}/internships",
    tags=["Internships"],
)

app.include_router(
    recommendations.router,
    prefix=f"{settings.API_V1_PREFIX}/recommendations",
    tags=["Recommendations"],
)

app.include_router(
    interactions.router,
    prefix=f"{settings.API_V1_PREFIX}/interactions",
    tags=["Interactions"],
)

app.include_router(
    resume.router,
    prefix=f"{settings.API_V1_PREFIX}/resume",
    tags=["Resume"],
)

app.include_router(
    admin.router,
    prefix=f"{settings.API_V1_PREFIX}/admin",
    tags=["Admin & Analytics"],
)

app.include_router(
    digilocker.router,
    prefix=f"{settings.API_V1_PREFIX}/digilocker",
    tags=["DigiLocker Auth"],
)

app.include_router(
    documents.router,
    prefix=f"{settings.API_V1_PREFIX}/documents",
    tags=["Documents & Verification"],
)


# ── Health Check ──────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "0.1.0",
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "PM Internship Recommendation Engine API",
        "docs": "/docs",
        "health": "/health",
    }
 
