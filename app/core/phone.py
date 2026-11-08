"""Bangladeshi phone number helpers."""
import re

BD_MOBILE = re.compile(r"^(?:\+?88)?(01[3-9]\d{8})$")


def normalize_bd_phone(value: str) -> str:
    """'+8801711223344' / '8801711223344' / '01711-223344' -> '01711223344'. Raises ValueError."""
    cleaned = re.sub(r"[\s\-()]", "", value or "")
    match = BD_MOBILE.match(cleaned)
    if not match:
        raise ValueError("must be a valid Bangladeshi mobile number, e.g. 01711223344")
    return match.group(1)


def is_bd_mobile(value: str) -> bool:
    try:
        normalize_bd_phone(value)
        return True
    except ValueError:
        return False


def to_e164(local: str) -> str:
    """'01711223344' -> '+8801711223344' (format WhatsApp needs)."""
    return "+88" + local
