FRAUD_SMS = "Apnar bKash account block hoye jabe. Ekhoni PIN diye verify korun: bit.ly/bk-verify"
SAFE_SMS = "You have received Tk 500 from 01712345678. Balance Tk 1,200. TrxID 9AB3CD7EF1"


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["whatsapp_mode"] == "mock"


def test_register_and_duplicate(client, user):
    assert user["whatsapp"] == "+8801711223344"
    assert user["guardian_whatsapp"] == "+8801811223344"
    r = client.post("/users", json={"name": "Rahim", "phone": "+8801711223344"})
    assert r.status_code == 409 and r.json()["error"] == "CONFLICT"


def test_register_validation_error_format(client):
    r = client.post("/users", json={"name": "R", "phone": "123"})
    body = r.json()
    assert r.status_code == 422 and body["error"] == "VALIDATION_ERROR"
    assert {d["field"] for d in body["details"]} == {"name", "phone"}


def test_get_unknown_user_404(client):
    r = client.get("/users/999")
    assert r.status_code == 404 and r.json()["error"] == "NOT_FOUND"


def test_analyze_fraud_sends_alert_to_user_and_guardian(client, user):
    r = client.post("/messages/analyze", json={"user_phone": "01711223344", "sender": "01899887766", "text": FRAUD_SMS})
    body = r.json()
    assert r.status_code == 200
    assert body["label"] == "FRAUD" and body["risk_score"] >= 70
    assert body["alert_status"] == "mocked"
    assert set(body["alerted"]) == {"+8801711223344", "+8801811223344"}


def test_analyze_safe_no_alert(client, user):
    body = client.post("/messages/analyze", json={"user_phone": "01711223344", "sender": "bKash", "text": SAFE_SMS}).json()
    assert body["label"] == "SAFE" and body["alert_status"] == "not_needed"


def test_analyze_without_user(client):
    body = client.post("/messages/analyze", json={"sender": "01899887766", "text": FRAUD_SMS}).json()
    assert body["label"] == "FRAUD" and body["alert_status"] == "no_user"


def test_analyze_unknown_user_404(client):
    r = client.post("/messages/analyze", json={"user_phone": "01999999999", "sender": "x1", "text": FRAUD_SMS})
    assert r.status_code == 404


def test_analyze_blank_text_422(client):
    r = client.post("/messages/analyze", json={"sender": "01899887766", "text": "    "})
    assert r.status_code == 422


def test_community_report_raises_score(client):
    sms = {"sender": "01866554433", "text": "Bhai ektu call diyen, dorkar ache"}
    before = client.post("/messages/analyze", json=sms).json()["risk_score"]
    for _ in range(2):
        r = client.post("/reports", json={"number": "01866554433", "reason": "scam call"})
    assert r.status_code == 201 and r.json()["report_count"] == 2
    after = client.post("/messages/analyze", json=sms).json()
    assert after["risk_score"] > before
    assert "reported" in after["reasons"][0]


def test_history_filter_and_stats(client, user):
    client.post("/messages/analyze", json={"user_phone": "01711223344", "sender": "01899887766", "text": FRAUD_SMS})
    client.post("/messages/analyze", json={"user_phone": "01711223344", "sender": "bKash", "text": SAFE_SMS})
    fraud = client.get("/messages?label=FRAUD").json()
    assert len(fraud) == 1 and fraud[0]["user_phone"] == "01711223344"
    assert client.get("/messages?label=WRONG").status_code == 422
    stats = client.get("/stats").json()
    assert stats["total_messages"] == 2 and stats["fraud"] == 1 and stats["alerts_sent"] == 1
    assert stats["top_fraud_senders"][0]["number"] == "01899887766"
