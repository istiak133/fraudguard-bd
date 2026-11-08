"""Request / response shapes + validation (Pydantic)."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.phone import normalize_bd_phone, to_e164


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Rahim Uddin"])
    phone: str = Field(..., description="BD mobile number", examples=["01711223344"])
    guardian_name: Optional[str] = Field(None, max_length=100, examples=["Karim (son)"])
    guardian_phone: Optional[str] = Field(None, description="Guardian's WhatsApp number", examples=["01811223344"])

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("name must have at least 2 characters")
        return v

    @field_validator("phone", "guardian_phone")
    @classmethod
    def valid_phone(cls, v: Optional[str]) -> Optional[str]:
        return None if v in (None, "") else normalize_bd_phone(v)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    phone: str
    whatsapp: str
    guardian_name: Optional[str]
    guardian_whatsapp: Optional[str]
    created_at: datetime


class AnalyzeRequest(BaseModel):
    sender: str = Field(..., min_length=2, max_length=30, description="Number or sender ID the SMS came from",
                        examples=["01899887766"])
    text: str = Field(..., min_length=3, max_length=1000,
                      examples=["Apnar bKash account block hoye jabe. Ekhoni PIN diye verify korun: bit.ly/bk-verify"])
    user_phone: Optional[str] = Field(None, description="Registered user who received the SMS (enables WhatsApp alert)",
                                      examples=["01711223344"])

    @field_validator("text", "sender")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v.strip()

    @field_validator("sender")
    @classmethod
    def normalize_sender(cls, v: str) -> str:
        try:
            return normalize_bd_phone(v)
        except ValueError:
            return v  # alphanumeric sender IDs like "bKash" are allowed

    @field_validator("user_phone")
    @classmethod
    def valid_user_phone(cls, v: Optional[str]) -> Optional[str]:
        return None if v in (None, "") else normalize_bd_phone(v)


class AnalyzeResponse(BaseModel):
    message_id: int
    risk_score: int = Field(..., ge=0, le=100)
    label: str = Field(..., description="SAFE | SUSPICIOUS | FRAUD")
    ml_probability: float
    rule_score: int
    reasons: List[str]
    alert_status: str = Field(..., description="not_needed | no_user | sent | mocked | partial | failed")
    alerted: List[str]


class MessageOut(BaseModel):
    id: int
    sender: str
    text: str
    risk_score: int
    label: str
    reasons: List[str]
    alert_status: str
    user_phone: Optional[str]
    created_at: datetime


class ReportCreate(BaseModel):
    number: str = Field(..., examples=["01899887766"])
    reason: Optional[str] = Field(None, max_length=300, examples=["Asked for my bKash PIN"])

    @field_validator("number")
    @classmethod
    def valid_number(cls, v: str) -> str:
        return normalize_bd_phone(v)


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    number: str
    report_count: int
    last_reason: Optional[str]
    updated_at: datetime


class TopNumber(BaseModel):
    number: str
    count: int


class StatsOut(BaseModel):
    total_messages: int
    fraud: int
    suspicious: int
    safe: int
    alerts_sent: int
    registered_users: int
    reported_numbers: int
    top_fraud_senders: List[TopNumber]
