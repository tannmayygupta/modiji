from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.session import get_db
from app.models.candidate import Candidate
from app.api.v1.auth import get_current_user
from app.services.aadhaar_parser import parse_aadhaar_zip, AadhaarParserError

router = APIRouter()


@router.post("/verify-aadhaar")
async def verify_aadhaar(
    file: UploadFile = File(...),
    share_code: str = Form(...),
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Step 1 → Step 2: Verify the candidate's Aadhaar using offline XML ZIP.
    Extracts name, DOB, and district securely. NEVER stores raw XML.
    """
    if current_user.auth_step >= 2:
        raise HTTPException(status_code=409, detail="Aadhaar already verified for this account.")

    # Read uploaded zip bytes
    zip_bytes = await file.read()
    
    try:
        profile_data = parse_aadhaar_zip(zip_bytes, share_code)
    except AadhaarParserError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Age check
    if not profile_data["is_eligible"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Age must be between 18 and 25 to apply for PMIS. You are {profile_data['age']} years old."
        )

    # Store the parsed name and address to Candidate profile
    current_user.aadhaar_name = profile_data["full_name"]
    current_user.state = profile_data["state"]
    current_user.district = profile_data["district"]
    current_user.is_rural = profile_data["is_rural"]
    current_user.auth_step = 2  # ADVANCE TO STEP 2

    # Option: store additional demographics in metadata JSON if tracking
    if not current_user.metadata_json:
        current_user.metadata_json = {}
    current_user.metadata_json.update({
        "aadhaar_age": profile_data["age"],
        "aadhaar_gender": profile_data["gender"],
        "aadhaar_pincode": profile_data["pincode"],
        "aadhaar_verified_at": "now" # In real app use datetime
    })

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Aadhaar verified successfully. You can now upload education documents.",
        "profile": profile_data,
        "auth_step": current_user.auth_step,
        "aadhaar_name": current_user.aadhaar_name,
    }


@router.get("/auth-status")
def get_auth_status(current_user: Candidate = Depends(get_current_user)):
    """Returns the candidate's current authentication level and what they can access."""
    access_map = {
        1: {"can_browse": True, "can_upload_docs": False, "can_apply": False, "next_action": "Verify Aadhaar"},
        2: {"can_browse": True, "can_upload_docs": True, "can_apply": False, "next_action": "Upload 10th/12th marksheets"},
        3: {"can_browse": True, "can_upload_docs": True, "can_apply": True, "next_action": "Fully verified — apply to internships"},
    }

    return {
        "auth_step": current_user.auth_step,
        "name": current_user.name,
        "aadhaar_name": current_user.aadhaar_name,
        "access": access_map.get(current_user.auth_step, access_map[1]),
    }

