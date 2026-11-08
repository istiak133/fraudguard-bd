"""Core feature: combine ML + rules + community blacklist into one risk score and decision."""
from dataclasses import dataclass
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.core import config
from app.models import FraudReport
from app.services import classifier, rules


@dataclass
class Verdict:
    risk_score: int
    label: str
    ml_probability: float
    rule_score: int
    reasons: List[str]


def blacklist_bonus(db: Session, sender: str) -> Tuple[int, int]:
    report = db.query(FraudReport).filter(FraudReport.number == sender).first()
    if not report:
        return 0, 0
    return min(40, 20 + 5 * report.report_count), report.report_count


def label_for(score: int) -> str:
    if score >= config.FRAUD_THRESHOLD:
        return "FRAUD"
    if score >= config.SUSPICIOUS_THRESHOLD:
        return "SUSPICIOUS"
    return "SAFE"


def analyze(db: Session, text: str, sender: str) -> Verdict:
    hits = rules.evaluate(text, sender)
    rule_score = rules.score(hits)
    prob = classifier.fraud_probability(text)
    bonus, reports = blacklist_bonus(db, sender)

    combined = config.ML_WEIGHT * prob * 100 + config.RULE_WEIGHT * rule_score
    # Strong rule evidence alone should never be diluted by the model.
    final = int(round(min(100, max(combined, rule_score) + bonus)))

    reasons = [h.reason for h in hits]
    reasons.append(f"ML model: {prob:.0%} similar to known scam messages")
    if reports:
        reasons.insert(0, f"Sender reported as fraud by the community {reports} time(s)")
    return Verdict(final, label_for(final), round(prob, 4), rule_score, reasons)
