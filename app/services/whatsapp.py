"""WhatsApp alerts via Twilio REST API. Falls back to mock mode when no credentials are set."""
import logging
from typing import List, Tuple

import httpx

from app.core import config

log = logging.getLogger("whatsapp")


def build_alert(name: str, sender: str, score: int, for_guardian: bool = False) -> str:
    who = f"আপনার পরিচিত {name}-এর" if for_guardian else f"{name}, আপনার"
    return (
        f"🚨 FraudGuard Alert\n"
        f"{who} ফোনে {sender} থেকে আসা SMS-টি প্রতারণামূলক (Risk {score}/100)।\n"
        f"❌ PIN/OTP দেবেন না  ❌ লিংকে ক্লিক করবেন না  ❌ টাকা পাঠাবেন না\n\n"
        f"Warning: The SMS from {sender} is a likely SCAM. Never share your PIN/OTP or send money."
    )


def is_live() -> bool:
    return bool(config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN)


def send(to: str, body: str) -> bool:
    """Send one WhatsApp message. Returns True on success. Never raises."""
    if not is_live():
        log.info("[MOCK WhatsApp] to=%s\n%s", to, body)
        return True
    url = f"https://api.twilio.com/2010-04-01/Accounts/{config.TWILIO_ACCOUNT_SID}/Messages.json"
    try:
        resp = httpx.post(
            url,
            data={"From": config.TWILIO_WHATSAPP_FROM, "To": f"whatsapp:{to}", "Body": body},
            auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN),
            timeout=10,
        )
        if resp.status_code >= 300:
            log.error("Twilio error %s: %s", resp.status_code, resp.text[:300])
            return False
        return True
    except httpx.HTTPError as exc:
        log.error("Twilio request failed: %s", exc)
        return False


def send_fraud_alerts(user, sender: str, score: int) -> Tuple[str, List[str]]:
    """Alert the user and their guardian. Returns (status, recipients)."""
    targets = [(user.whatsapp, build_alert(user.name, sender, score))]
    if user.guardian_whatsapp:
        targets.append((user.guardian_whatsapp, build_alert(user.name, sender, score, for_guardian=True)))
    results = [(to, send(to, body)) for to, body in targets]
    delivered = [to for to, ok in results if ok]
    if not delivered:
        status = "failed"
    elif not is_live():
        status = "mocked"
    else:
        status = "sent" if len(delivered) == len(results) else "partial"
    return status, delivered
