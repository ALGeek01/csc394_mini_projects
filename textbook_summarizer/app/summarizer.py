from __future__ import annotations

import os
from io import BytesIO
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

load_dotenv()


class SummarizationError(Exception):
    """Raised when summarization fails in a user-facing way."""


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        chunks = []
        for page in reader.pages:
            chunks.append(page.extract_text() or "")
        return "\n".join(chunks).strip()
    except Exception as exc:  # noqa: BLE001 - return clean error to user
        raise SummarizationError(f"Unable to read PDF file: {exc}") from exc


def _build_assignment_prompt(
    text: str,
    max_points: int,
    chapter_title: Optional[str],
    page_range: Optional[str],
    summary_style: str,
    output_language: str,
) -> str:
    style_map = {
        "quick-review": "Focus on a fast review before class.",
        "exam-ready": "Focus on concepts likely to appear on a quiz or exam.",
        "simple": "Use simple wording a younger student could understand.",
    }
    style_instruction = style_map.get(summary_style, style_map["quick-review"])
    chapter_hint = f"Chapter title/topic: {chapter_title}\n" if chapter_title else ""
    page_hint = f"Assigned pages: {page_range}\n" if page_range else ""
    return (
        "You are a study assistant for textbook assignments.\n"
        "Create a concise summary from the provided textbook passage.\n"
        f"Return exactly {max_points} bullet points.\n"
        f"Output language: {output_language}.\n"
        f"{style_instruction}\n"
        "Each bullet must contain one high-value idea from the source.\n"
        "Do not invent facts not present in the source.\n\n"
        f"{chapter_hint}"
        f"{page_hint}"
        "Textbook assignment content:\n"
        f"{text}"
    )


def summarize_textbook_content(
    text: Optional[str],
    pdf_bytes: Optional[bytes],
    max_points: int,
    chapter_title: Optional[str] = None,
    page_range: Optional[str] = None,
    summary_style: str = "quick-review",
    output_language: str = "English",
) -> str:
    if not (1 <= max_points <= 10):
        raise SummarizationError("Summary length must be between 1 and 10 bullet points.")

    source_text = (text or "").strip()
    if pdf_bytes:
        source_text = _extract_pdf_text(pdf_bytes)

    if not source_text:
        raise SummarizationError("No readable text was provided. Paste text or upload a valid PDF.")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SummarizationError(
            "Missing OPENAI_API_KEY in environment. Add it to your .env file."
        )

    try:
        client = OpenAI(api_key=api_key)
        prompt = _build_assignment_prompt(
            text=source_text,
            max_points=max_points,
            chapter_title=chapter_title,
            page_range=page_range,
            summary_style=summary_style,
            output_language=output_language,
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You create study-friendly textbook summaries.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=320,
            temperature=0.2,
        )
    except Exception as exc:  # noqa: BLE001 - return clean error to user
        message = str(exc)
        if "invalid_api_key" in message or "Incorrect API key provided" in message:
            raise SummarizationError(
                "Invalid OPENAI_API_KEY. Update your .env file with a valid key and restart the server."
            ) from exc
        raise SummarizationError(f"Summarization request failed: {exc}") from exc

    content = (response.choices[0].message.content or "").strip()
    if not content:
        raise SummarizationError("Model returned an empty summary. Please try again.")

    return content
