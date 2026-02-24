from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import timedelta
from sqlalchemy.orm import Session

from core.security import (
    verify_password, get_password_hash, create_access_token,
    decode_access_token, get_user_id_from_token
)
from models import User, QuestionnaireResponse, get_db
from config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    expertise_level: Optional[str] = "beginner"
    background: Optional[str] = "both"
    preferred_language: Optional[str] = "en"

class UserLogin(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    expertise_level: str
    background: str
    preferred_language: str
    learning_goals: Dict[str, Any]
    subscription_status: str
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserProfile

class QuestionnaireItem(BaseModel):
    question_id: str
    question_text: str
    response: Any

class QuestionnaireSubmit(BaseModel):
    responses: List[QuestionnaireItem]

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user

# Endpoints
@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        expertise_level=user_data.expertise_level,
        background=user_data.background,
        preferred_language=user_data.preferred_language,
        learning_goals={},
        subscription_status="free",
        is_active=True,
        is_verified=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    # Return token and user profile
    user_profile = UserProfile(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        expertise_level=user.expertise_level,
        background=user.background,
        preferred_language=user.preferred_language,
        learning_goals=user.learning_goals,
        subscription_status=user.subscription_status,
        created_at=user.created_at.isoformat()
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_profile
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    # Return token and user profile
    user_profile = UserProfile(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        expertise_level=user.expertise_level,
        background=user.background,
        preferred_language=user.preferred_language,
        learning_goals=user.learning_goals,
        subscription_status=user.subscription_status,
        created_at=user.created_at.isoformat()
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_profile
    )

@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        expertise_level=current_user.expertise_level,
        background=current_user.background,
        preferred_language=current_user.preferred_language,
        learning_goals=current_user.learning_goals,
        subscription_status=current_user.subscription_status,
        created_at=current_user.created_at.isoformat()
    )

@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_update: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    allowed_fields = ["full_name", "expertise_level", "background", "preferred_language", "learning_goals"]

    for field, value in profile_update.items():
        if field in allowed_fields and hasattr(current_user, field):
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        expertise_level=current_user.expertise_level,
        background=current_user.background,
        preferred_language=current_user.preferred_language,
        learning_goals=current_user.learning_goals,
        subscription_status=current_user.subscription_status,
        created_at=current_user.created_at.isoformat()
    )

@router.post("/questionnaire")
async def submit_questionnaire(
    questionnaire: QuestionnaireSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit questionnaire responses."""
    responses = []

    for item in questionnaire.responses:
        # Store each response
        response = QuestionnaireResponse(
            user_id=current_user.id,
            question_id=item.question_id,
            response=item.response
        )
        db.add(response)
        responses.append(response)

    # Update user's expertise level if relevant questions answered
    expertise_responses = [r for r in questionnaire.responses if r.question_id.startswith("expertise")]
    if expertise_responses:
        # Logic to determine expertise level from responses
        # For simplicity, use the first expertise response
        current_user.expertise_level = expertise_responses[0].response

    db.commit()

    return {"message": "Questionnaire submitted successfully", "responses_count": len(responses)}

@router.get("/questionnaire")
async def get_questionnaire_responses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's questionnaire responses."""
    responses = db.query(QuestionnaireResponse).filter(
        QuestionnaireResponse.user_id == current_user.id
    ).all()

    return {
        "user_id": current_user.id,
        "responses": [
            {
                "question_id": r.question_id,
                "response": r.response,
                "created_at": r.created_at.isoformat()
            }
            for r in responses
        ]
    }