import json
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.core.phone import normalize_bd_phone
from app.db import get_db
from app.models import Message, User
from app.schemas.dto import AnalyzeRequest, AnalyzeResponse, MessageOut
from app.services import detector, whatsapp

router = APIRouter(prefix="/messages", tags=["Messages (core)"])


@router.post("/analyze", response_model=AnalyzeResponse,
             summary="⭐ Analyze an incoming SMS and alert on WhatsApp if it's fraud")
def analyze_message(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    1. Validate the SMS  2. Score it with **rules + local ML model + community blacklist**
    3. Label SAFE / SUSPICIOUS / FRAUD  4. If FRAUD → WhatsApp alert to user + guardian  5. Save to history
    """
    user = None
    if payload.user_phone:
        user = db.query(User).filter(User.phone == payload.user_phone).first()
        if not user:
            raise NotFoundError(f"No registered user with phone {payload.user_phone}")

    verdict = detector.analyze(db, payload.text, payload.sender)

    alert_status, alerted = "not_needed", []
    if verdict.label == "FRAUD":
        if user:
            alert_status, alerted = whatsapp.send_fraud_alerts(user, payload.sender, verdict.risk_score)
        else:
            alert_status = "no_user"

    msg = Message(
        user_id=user.id if user else None,
        sender=payload.sender,
        text=payload.text,
        risk_score=verdict.risk_score,
        label=verdict.label,
        ml_probability=verdict.ml_probability,
        reasons=json.dumps(verdict.reasons, ensure_ascii=False),
        alert_status=alert_status,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return AnalyzeResponse(
        message_id=msg.id, risk_score=verdict.risk_score, label=verdict.label,
        ml_probability=verdict.ml_probability, rule_score=verdict.rule_score,
        reasons=verdict.reasons, alert_status=alert_status, alerted=alerted,
    )


@router.get("", response_model=List[MessageOut], summary="History of analyzed messages")
def list_messages(
    label: Optional[str] = Query(None, pattern="^(SAFE|SUSPICIOUS|FRAUD)$"),
    user_phone: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(Message)
    if label:
        q = q.filter(Message.label == label)
    if user_phone:
        try:
            phone = normalize_bd_phone(user_phone)
        except ValueError:
            from app.core.errors import AppError
            raise AppError(422, "VALIDATION_ERROR", "user_phone must be a valid BD mobile number")
        q = q.join(User).filter(User.phone == phone)
    rows = q.order_by(Message.id.desc()).offset(offset).limit(limit).all()
    return [
        MessageOut(
            id=m.id, sender=m.sender, text=m.text, risk_score=m.risk_score, label=m.label,
            reasons=json.loads(m.reasons), alert_status=m.alert_status,
            user_phone=m.user.phone if m.user else None, created_at=m.created_at,
        )
        for m in rows
    ]
