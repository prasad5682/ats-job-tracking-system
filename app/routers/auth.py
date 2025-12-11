from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import timedelta

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------
# 🔐 Hash Password
# ---------------------------------------------------------
def hash_password(password: str):
    return pwd_context.hash(password)


# ---------------------------------------------------------
# 🔐 Verify Password
# ---------------------------------------------------------
def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)


# ---------------------------------------------------------
# ✅ 1. REGISTER USER (Candidate / Recruiter / Hiring Manager)
# ---------------------------------------------------------
@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    # Check if email exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pw = hash_password(user.password)

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hashed_pw,
        role=user.role,
        company_id=user.company_id  # recruiter/hiring_manager can belong to a company
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }


# ---------------------------------------------------------
# ✅ 2. LOGIN & GET JWT TOKEN
# ---------------------------------------------------------
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"user_id": db_user.id, "role": db_user.role},
        expires_delta=access_token_expires
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": db_user.role,
        "user_id": db_user.id
    }
