from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut, UserLogin, Token
from app.services.auth_service import create_user, authenticate_user, login_access_token
from app.db.session import get_db
from app.models.user import User


router = APIRouter()

@router.get("/health")
def auth_health():
    return {"auth": "ok"}


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = create_user(db, email=user_in.email, password=user_in.password)
    return user


@router.post("/login", response_model=Token)
def login(form_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, email=form_data.email, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = login_access_token(user)
    return {"access_token": token, "token_type": "bearer"}
