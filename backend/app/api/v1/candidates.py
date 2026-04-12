"""
Candidate Profile API Routes.
Handles profile retrieval, wizard submission, and profile updates.
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
import json

from app.services.video_analysis import process_video_intro

from app.db.session import get_db
from app.models.candidate import Candidate, EducationLevel, SocialCategory, LocationPreference
from app.schemas.schemas import WizardSubmission, CandidateProfile
from app.api.v1.auth import get_current_user

router = APIRouter()


# Map of Indian states to aspirational districts (subset for prototype)
ASPIRATIONAL_DISTRICTS = {
    "Jharkhand": ["Chatra", "Dumka", "Godda", "Gumla", "Khunti", "Latehar", "Pakur", "Ramgarh", "Simdega", "West Singhbhum"],
    "Bihar": ["Araria", "Aurangabad", "Banka", "Begusarai", "Gaya", "Jamui", "Katihar", "Khagaria", "Muzaffarpur", "Nawada", "Purnia", "Sheikhpura", "Sitamarhi"],
    "Madhya Pradesh": ["Barwani", "Chhatarpur", "Damoh", "Khandwa", "Rajgarh", "Singrauli", "Vidisha"],
    "Uttar Pradesh": ["Bahraich", "Balrampur", "Chandauli", "Chitrakoot", "Fatehpur", "Shravasti", "Siddharthnagar", "Sonbhadra"],
    "Rajasthan": ["Baran", "Dholpur", "Jaisalmer", "Karauli", "Sirohi"],
    "Chhattisgarh": ["Bastar", "Bijapur", "Dantewada", "Kanker", "Kondagaon", "Korba", "Mahasamund", "Narayanpur", "Rajnandgaon", "Sukma"],
    "Odisha": ["Balangir", "Dhenkanal", "Gajapati", "Kalahandi", "Kandhamal", "Koraput", "Malkangiri", "Nabarangpur", "Nuapada", "Rayagada"],
    "Maharashtra": ["Gadchiroli", "Nandurbar", "Osmanabad", "Washim"],
    "Andhra Pradesh": ["Visakhapatnam", "YSR Kadapa"],
    "Telangana": ["Asifabad", "Bhupalpally", "Khammam"],
    "Karnataka": ["Raichur", "Yadgir"],
    "Tamil Nadu": ["Ramanathapuram", "Virudhunagar"],
    "Assam": ["Baksa", "Darrang", "Dhubri", "Goalpara", "Hailakandi", "Udalguri"],
    "Nagaland": ["Kiphire"],
    "Manipur": ["Chandel", "Noney"],
    "Meghalaya": ["Ribhoi"],
    "Mizoram": ["Mamit"],
    "Arunachal Pradesh": ["Namsai"],
}


def is_aspirational_district(state: str, district: str) -> bool:
    """Check if a district is in the government's aspirational district list."""
    if not state or not district:
        return False
    districts = ASPIRATIONAL_DISTRICTS.get(state, [])
    return district.lower() in [d.lower() for d in districts]


@router.get("/me", response_model=CandidateProfile)
def get_profile(current_user: Candidate = Depends(get_current_user)):
    """Get the current candidate's full profile."""
    return CandidateProfile(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        education_level=current_user.education_level.value if current_user.education_level else None,
        field_of_study=current_user.field_of_study,
        academic_score=current_user.academic_score,
        skills=current_user.skills or [],
        state=current_user.state,
        district=current_user.district,
        is_rural=current_user.is_rural,
        social_category=current_user.social_category.value if current_user.social_category else None,
        sector_preferences=current_user.sector_preferences or [],
        location_preference=current_user.location_preference.value if current_user.location_preference else None,
        preferred_language=current_user.preferred_language,
        has_past_participation=current_user.has_past_participation,
        created_at=current_user.created_at,
    )


