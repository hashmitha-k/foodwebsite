from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import get_db, User
from auth import get_current_user, hash_password

router = APIRouter(prefix="/users", tags=["Users"])


# ─── SCHEMAS ─────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id:         int
    username:   str
    email:      str

    class Config:
        from_attributes = True

class UpdateInput(BaseModel):
    username: Optional[str] = None
    email:    Optional[EmailStr] = None
    password: Optional[str] = None


# ─── GET MY PROFILE ──────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ─── UPDATE MY PROFILE ───────────────────────────────────────────────

@router.put("/me", response_model=UserOut)
def update_me(data: UpdateInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if data.username:
        existing = db.query(User).filter(User.username == data.username, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken.")
        current_user.username = data.username

    if data.email:
        existing = db.query(User).filter(User.email == data.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use.")
        current_user.email = data.email

    if data.password:
        current_user.hashed_password = hash_password(data.password)

    db.commit()
    db.refresh(current_user)
    return current_user


# ─── DELETE ACCOUNT ──────────────────────────────────────────────────

@router.delete("/me")
def delete_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted."}
