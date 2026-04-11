"""
Pydantic Schemas for request/response validation.
Handles serialization between API layer and database models.
"""
from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator


# ──────────────────────────────────────────────
# Auth Schemas
# ──────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


# ──────────────────────────────────────────────
# Candidate Schemas
# ──────────────────────────────────────────────

class WizardStep1(BaseModel):
    """Step 1: Education Level"""
    education_level: str = Field(..., description="10TH, 12TH, ITI, DIPLOMA, GRADUATE, PG")
    field_of_study: Optional[str] = None
    academic_score: Optional[float] = Field(None, ge=0, le=100)


class WizardStep2(BaseModel):
    """Step 2: Skills Selection"""
    skills: list[str] = Field(..., min_length=1, max_length=20)


class WizardStep3(BaseModel):
    """Step 3: Sector Interests"""
    sector_preferences: list[str] = Field(..., min_length=1, max_length=5)


class WizardStep4(BaseModel):
    """Step 4: Location Preference"""
    state: str
    district: Optional[str] = None
    location_preference: str = Field(..., description="HOME_STATE, NEARBY, PAN_INDIA")


class WizardSubmission(BaseModel):
    """Complete wizard data (all 4 steps combined)."""
    # Step 1
    education_level: str
    field_of_study: Optional[str] = None
    academic_score: Optional[float] = Field(None, ge=0, le=100)
    # Step 2
    skills: list[str]
    # Step 3
    sector_preferences: list[str]
    # Step 4
    state: str
    district: Optional[str] = None
    location_preference: str = "HOME_STATE"
    # Optional demographics
    social_category: Optional[str] = "GENERAL"
    preferred_language: Optional[str] = "en"


class CandidateProfile(BaseModel):
    """Full candidate profile response."""
    id: str
    name: str
    email: str
    education_level: str
    field_of_study: Optional[str] = None
    academic_score: Optional[float] = None
    skills: list[str] = []
    state: Optional[str] = None
    district: Optional[str] = None
    is_rural: bool = False
    social_category: Optional[str] = None
    sector_preferences: list[str] = []
    location_preference: Optional[str] = None
    preferred_language: str = "en"
    has_past_participation: bool = False
    created_at: Optional[datetime] = None

    # Video AI Integration
    video_uploaded: bool = False
    video_url: Optional[str] = None
    video_comm_score: Optional[int] = None
    video_conf_score: Optional[int] = None
    video_clarity_score: Optional[int] = None
    video_overall_score: Optional[int] = None

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# Internship Schemas
# ──────────────────────────────────────────────

class InternshipCreate(BaseModel):
    """Schema for creating a new internship."""
    company_name: str
    company_description: Optional[str] = None
    role_title: str
    description: str
    required_skills: list[str] = []
    min_education: str
    preferred_fields: list[str] = []
    sector: str
    city: str
    state: str
    stipend_amount: Optional[float] = None
    capacity: int
    duration_months: int = 12
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class InternshipResponse(BaseModel):
    """Internship listing response."""
    id: str
    company_name: str
    company_description: Optional[str] = None
    role_title: str
    description: str
    required_skills: list[str] = []
    min_education: str
    preferred_fields: list[str] = []
    sector: str
    city: str
    state: str
    stipend_amount: Optional[float] = None
    capacity: int
    filled_count: int
    available_slots: int = 0
    duration_months: int = 12
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class InternshipListResponse(BaseModel):
    """Paginated internship list."""
    items: list[InternshipResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ──────────────────────────────────────────────
# Recommendation Schemas
# ──────────────────────────────────────────────

class SkillAlignment(BaseModel):
    matched: list[str] = []
    partial: list[str] = []
    missing: list[str] = []


class MatchReason(BaseModel):
    icon: str
    text: str
    category: str  # "education", "skills", "location", "sector"


class RecommendationExplanation(BaseModel):
    match_percentage: int = Field(..., ge=0, le=100)
    reasons: list[MatchReason] = []
    skill_alignment: Optional[SkillAlignment] = None


class RecommendationCard(BaseModel):
    """Single recommendation card shown to the user."""
    id: str
    internship_id: str
    company_name: str
    role_title: str
    match_percentage: int
    sector: str
    city: str
    state: str
    stipend_amount: Optional[float] = None
    explanation: RecommendationExplanation
    display_rank: int

    class Config:
        from_attributes = True


class RecommendationListResponse(BaseModel):
    """List of personalized recommendations."""
    candidate_id: str
    recommendations: list[RecommendationCard]
    generated_at: datetime
    engine_version: str = "hybrid-v1"


# ──────────────────────────────────────────────
# Interaction Schemas
# ──────────────────────────────────────────────

class InteractionCreate(BaseModel):
    internship_id: str
    interaction_type: str = Field(..., description="VIEW, SAVE, APPLY, ACCEPT, REJECT, COMPLETE")


class FeedbackCreate(BaseModel):
    recommendation_id: str
    is_positive: bool  # thumbs up / thumbs down


# ──────────────────────────────────────────────
# Admin / Analytics Schemas
# ──────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_candidates: int
    total_internships: int
    total_applications: int
    total_recommendations_generated: int
    avg_match_score: float
    conversion_rate: float  # applications / recommendations shown
    category_distribution: dict  # {"GENERAL": 40, "OBC": 30, ...}
    top_sectors: list[dict]  # [{"sector": "IT", "count": 150}, ...]


class ModelMetrics(BaseModel):
    precision_at_5: float
    ndcg_at_5: float
    coverage: float
    diversity_score: float
    fairness_gap: float
    avg_latency_ms: float
    last_trained_at: Optional[datetime] = None
