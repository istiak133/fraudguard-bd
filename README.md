<div align="center">

# 🛡️ FraudGuard BD

**Real-time scam SMS detection for bKash / Nagad users, with WhatsApp alerts that arrive *before* the money is gone.**

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-F7931E?logo=scikitlearn&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-SQLAlchemy%202-003B57?logo=sqlite&logoColor=white)
![Tests](https://img.shields.io/badge/tests-26%20passing-2EA44F)

*Credosis Internship Program · Phase 02 · Backend Engineer track*

</div>

---

## Table of Contents
1. [The Problem](#-the-problem)
2. [The Solution](#-the-solution)
3. [Features](#-features)
4. [Architecture](#-architecture)
5. [How Detection Works](#-how-detection-works)
6. [API Reference](#-api-reference)
7. [Getting Started](#-getting-started)
8. [Testing](#-testing)
9. [Project Structure](#-project-structure)
10. [Design Decisions](#-design-decisions)
11. [Challenges](#-challenges)
12. [Limitations & Roadmap](#-limitations--roadmap)

---

## 🎯 The Problem

Millions of people in Bangladesh use mobile financial services (bKash, Nagad, Rocket). Scammers reach them every day with SMS like these:

- *"Your bKash account will be blocked in 24 hours. Verify with your PIN: bit.ly/…"*
- *"Bhai, I sent 5,000 tk to your number by mistake, please send it back."*
- *"Congratulations! You won 25,000 tk in the bKash lottery. Tell us your PIN to claim."*

The providers' warnings are generic ("never share your PIN"). By the time a victim realises what happened, the money is gone. Elderly and less tech-savvy users are hit hardest, and **nobody close to them knows until it's too late**.

## 💡 The Solution

FraudGuard BD is a backend service that **analyzes every incoming SMS the moment it arrives** and:

1. Scores its fraud risk from **0 to 100** with a **local, lightweight ML model**, an **explainable rule engine** and a **community blacklist**.
2. Explains **why**, with human-readable reasons.
3. If the SMS is fraud, sends a **bilingual (Bangla + English) WhatsApp warning to the user *and* to a family "guardian"**, so someone can step in *before* money is sent.

```
📱 SMS arrives ──► POST /messages/analyze ──► risk 97 · FRAUD ──► 💬 WhatsApp → user + guardian
```

## ✨ Features

| | Feature | Why it matters |
|---|---|---|
| ⭐ **Core** | **SMS analysis → risk score + reasons → WhatsApp alert** | The main idea: a warning delivered at the moment of risk |
| 👨‍👩‍👧 | **Guardian alerts** | A family member is told too, which protects the most vulnerable users |
| 🚩 | **Community reports / blacklist** | Each report makes future SMS from that number riskier |
| 📊 | **History & stats** | Filterable message history plus a dashboard of fraud caught and top scam senders |
| 📘 | **Swagger + Scalar docs, demo UI** | `/docs`, `/scalar` and a bKash-themed simulator at `/` |

## 🏗️ Architecture

```
                ┌──────────────────────────── FastAPI app ────────────────────────────┐
 Client         │  api/routes            schemas            services             models  │
 (Swagger,  ──► │  messages  ──validate──►  dto.py  ──►  detector ─┬─ rules         ──► SQLite
  UI, future    │  users                                          ├─ classifier (ML)     (SQLAlchemy)
  Android app)  │  reports                                        └─ blacklist           │
                │  stats                               whatsapp (Twilio / mock) ──► 💬     │
                │  core: config · errors (uniform JSON) · phone (BD number validation)   │
                └────────────────────────────────────────────────────────────────────────┘
```

**Layering rule:** routes are thin (HTTP in, HTTP out), schemas validate, services hold the business logic, and models hold persistence. Every layer can be tested on its own.

## 🧠 How Detection Works

```
                     ┌─► Rule engine ──► rule_score (0–100) + reasons
SMS text + sender ───┼─► ML model    ──► fraud probability (0–1)
                     └─► Blacklist   ──► bonus (+25 … +40) if the sender was reported

risk = min(100, max(0.6 × ML×100 + 0.4 × rules, rules) + blacklist_bonus)

  ≥ 70  🚨 FRAUD       → WhatsApp alert to user + guardian
 40–69  ⚠️ SUSPICIOUS  → flagged, no alert
  < 40  ✅ SAFE
```

### Rule engine ([`app/services/rules.py`](app/services/rules.py))
| Rule | Example trigger | Points |
|---|---|---|
| Credential request | "PIN din", "OTP bolun", "পিন নম্বর দিন" (ignored when the SMS says *"never share"*) | +35 |
| Shortened / suspicious link | `bit.ly`, `tinyurl`, `.xyz`, `t.me/` | +25 / +15 |
| Urgency or threat | "block hoye jabe", "suspend", "এখনই" | +15 |
| Prize bait | "lottery", "jitechen", "পুরস্কার" | +20 |
| "Sent by mistake, send it back" | "bhul kore pathiye felsi, ferot pathan" | +25 |
| Impersonation | "bKash head office theke bolchi" | +15 |
| Advance-fee job/loan | "registration fee", "ghore bose income" | +20 |
| Financial SMS from a personal number | Real alerts come from the `bKash` / `NAGAD` sender ID, never from `017…` | +20 |

### ML model ([`ml/`](ml/))
- **Features:** TF-IDF on word 1–2-grams **plus** character 2–5-grams
- **Classifier:** Logistic Regression
- **Size / speed:** ~200 KB, runs in a few milliseconds on CPU, fully offline
- **Data:** a synthetic dataset of 1,505 labelled SMS (959 fraud, 546 legit) in Bangla, Banglish and English, generated from real-world scam patterns ([`ml/generate_dataset.py`](ml/generate_dataset.py))

## 📡 API Reference

Interactive docs: **Swagger UI → `/docs`** · **Scalar → `/scalar`** · OpenAPI JSON → `/openapi.json`

| Method | Endpoint | Description | Success |
|---|---|---|---|
| `POST` | `/messages/analyze` | ⭐ Analyze an SMS, score it, alert if fraud | `200` |
| `GET` | `/messages` | History (`label`, `user_phone`, `limit`, `offset`) | `200` |
| `POST` | `/users` | Register a user and an optional guardian | `201` |
| `GET` | `/users` · `/users/{id}` | List users / get one user | `200` |
| `POST` | `/reports` | Report a number as fraud | `201` |
| `GET` | `/reports` | Community blacklist | `200` |
| `GET` | `/stats` | Dashboard numbers | `200` |
| `GET` | `/health` | Liveness check and WhatsApp mode | `200` |

### Example: the core endpoint
```bash
curl -X POST http://127.0.0.1:8765/messages/analyze \
  -H "Content-Type: application/json" \
  -d '{
        "user_phone": "01711223344",
        "sender": "01899887766",
        "text": "Apnar bKash account block hoye jabe. Ekhoni PIN diye verify korun: bit.ly/bk-verify"
      }'
```
```json
{
  "message_id": 1,
  "risk_score": 97,
  "label": "FRAUD",
  "ml_probability": 0.9858,
  "rule_score": 95,
  "reasons": [
    "Asks for PIN/OTP/password — bKash & Nagad never ask for these",
    "Contains a shortened link that hides the real website",
    "Uses threats or urgency (block/suspend/act now)",
    "Financial SMS from a personal number — official alerts come from 'bKash'/'NAGAD' sender IDs",
    "ML model: 99% similar to known scam messages"
  ],
  "alert_status": "sent",
  "alerted": ["+8801711223344", "+8801811223344"]
}
```

### Error format
Every error, including validation errors, 404s and unexpected crashes, uses the same shape:
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid request data",
  "details": [{ "field": "phone", "issue": "must be a valid Bangladeshi mobile number, e.g. 01711223344" }]
}
```
| Code | HTTP | When |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Bad phone number, blank text, invalid filter… |
| `NOT_FOUND` | 404 | Unknown user or route |
| `CONFLICT` | 409 | Phone number already registered |
| `INTERNAL_ERROR` | 500 | Unexpected failure (no stack trace leaked) |

## 🚀 Getting Started

**Requirements:** Python 3.9+

```bash
git clone https://github.com/istiak133/fraudguard-bd.git
cd fraudguard-bd
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8765
```

| URL | What |
|---|---|
| http://127.0.0.1:8765/ | Demo UI (phone simulator) |
| http://127.0.0.1:8765/docs | Swagger UI |
| http://127.0.0.1:8765/scalar | Scalar API reference |

### Enable real WhatsApp alerts (optional)
With no credentials, alerts run in **mock mode**: they are printed in the server log and the API returns `alert_status: "mocked"`.
1. Create a free [Twilio](https://www.twilio.com) account → *Messaging → Try WhatsApp* → join the sandbox from your phone.
2. `cp .env.example .env` and set `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`.
3. Restart the server. `/health` now shows `"whatsapp_mode": "live"`.

### Retrain the model (optional)
```bash
python -m ml.generate_dataset   # writes data/sms_dataset.csv
python -m ml.train              # prints a classification report and writes ml/model.joblib
```

### Docker
```bash
docker build -t fraudguard-bd .
docker run -p 8765:8000 --env-file .env fraudguard-bd
```

### Configuration
| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///data/app.db` | Any SQLAlchemy URL (e.g. Postgres) |
| `FRAUD_THRESHOLD` | `70` | Score at or above this is FRAUD |
| `SUSPICIOUS_THRESHOLD` | `40` | Score at or above this is SUSPICIOUS |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` | *(empty)* | Empty means mock mode |
| `TWILIO_WHATSAPP_FROM` | `whatsapp:+14155238886` | Twilio sandbox sender |

## 🧪 Testing

```bash
pytest -q
# 26 passed in ~2s
```

| Suite | Covers |
|---|---|
| [`tests/test_units.py`](tests/test_units.py) | BD phone normalization, every major rule, the "never share" exception, score capping, ML separation, labelling, alert text |
| [`tests/test_api.py`](tests/test_api.py) | End-to-end: registration, 409 duplicates, 422 error format, 404s, fraud → alert to user + guardian, safe → no alert, blacklist raising the score, history filters, stats |

Tests run against an **in-memory SQLite DB**, and WhatsApp is **forced into mock mode**, so they never touch real data or send real messages.

## 🗂️ Project Structure

```
.
├── app/
│   ├── main.py                 # App factory: routers, error handlers, lifespan, UI, Scalar
│   ├── db.py                   # Engine, session, get_db dependency
│   ├── core/
│   │   ├── config.py           # All settings (env-driven)
│   │   ├── errors.py           # AppError hierarchy + uniform JSON error handlers
│   │   └── phone.py            # Bangladeshi number validation / normalization
│   ├── api/routes/             # Thin HTTP layer
│   │   ├── messages.py         # ⭐ /messages/analyze, /messages
│   │   ├── users.py · reports.py · stats.py · health.py
│   ├── schemas/dto.py          # Pydantic request/response models + validators
│   ├── services/               # Business logic
│   │   ├── detector.py         # Combines ML + rules + blacklist → verdict
│   │   ├── rules.py            # Explainable red-flag rules
│   │   ├── classifier.py       # Loads the model once, predicts probability
│   │   └── whatsapp.py         # Twilio sender with mock fallback
│   ├── models/entities.py      # SQLAlchemy tables: users, messages, fraud_reports
│   └── static/index.html       # Demo UI
├── ml/
│   ├── generate_dataset.py     # Synthetic Bangla/Banglish/English SMS
│   ├── train.py                # TF-IDF + Logistic Regression training
│   └── model.joblib            # Trained model (~200 KB)
├── data/sms_dataset.csv
├── tests/
├── Dockerfile · requirements.txt · .env.example
```

## 🧭 Design Decisions

Each decision below lists what we chose, the alternatives we considered, and why.

### D1. Backend-first: simulate SMS input instead of building a mobile app
- **Context:** Reading SMS needs a native Android app. iOS doesn't allow it at all. The deadline was a few hours away.
- **Decision:** Build the whole detection and alert pipeline as an API. SMS are "delivered" through `POST /messages/analyze`, from Swagger or the demo UI.
- **Why:** This is the part that carries the value. A future Android companion app only has to forward each SMS to the same endpoint, so **no backend change is needed**.

### D2. Classical ML (TF-IDF + Logistic Regression) instead of an LLM or deep model
- **Alternatives:** an LLM API, a fine-tuned BERT/BanglaBERT, Naive Bayes.
- **Decision:** TF-IDF + Logistic Regression.
- **Why:** It runs **locally and offline** (an SMS never leaves the server, which helps privacy), predicts in **milliseconds**, has **zero per-request cost**, is ~200 KB (small enough to run on a phone later), and gives calibrated probabilities. An LLM would add latency, cost and a dependency on an external service, all for a short-text classification task.

### D3. Character n-grams on top of word n-grams
- **Context:** Banglish has no standard spelling (*bhul / vul*, *ekhoni / akhoni*), and Bangla script needs special tokenization.
- **Decision:** Add `char_wb` 2–5-grams to the TF-IDF features.
- **Why:** Character fragments match across spelling variants and work for Bangla script **without a language-specific tokenizer**.

### D4. Hybrid scoring: ML + rules + community blacklist
- **Decision:** `risk = max(0.6·ML + 0.4·Rules, Rules) + blacklist bonus`
- **Why:**
  - **Explainability:** rules give human-readable reasons, which users and reviewers can trust.
  - **Robustness:** rules catch strong signals (like a PIN request) even when the model is unsure. The `max(…, Rules)` term means strong rule evidence is **never diluted** by a low ML score.
  - **Safety against false alarms:** ML alone can reach at most 60, so it can flag a message as SUSPICIOUS but **cannot trigger a WhatsApp alert without at least one red flag**.
  - **Network effect:** community reports catch scammers whose wording is new.

### D5. A synthetic dataset
- **Context:** There is no public labelled dataset of Bangladeshi MFS scam SMS.
- **Decision:** Generate 1,505 labelled SMS from templates based on real scam patterns, in three languages/scripts. Include hard negatives: real cash-in notices, *genuine OTP messages that say "never share"*, and casual chat.
- **Why:** It unblocks the demo and is reproducible (fixed seed). We noticed early on that an innocent "parcel delivered?" message scored 73% fraud, so we **added more varied legitimate chat** and retrained (73% → 10%).
- **Trade-off:** 100% accuracy on the held-out split reflects template data, **not real-world performance** (see Limitations).

### D6. The sender ID is a first-class signal
- **Insight:** Real bKash/Nagad notifications come from alphanumeric sender IDs (`bKash`, `NAGAD`). A *"Cash In Tk 5,000 successful"* SMS from `01899…` is a classic fake used before the "please send it back" call.
- **Decision:** The `PERSONAL_SENDER` rule fires when a financial SMS comes from a personal mobile number.

### D7. Guardian alerts
- **Decision:** Each user can register a guardian, who gets their own WhatsApp warning.
- **Why:** The victim may not read or believe a warning. A son or daughter getting *"Your father just received a scam SMS"* can call them in time. Existing provider warnings don't do this.

### D8. WhatsApp through Twilio's REST API, with mock mode
- **Alternatives:** Meta WhatsApp Cloud API (needs business verification), SMS alerts.
- **Decision:** Twilio's WhatsApp sandbox, called with a plain `httpx` POST (no SDK). If no credentials are set, alerts run in **mock mode** and are logged instead of sent.
- **Why:** The sandbox is ready in minutes. Mock mode means the demo, tests and CI **never break** for lack of keys. Alert failures are caught and reported (`alert_status: failed`), and **analysis still succeeds**.

### D9. Thin routes, layered services
- **Decision:** `routes → schemas → services → models`.
- **Why:** The business logic (`detector`, `rules`) has no HTTP or DB-framework code in it, so it is easy to unit-test and could be reused (for example in a background worker).

### D10. One error format everywhere
- **Decision:** Custom handlers turn `AppError`, Pydantic validation errors, HTTP errors and unexpected exceptions into `{error, message, details}`.
- **Why:** Clients only handle one shape. Validation errors name the exact field. 500s never leak stack traces.

### D11. Normalize phone numbers at the edge
- **Decision:** Every phone input (`01711…`, `+8801711…`, `01711-…`) is validated and normalized to `01XXXXXXXXX` in the schema layer, and converted to E.164 (`+8801…`) only for WhatsApp.
- **Why:** This prevents duplicate users and missed blacklist matches caused by formatting differences.

### D12. Analysis works without a registered user
- **Decision:** `user_phone` is optional. Without it, the SMS is still analyzed and saved, with `alert_status: "no_user"`. An unknown `user_phone` returns `404`.
- **Why:** The endpoint is also useful as a plain "is this SMS a scam?" checker, and a typo in the phone number still fails loudly.

### D13. SQLite + SQLAlchemy, with the DB set by environment variable
- **Decision:** SQLite by default, `DATABASE_URL` for anything else.
- **Why:** No setup needed for reviewers. Switching to Postgres is a config change. Tests use an in-memory DB.

### D14. The model loads once at startup and can retrain itself
- **Decision:** It loads in FastAPI's `lifespan` hook. If `model.joblib` is missing, it trains automatically from the dataset.
- **Why:** No per-request loading cost, and a fresh clone or deploy can't fail because of a missing artifact.

### D15. The demo UI is served by the same app
- **Decision:** A single static HTML page (vanilla JS, bKash-pink theme) at `/`. No separate frontend build.
- **Why:** The track is backend-focused. One process and one URL make the demo easy to run and deploy.

## 🧗 Challenges

| Challenge | How we handled it |
|---|---|
| Apps can't read SMS on iOS, and Android needs a native app | Exposed ingestion as an API (D1). The companion app is on the roadmap |
| No real labelled dataset | Synthetic generator with hard negatives (D5) |
| Banglish spelling chaos plus Bangla script | Character n-grams (D3) |
| False positives on ordinary chat | Found during manual testing, fixed with more data, and guarded so ML alone can't trigger alerts (D4) |
| Genuine OTP SMS contain "OTP" and "code" too | The rule engine skips credential matches when the SMS contains a safety note ("never share") |
| WhatsApp API access | Twilio sandbox with mock fallback (D8) |

## 🔭 Limitations & Roadmap

**Known limitations**
- The model is trained on **synthetic** data, so real-world accuracy will be lower than the reported test score. Collecting real, consented, labelled SMS is the most important next step.
- Rules are keyword/regex based, so a determined scammer can rephrase around them (the ML and the blacklist partly compensate).
- There is no authentication or rate limiting yet, and the community report endpoint could be abused.

**Roadmap**
- [ ] Android companion app (`READ_SMS` permission → `POST /messages/analyze`)
- [ ] API-key / JWT auth, per-user rate limiting, abuse protection for reports
- [ ] Real-data collection loop: user feedback ("this was / wasn't a scam") → retraining
- [ ] URL reputation lookup (domain age, known phishing lists)
- [ ] Meta WhatsApp Cloud API with a verified business sender
- [ ] PostgreSQL + Alembic migrations, background task queue for alerts

---

<div align="center">
Built by <b>Istiak Ahmed</b> for the Credosis Internship Program · Phase 02
</div>
