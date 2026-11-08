"""Central settings. Values come from environment variables (or a .env file)."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

APP_NAME = "FraudGuard BD API"
APP_VERSION = "1.0.0"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'app.db'}")
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(BASE_DIR / "ml" / "model.joblib")))
DATASET_PATH = BASE_DIR / "data" / "sms_dataset.csv"

# Risk thresholds (0-100)
FRAUD_THRESHOLD = int(os.getenv("FRAUD_THRESHOLD", "70"))
SUSPICIOUS_THRESHOLD = int(os.getenv("SUSPICIOUS_THRESHOLD", "40"))

# How much each signal counts in the final score
ML_WEIGHT = 0.6
RULE_WEIGHT = 0.4

# Twilio WhatsApp. If SID/token are empty, alerts run in "mock" mode (logged, not sent).
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
