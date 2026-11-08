from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.core.phone import to_e164
from app.db import get_db
from app.models import User
from app.schemas.dto import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED,
             summary="Register a user and their guardian for WhatsApp alerts")
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == payload.phone).first():
        raise ConflictError(f"User with phone {payload.phone} is already registered")
    user = User(
        name=payload.name,
        phone=payload.phone,
        whatsapp=to_e164(payload.phone),
        guardian_name=payload.guardian_name,
        guardian_whatsapp=to_e164(payload.guardian_phone) if payload.guardian_phone else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=List[UserOut], summary="List registered users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id.desc()).all()


@router.get("/{user_id}", response_model=UserOut, summary="Get one user")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found")
    return user
