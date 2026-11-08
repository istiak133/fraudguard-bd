from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import FraudReport, Message, User
from app.schemas.dto import StatsOut, TopNumber

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("", response_model=StatsOut, summary="Dashboard numbers")
def get_stats(db: Session = Depends(get_db)):
    counts = dict(db.query(Message.label, func.count(Message.id)).group_by(Message.label).all())
    top = (
        db.query(Message.sender, func.count(Message.id).label("c"))
        .filter(Message.label == "FRAUD").group_by(Message.sender)
        .order_by(func.count(Message.id).desc()).limit(5).all()
    )
    return StatsOut(
        total_messages=sum(counts.values()),
        fraud=counts.get("FRAUD", 0),
        suspicious=counts.get("SUSPICIOUS", 0),
        safe=counts.get("SAFE", 0),
        alerts_sent=db.query(Message).filter(Message.alert_status.in_(["sent", "mocked", "partial"])).count(),
        registered_users=db.query(User).count(),
        reported_numbers=db.query(FraudReport).count(),
        top_fraud_senders=[TopNumber(number=s, count=c) for s, c in top],
    )
