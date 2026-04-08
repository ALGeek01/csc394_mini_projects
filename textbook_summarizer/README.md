# Student Textbook Summarizer

Browser-based mini project for students to summarize assigned textbook chapters/pages into concise study bullets.

## Features

- Client/server architecture with FastAPI backend and browser UI.
- Accepts either pasted textbook text or PDF upload.
- Lets students choose summary length (2-6 bullet points).
- Textbook-focused context inputs (`chapter/topic`, `assigned pages`).
- Summary styles (`Quick Review`, `Exam Ready`, `Simple Language`).
- Configurable output language.
- User-friendly error handling for missing input, invalid file type, and API issues.

## Tech Stack

- **Server:** FastAPI + Uvicorn
- **Client:** HTML + CSS + JavaScript
- **AI:** OpenAI Chat Completions (`gpt-4o-mini`)
- **PDF Parsing:** `pypdf`

## Run Locally

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` from `.env.example` and set your API key:

```bash
cp .env.example .env
```

4. Start the server:

```bash
uvicorn app.main:app --reload
```

5. Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## API Endpoint

- `POST /api/summarize` (multipart form data)
  - `text_input` (optional if PDF is provided)
  - `pdf_file` (optional if text is provided, PDF only)
  - `chapter_title` (optional)
  - `page_range` (optional)
  - `max_points` (2-6 in UI)
  - `summary_style` (`quick-review`, `exam-ready`, `simple`)
  - `output_language` (default `English`)

## Documentation and Prompt Archive

- Project Manual: `docs/PROJECT_MANUAL.md`
- Prompt Archive: `prompt_archive/prompts.md`
