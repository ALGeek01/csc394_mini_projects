from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.summarizer import SummarizationError, summarize_textbook_content

BASE_DIR = Path(__file__).resolve().parent


def create_summarizer_app(mount_prefix: str = "") -> FastAPI:
    """Build the summarizer app. When mounted under a hub, pass e.g. ``/summarizer``."""
    mount_prefix = (mount_prefix or "").rstrip("/")

    app = FastAPI(title="Student Textbook Summarizer")
    app.mount(
        "/static",
        StaticFiles(directory=str(BASE_DIR / "static")),
        name="summarizer_static",
    )
    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"mount_prefix": mount_prefix},
        )

    @app.post("/api/summarize")
    async def summarize(
        text_input: Optional[str] = Form(default=None),
        max_points: int = Form(default=3),
        chapter_title: Optional[str] = Form(default=None),
        page_range: Optional[str] = Form(default=None),
        summary_style: str = Form(default="quick-review"),
        output_language: str = Form(default="English"),
        pdf_file: Optional[UploadFile] = File(default=None),
    ) -> JSONResponse:
        try:
            allowed_styles = {"quick-review", "exam-ready", "simple"}
            if summary_style not in allowed_styles:
                raise SummarizationError("Invalid summary style selected.")

            pdf_bytes = None
            has_uploaded_file = pdf_file is not None and bool((pdf_file.filename or "").strip())
            if has_uploaded_file:
                if pdf_file.content_type not in {"application/pdf"}:
                    raise SummarizationError("Only PDF uploads are supported for files.")
                pdf_bytes = await pdf_file.read()

            summary = summarize_textbook_content(
                text=text_input,
                pdf_bytes=pdf_bytes,
                max_points=max_points,
                chapter_title=chapter_title,
                page_range=page_range,
                summary_style=summary_style,
                output_language=output_language,
            )
            return JSONResponse({"ok": True, "summary": summary})
        except SummarizationError as exc:
            return JSONResponse({"ok": False, "error": str(exc)}, status_code=400)
        except Exception:
            return JSONResponse(
                {"ok": False, "error": "Unexpected server error. Please try again."},
                status_code=500,
            )

    return app


app = create_summarizer_app()
