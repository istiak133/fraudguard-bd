"""Database tables."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db import Base


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(11), unique=True, index=True, nullable=False)
    whatsapp = Column(String(20), nullable=False)
    guardian_name = Column(String(100), nullable=True)
    guardian_whatsapp = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)

    messages = relationship("Message", back_populates="user")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    sender = Column(String(30), nullable=False, index=True)
    text = Column(Text, nullable=False)
    risk_score = Column(Integer, nullable=False)
    label = Column(String(12), nullable=False, index=True)
    ml_probability = Column(Float, nullable=False)
    reasons = Column(Text, nullable=False)  # JSON list
    alert_status = Column(String(20), nullable=False, default="not_needed")
    created_at = Column(DateTime(timezone=True), default=_now, index=True)

    user = relationship("User", back_populates="messages")


class FraudReport(Base):
    """Community blacklist: one row per reported number."""
    __tablename__ = "fraud_reports"

    id = Column(Integer, primary_key=True)
    number = Column(String(30), unique=True, index=True, nullable=False)
    report_count = Column(Integer, nullable=False, default=1)
    last_reason = Column(String(300), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)
