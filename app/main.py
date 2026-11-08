import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import health, messages, reports, stats, users
from app.core.config import APP_NAME, APP_VERSION, BASE_DIR
from app.core.errors import register_error_handlers
from app.db import Base, engine
from app.services.classifier import load_model

logging.basicConfig(level=logging.INFO)
STATIC_DIR = BASE_DIR / "app" / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    (BASE_DIR / "data").mkdir(exist_ok=True)
    Base.metadata.create_all(bind=engine)  # create tables
    load_model()                            # load ML model once
    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=(
        "Detects bKash/Nagad scam SMS using a **local lightweight ML model + rule engine** and warns the "
        "user *and their guardian* on **WhatsApp** before they lose money.\n\n"
        "Try the core endpoint: `POST /messages/analyze`. Docs: Swagger `/docs` · Scalar `/scalar`."
    ),
    lifespan=lifespan,
)

register_error_handlers(app)
for module in (health, messages, users, reports, stats):
    app.include_router(module.router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/scalar", include_in_schema=False)
def scalar_docs():
    return HTMLResponse(f"""<!doctype html><html><head><title>{APP_NAME} · Scalar</title>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/></head>
<body><script id="api-reference" data-url="/openapi.json"></script>
<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.25.0"></script></body></html>""")
