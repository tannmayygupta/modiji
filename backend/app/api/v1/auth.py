"""
Authentication API Routes.
Handles registration, login, and JWT token management.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.db.session import get_db
from app.config import get_settings
from app.models.candidate import Candidate
from app.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse

try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth
    from firebase_admin import credentials
    # Intialize globally - relies on FIREBASE_CREDENTIALS_PATH environment variable or default
    if not firebase_admin._apps:
        # NOTE: Without credentials, this app requires GOOGLE_APPLICATION_CREDENTIALS in prod
        firebase_admin.initialize_app()
except ImportError:
    pass

router = APIRouter()
settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Candidate:
    """Extract and validate the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Candidate).filter(Candidate.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new candidate account."""
    # Check if email already exists
    existing = db.query(Candidate).filter(Candidate.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    candidate = Candidate(
        name=req.name,
        email=req.email,
        password_hash=hash_password(req.password),
        phone=req.phone,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    token = create_access_token({"sub": str(candidate.id)})
    return TokenResponse(access_token=token, user_id=str(candidate.id))


class FirebaseOTPRequest(BaseModel):
    firebase_id_token: str
    phone: str

@router.post("/verify-phone", response_model=TokenResponse)
def verify_firebase_phone(req: FirebaseOTPRequest, db: Session = Depends(get_db)):
    """
    Verify Firebase OTP token. 
    If valid, get or create the user based on firebase_uid and return our JWT.
    """
    try:
        # In a real environment, this validates the JWT signature against Firebase
        decoded_token = firebase_auth.verify_id_token(req.firebase_id_token)
        firebase_uid = decoded_token['uid']
    except Exception as e:
        # Dev bypass: frontend sends dev_bypass_token_<phone> when NODE_ENV=development
        if req.firebase_id_token.startswith("dev_bypass_token_"):
            firebase_uid = f"dev_uid_{req.phone.replace('+', '').replace(' ', '')}"
        # Legacy simulated token support
        elif "simulated_token_" in req.firebase_id_token:
            firebase_uid = req.firebase_id_token.replace("simulated_token_", "uid_")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Firebase ID token: {str(e)}"
            )

    # Standardize phone number format completely to prevent mismatch
    clean_phone = req.phone.replace(" ", "").strip()
    if clean_phone.startswith("+91"):
        clean_phone = clean_phone[3:]
    elif clean_phone.startswith("0"):
        clean_phone = clean_phone[1:]

    # Check if candidate exists by their cleaned phone number OR their +91 version
    candidate = db.query(Candidate).filter(
        (Candidate.phone == clean_phone) | (Candidate.phone == f"+91{clean_phone}")
    ).first()
    
    if not candidate:
        import uuid
        # Creating placeholder user with a globally unique email to bypass SQLite UNIQUE constraint
        candidate = Candidate(
            name="New User (OTP)",
            email=f"otp_{uuid.uuid4().hex[:8]}@pmis.gov.in",
            phone=f"+91{clean_phone}",
            password_hash=hash_password(firebase_uid[:16]),
            auth_step=1,
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    token = create_access_token({"sub": str(candidate.id)})
    return TokenResponse(access_token=token, user_id=str(candidate.id))

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password."""
    candidate = db.query(Candidate).filter(Candidate.email == req.email).first()
    if not candidate or not verify_password(req.password, candidate.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({"sub": str(candidate.id)})
    return TokenResponse(access_token=token, user_id=str(candidate.id))


@router.get("/me")
def get_me(current_user: Candidate = Depends(get_current_user)):
    """Get the currently authenticated user's basic info and auth level."""
    access_map = {
        1: {"can_browse": True, "can_upload_docs": False, "can_apply": False},
        2: {"can_browse": True, "can_upload_docs": True, "can_apply": False},
        3: {"can_browse": True, "can_upload_docs": True, "can_apply": True},
    }
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "auth_step": current_user.auth_step,
        "aadhaar_name": current_user.aadhaar_name,
        "has_completed_wizard": bool(current_user.skills),
        "access": access_map.get(current_user.auth_step, access_map[1]),
    }
