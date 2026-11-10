from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db, User
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


# ─── SCHEMAS (what data comes in / goes out) ─────────────────────────

class RegisterInput(BaseModel):
    username: str
    email:    EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type:   str = "bearer"


# ─── REGISTER ────────────────────────────────────────────────────────

@router.post("/register", status_code=201)
def register(data: RegisterInput, db: Session = Depends(get_db)):
    # Check if email already exists
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Check if username already exists
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken.")

    user = User(
        username        = data.username,
        email           = data.email,
        hashed_password = hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": f"Account created! Welcome, {user.username}."}


# ─── LOGIN ───────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm uses 'username' field — we allow login by email OR username
    user = (
        db.query(User).filter(User.email == form.username).first()
        or db.query(User).filter(User.username == form.username).first()
    )

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email/username or password.")

    token = create_access_token({"user_id": user.id})
    return {"access_token": token}
