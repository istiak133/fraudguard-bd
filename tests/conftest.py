import os

# Must be set BEFORE the app is imported: in-memory DB, WhatsApp forced to mock mode.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["TWILIO_ACCOUNT_SID"] = ""
os.environ["TWILIO_AUTH_TOKEN"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def user(client):
    r = client.post("/users", json={"name": "Rahim", "phone": "01711223344",
                                    "guardian_name": "Karim", "guardian_phone": "01811223344"})
    assert r.status_code == 201
    return r.json()
