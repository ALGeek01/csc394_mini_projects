# Project Manual

## Mini Project: Student Textbook Summarizer

### Project Overview

This mini project is a browser-based client/server application that helps students summarize assigned textbook chapters/pages into short bullet points.

Users can either:

- paste textbook text directly in the browser, or
- upload a textbook PDF file.

The server processes user input and sends it to an LLM for concise, study-friendly summaries.

### Requirements Mapping

- **Domain & AI collaboration tools:** Implemented in education domain with AI-assisted design, coding, and documentation.
- **Client/server architecture:** Browser client + FastAPI server (`app/main.py`).
- **LLM integration:** Real-time OpenAI API call in `app/summarizer.py`.
- **User input via browser:** Form UI in `app/templates/index.html`.
- **Server-side processing:** Input validation, PDF extraction, prompt construction, and LLM call in backend code.
- **Documentation:** This project manual plus repository README and archived prompts.
- **Prompt archiving:** Stored electronically in `prompt_archive/prompts.md` and referenced in formal documentation.

### How AI Was Used

#### 1) AI for Design

AI collaboration was used to shape the mini project scope and architecture:

- selected a student-focused textbook summarization workflow,
- defined client/server responsibilities,
- identified key UX inputs (chapter/topic, assigned pages, summary style, output language),
- designed robust error paths and validation behavior.

#### 2) AI for Code Implementation

AI collaboration assisted in implementing:

- FastAPI API route and input handling,
- PDF extraction and error-safe processing,
- LLM prompt engineering tuned for textbook study support,
- browser-side JavaScript form submission and response handling,
- iterative refinements for summary styles and educational use context.

#### 3) AI for Documentation

AI collaboration helped draft:

- project setup and usage instructions,
- requirements-to-implementation mapping,
- this formal project manual section,
- archived prompt records and rationale.

### Architecture Summary

- **Frontend (browser):**
  - `app/templates/index.html`
  - `app/static/styles.css`
  - `app/static/app.js`
- **Backend (server):**
  - `app/main.py` (routes + request handling)
  - `app/summarizer.py` (PDF parse + prompt + LLM integration)
- **Documentation & prompts:**
  - `README.md`
  - `docs/PROJECT_MANUAL.md`
  - `prompt_archive/prompts.md`

### Prompt Archive Inclusion

Prompt records are archived at `prompt_archive/prompts.md` and are part of the formal project documentation package for this mini project.

### Local Run Instructions

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Create `.env` with `OPENAI_API_KEY`.
3. Run server:
   - `uvicorn app.main:app --reload`
4. Use browser client at:
   - `http://127.0.0.1:8000`
