from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import FraudReport
from app.schemas.dto import ReportCreate, ReportOut

router = APIRouter(prefix="/reports", tags=["Community Reports"])


@router.post("", response_model=ReportOut, status_code=status.HTTP_201_CREATED,
             summary="Report a number as fraud (raises risk for future SMS from it)")
def report_number(payload: ReportCreate, db: Session = Depends(get_db)):
    report = db.query(FraudReport).filter(FraudReport.number == payload.number).first()
    if report:
        report.report_count += 1
        report.last_reason = payload.reason or report.last_reason
    else:
        report = FraudReport(number=payload.number, last_reason=payload.reason)
        db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("", response_model=List[ReportOut], summary="Community blacklist, most reported first")
def list_reports(db: Session = Depends(get_db)):
    return db.query(FraudReport).order_by(FraudReport.report_count.desc()).limit(100).all()
