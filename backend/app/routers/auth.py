from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.schema.user import UserCreate, UserLogin, UserOut
from backend.app.utils.password import hash_password, verify_password

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(User).where(User.email == payload.email)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    u = User(
        email=str(payload.email),
        name=payload.name,
        password_hash=hash_password(payload.password),
        role="member",
    )
    try:
        db.add(u)
        db.commit()
        db.refresh(u)
        return u
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {e}")

@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    u = db.execute(select(User).where(User.email == payload.email)).scalars().first()
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "login ok (JWT cookies come next)"}
