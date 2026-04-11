"""
Internship Listing API Routes.
Handles browsing, filtering, and detail views for internship opportunities.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import math

from app.db.session import get_db
from app.models.internship import Internship
from app.schemas.schemas import InternshipResponse, InternshipListResponse, InternshipCreate
from ml.engine.fraud_detector import FraudDetector

router = APIRouter()

# Sectors available in the PM Internship Scheme
AVAILABLE_SECTORS = [
    "IT & Software", "Banking & Finance", "Healthcare", "Manufacturing",
    "Retail & E-Commerce", "Education", "Automobile", "Telecom",
    "Energy & Power", "FMCG", "Construction & Real Estate", "Agriculture",
    "Textiles", "Pharmaceuticals", "Logistics & Supply Chain",
    "Media & Entertainment", "Hospitality & Tourism", "Legal & Compliance",
    "Government & Public Sector", "Research & Development",
    "Data Science & Analytics", "Marketing & Sales",
    "Human Resources", "Others"
]


@router.get("/", response_model=InternshipListResponse)
def list_internships(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sector: Optional[str] = None,
    state: Optional[str] = None,
    min_education: Optional[str] = None,
    search: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db),
):
    """
    List internships with filtering and pagination.
    Supports filtering by sector, state, education level, and search text.
    """
    query = db.query(Internship).filter(
        Internship.is_active == True,
        Internship.is_verified == True,
        Internship.fraud_risk_score <= 0.4
    )

    # Filters
    if sector:
        query = query.filter(Internship.sector == sector)
    if state:
        query = query.filter(Internship.state == state)
    if min_education:
        query = query.filter(Internship.min_education == min_education)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Internship.role_title.ilike(search_term)) |
            (Internship.company_name.ilike(search_term)) |
            (Internship.description.ilike(search_term))
        )

    # Total count
    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # Pagination
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return InternshipListResponse(
        items=[
            InternshipResponse(
                id=str(i.id),
                company_name=i.company_name,
                company_description=i.company_description,
                role_title=i.role_title,
                description=i.description,
                required_skills=i.required_skills or [],
                min_education=i.min_education,
                preferred_fields=i.preferred_fields or [],
                sector=i.sector,
                city=i.city,
                state=i.state,
                stipend_amount=i.stipend_amount,
                capacity=i.capacity,
                filled_count=i.filled_count,
                available_slots=i.available_slots,
                duration_months=i.duration_months,
                start_date=i.start_date,
                end_date=i.end_date,
                is_active=i.is_active,
            )
            for i in items
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/", response_model=InternshipResponse)
def create_internship(
    internship_in: InternshipCreate,
    db: Session = Depends(get_db)
):
    # Run the PMIS Fraud Detection Engine
    evaluation = FraudDetector.evaluate_internship(internship_in.model_dump())
    
    internship = Internship(
        **internship_in.model_dump(),
        is_verified=evaluation["is_verified"],
        fraud_risk_score=evaluation["fraud_risk_score"],
        verification_notes=evaluation["verification_notes"]
    )
    
    db.add(internship)
    db.commit()
    db.refresh(internship)
    return internship


@router.get("/sectors")
def list_sectors():
    """Return available internship sectors."""
    return {"sectors": AVAILABLE_SECTORS}


@router.get("/{internship_id}", response_model=InternshipResponse)
def get_internship(internship_id: str, db: Session = Depends(get_db)):
    """Get details for a specific internship."""
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    return InternshipResponse(
        id=str(internship.id),
        company_name=internship.company_name,
        company_description=internship.company_description,
        role_title=internship.role_title,
        description=internship.description,
        required_skills=internship.required_skills or [],
        min_education=internship.min_education,
        preferred_fields=internship.preferred_fields or [],
        sector=internship.sector,
        city=internship.city,
        state=internship.state,
        stipend_amount=internship.stipend_amount,
        capacity=internship.capacity,
        filled_count=internship.filled_count,
        available_slots=internship.available_slots,
        duration_months=internship.duration_months,
        start_date=internship.start_date,
        end_date=internship.end_date,
        is_active=internship.is_active,
    )
