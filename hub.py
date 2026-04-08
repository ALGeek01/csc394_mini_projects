"""
CSC394 hub: one Uvicorn process for the web mini projects.

Run from this directory:
  uvicorn hub:app --reload --host 127.0.0.1 --port 8000

Individual projects can still be run alone (see each subfolder README).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "textbook_summarizer") not in sys.path:
    sys.path.insert(0, str(ROOT / "textbook_summarizer"))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.main import create_summarizer_app
from last_exit.main import app as last_exit_app


def build_hub() -> FastAPI:
    hub = FastAPI(title="CSC394 Mini Projects Hub")
    templates = Jinja2Templates(directory=str(ROOT / "hub_templates"))

    @hub.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "hub.html", {})

    hub.mount("/summarizer", create_summarizer_app("/summarizer"))
    hub.mount("/last-exit", last_exit_app)
    hub.mount(
        "/white-noise",
        StaticFiles(directory=str(ROOT / "white_noise"), html=True),
        name="white_noise",
    )
    hub.mount(
        "/paperplay",
        StaticFiles(directory=str(ROOT / "paperplay_web"), html=True),
        name="paperplay_web",
    )

    return hub


app = build_hub()
