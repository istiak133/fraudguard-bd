"""Rule engine: explainable red flags that scammers use. Each rule adds points + a reason."""
import re
from dataclasses import dataclass
from typing import List

from app.core.phone import is_bd_mobile

I = re.IGNORECASE

CREDENTIAL = re.compile(r"\b(pin|otp|password|passcode|verification code|code)\b|পিন|ওটিপি|পাসওয়ার্ড|কোড", I)
ASKS = re.compile(r"\b(din|dite|diye|share|send|bolun|bolen|pathan|provide|enter|confirm|login|verify)\b|দিন|বলুন|পাঠান|ভেরিফাই", I)
SAFETY_NOTE = re.compile(r"never share|do not share|don't share|kauke (deben|diben) na|কাউকে দিবেন না|কাউকে বলবেন না|never asks", I)
LINK = re.compile(r"https?://|www\.|\b[\w-]+\.(xyz|top|click|info|link|online|site|tk)\b|t\.me/", I)
SHORTENER = re.compile(r"\b(bit\.ly|tinyurl\.com|cutt\.ly|rb\.gy|is\.gd|t\.co)\b", I)
URGENCY = re.compile(r"\b(block|blocked|suspend|suspended|locked|expire|bondho|urgent|immediately|ekhoni|last chance|24 ghonta|24 hours?)\b|বন্ধ|ব্লক|এখনই|শেষ সুযোগ", I)
PRIZE = re.compile(r"\b(lottery|won|winner|prize|reward|jitechen|cashback peyechen|bonus)\b|লটারি|জিতেছেন|পুরস্কার|বোনাস", I)
MONEY_BACK = re.compile(r"\b(bhul|vul|mistake|wrong)\b.*\b(pathiye|send|gese|gechhe|chole|return|ferot)\b|ভুল.*(ফেরত|চলে)|\bferot pathan\b|\breturn the money\b", I)
IMPERSONATION = re.compile(r"(bkash|nagad|rocket|বিকাশ|নগদ).{0,20}(head office|office|officer|customer care|agent|কাস্টমার কেয়ার|অফিস)", I)
FEE_SCAM = re.compile(r"\b(registration|processing) fee\b|ghore bose", I)
FINANCIAL = re.compile(r"bkash|nagad|rocket|cash in|trxid|balance tk|বিকাশ|নগদ", I)


@dataclass
class RuleHit:
    code: str
    points: int
    reason: str


def evaluate(text: str, sender: str) -> List[RuleHit]:
    hits: List[RuleHit] = []

    def add(code, points, reason):
        hits.append(RuleHit(code, points, reason))

    if CREDENTIAL.search(text) and ASKS.search(text) and not SAFETY_NOTE.search(text):
        add("CREDENTIAL_REQUEST", 35, "Asks for PIN/OTP/password — bKash & Nagad never ask for these")
    if SHORTENER.search(text):
        add("SHORT_LINK", 25, "Contains a shortened link that hides the real website")
    elif LINK.search(text):
        add("SUSPICIOUS_LINK", 15, "Contains a link to a non-official website")
    if URGENCY.search(text):
        add("URGENCY", 15, "Uses threats or urgency (block/suspend/act now)")
    if PRIZE.search(text):
        add("PRIZE_BAIT", 20, "Promises a prize, lottery or bonus")
    if MONEY_BACK.search(text):
        add("MONEY_BACK", 25, "Claims money was sent by mistake and asks to return it")
    if IMPERSONATION.search(text):
        add("IMPERSONATION", 15, "Pretends to be a bKash/Nagad office or agent")
    if FEE_SCAM.search(text):
        add("ADVANCE_FEE", 20, "Asks for an upfront fee for a job/loan/income offer")
    if is_bd_mobile(sender) and FINANCIAL.search(text):
        add("PERSONAL_SENDER", 20, "Financial SMS from a personal number — official alerts come from 'bKash'/'NAGAD' sender IDs")
    return hits


def score(hits: List[RuleHit]) -> int:
    return min(100, sum(h.points for h in hits))
