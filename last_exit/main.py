"""LAST EXIT — browser narrative game (FastAPI)."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

ROOT = Path(__file__).resolve().parent
STORY_PATH = ROOT / "story.json"

app = FastAPI(title="LAST EXIT")
app.mount(
    "/static",
    StaticFiles(directory=str(ROOT / "static")),
    name="last_exit_static",
)
templates = Jinja2Templates(directory=str(ROOT / "templates"))


def load_story() -> dict:
    with STORY_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@app.get("/")
def index(request: Request):
    story = load_story()
    return templates.TemplateResponse(
        request,
        "index.html",
        {"story": story},
    )