@router.post("/me/wizard", response_model=CandidateProfile)
def submit_wizard(
    wizard_data: WizardSubmission,
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit complete wizard data (all 4 steps).
    Updates the candidate's profile with education, skills, sector preferences, and location.
    """
    # Step 1: Education
    current_user.education_level = EducationLevel(wizard_data.education_level)
    current_user.field_of_study = wizard_data.field_of_study
    current_user.academic_score = wizard_data.academic_score

    # Step 2: Skills
    current_user.skills = wizard_data.skills

    # Step 3: Sectors
    current_user.sector_preferences = wizard_data.sector_preferences

    # Step 4: Location
    current_user.state = wizard_data.state
    current_user.district = wizard_data.district
    current_user.location_preference = LocationPreference(wizard_data.location_preference)

    # Auto-detect aspirational district
    current_user.is_aspirational_district = is_aspirational_district(
        wizard_data.state, wizard_data.district
    )

    # Demographics (optional)
    if wizard_data.social_category:
        current_user.social_category = SocialCategory(wizard_data.social_category)
    if wizard_data.preferred_language:
        current_user.preferred_language = wizard_data.preferred_language

    db.commit()
    db.refresh(current_user)

    return CandidateProfile(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        education_level=current_user.education_level.value,
        field_of_study=current_user.field_of_study,
        academic_score=current_user.academic_score,
        skills=current_user.skills or [],
        state=current_user.state,
        district=current_user.district,
        is_rural=current_user.is_rural,
        social_category=current_user.social_category.value if current_user.social_category else None,
        sector_preferences=current_user.sector_preferences or [],
        location_preference=current_user.location_preference.value if current_user.location_preference else None,
        preferred_language=current_user.preferred_language,
        has_past_participation=current_user.has_past_participation,
        created_at=current_user.created_at,
    )


@router.put("/me", response_model=CandidateProfile)
def update_profile(
    updates: dict,
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update specific fields of the candidate's profile."""
    allowed_fields = {
        "name", "phone", "education_level", "field_of_study", "academic_score",
        "skills", "state", "district", "is_rural", "social_category",
        "sector_preferences", "location_preference", "preferred_language",
    }

    for key, value in updates.items():
        if key in allowed_fields and hasattr(current_user, key):
            if key == "education_level":
                value = EducationLevel(value)
            elif key == "social_category":
                value = SocialCategory(value)
            elif key == "location_preference":
                value = LocationPreference(value)
            setattr(current_user, key, value)

    # Recheck aspirational district
    if "district" in updates or "state" in updates:
        current_user.is_aspirational_district = is_aspirational_district(
            current_user.state, current_user.district
        )

    db.commit()
    db.refresh(current_user)

    return CandidateProfile(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        education_level=current_user.education_level.value if current_user.education_level else None,
        field_of_study=current_user.field_of_study,
        academic_score=current_user.academic_score,
        skills=current_user.skills or [],
        state=current_user.state,
        district=current_user.district,
        is_rural=current_user.is_rural,
        social_category=current_user.social_category.value if current_user.social_category else None,
        sector_preferences=current_user.sector_preferences or [],
        location_preference=current_user.location_preference.value if current_user.location_preference else None,
        preferred_language=current_user.preferred_language,
        has_past_participation=current_user.has_past_participation,
        created_at=current_user.created_at,
        video_uploaded=current_user.video_uploaded,
        video_url=current_user.video_url,
        video_comm_score=current_user.video_comm_score,
        video_conf_score=current_user.video_conf_score,
        video_clarity_score=current_user.video_clarity_score,
        video_overall_score=current_user.video_overall_score
    )


@router.post("/upload-video")
async def upload_video_intro(
    file: UploadFile = File(...),
    current_user: Candidate = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a video/audio intro. Groq Whisper transcribes it,
    Llama 3.3 analyzes communication quality, and scores are saved.
    """
    allowed_types = [
        "video/mp4", "video/webm", "video/quicktime",
        "audio/mpeg", "audio/wav", "audio/mp3", "audio/x-wav",
    ]
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    video_bytes = await file.read()
    if len(video_bytes) > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=400, detail="File too large. Max 50MB.")

    try:
        result = process_video_intro(video_bytes, file.filename or "video.mp4")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")

    # Before saving to DB, upload original video to Supabase so Admins can watch it
    from app.services.supabase_storage import upload_file_to_supabase
    
    try:
        supabase_video_url = upload_file_to_supabase(
            file_bytes=video_bytes,
            file_name=file.filename or "video.mp4",
            bucket_name="pmis-media",
            folder_name="videos",
            content_type=file.content_type or "video/mp4"
        )
    except Exception as e:
        print(f"Supabase video upload failed or skipped: {e}")
        supabase_video_url = None

    # Save scores and URL to DB
    current_user.video_uploaded = True
    current_user.video_url = supabase_video_url  # Save Cloud URL

    current_user.video_transcript = result.get("transcript", "")
    current_user.video_comm_score = result.get("communication_score", 0)
    current_user.video_conf_score = result.get("confidence_score", 0)
    current_user.video_clarity_score = result.get("clarity_score", 0)
    current_user.video_overall_score = result.get("overall_score", 0)
    current_user.video_skills_detected = json.dumps(result.get("skills_mentioned", []))
    current_user.video_sectors_detected = json.dumps(result.get("sectors_mentioned", []))
    current_user.video_is_bilingual = result.get("is_bilingual", False)
    current_user.video_pace = result.get("speech_pace", "moderate")

    db.commit()
    db.refresh(current_user)

    return {
        "status": "success",
        "scores": {
            "communication_score": result.get("communication_score", 0),
            "confidence_score": result.get("confidence_score", 0),
            "clarity_score": result.get("clarity_score", 0),
            "overall_score": result.get("overall_score", 0),
            "top_strength": result.get("top_strength", ""),
            "feedback": result.get("feedback_for_candidate", ""),
        },
        "transcript_preview": result.get("transcript", "")[:200],
    }
