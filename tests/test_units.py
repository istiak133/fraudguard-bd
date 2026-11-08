import pytest

from app.core.phone import normalize_bd_phone, to_e164
from app.services import rules
from app.services.classifier import fraud_probability
from app.services.detector import label_for
from app.services.whatsapp import build_alert


@pytest.mark.parametrize("raw", ["01711223344", "+8801711223344", "8801711223344", "01711-223344"])
def test_phone_normalization(raw):
    assert normalize_bd_phone(raw) == "01711223344"
    assert to_e164(normalize_bd_phone(raw)) == "+8801711223344"


@pytest.mark.parametrize("raw", ["12345", "01211223344", "0171122334", "abc"])
def test_invalid_phone(raw):
    with pytest.raises(ValueError):
        normalize_bd_phone(raw)


def codes(text, sender="01899887766"):
    return {h.code for h in rules.evaluate(text, sender)}


def test_rules_detect_pin_phishing():
    c = codes("Apnar bKash account block hobe. PIN diye verify korun: bit.ly/x")
    assert {"CREDENTIAL_REQUEST", "SHORT_LINK", "URGENCY", "PERSONAL_SENDER"} <= c


def test_rules_ignore_legit_otp_safety_note():
    assert "CREDENTIAL_REQUEST" not in codes("Your OTP is 1234. Never share this code with anyone.", "bKash")


def test_rules_money_back_scam():
    assert "MONEY_BACK" in codes("Vai bhul kore 5000 tk pathiye felsi, ferot pathan please")


def test_rule_score_capped():
    hits = rules.evaluate("bKash office: account block! PIN din bit.ly/x lottery jitechen bhul kore pathiye ferot", "01899887766")
    assert rules.score(hits) == 100


def test_ml_separates_fraud_and_legit():
    assert fraud_probability("Apnar bKash account block hobe, ekhoni PIN din") > 0.7
    assert fraud_probability("Bhai kal meeting ta 11 tay, office e chole ashben.") < 0.3


def test_labels():
    assert label_for(85) == "FRAUD"
    assert label_for(50) == "SUSPICIOUS"
    assert label_for(10) == "SAFE"


def test_alert_text_bilingual():
    msg = build_alert("Rahim", "01899887766", 92)
    assert "01899887766" in msg and "92/100" in msg and "PIN" in msg
