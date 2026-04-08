# CSC394 mini projects

Unified **FastAPI + Uvicorn** hub for local web mini projects: textbook summarizer, LAST EXIT, white noise, PaperPlay (browser), and related assets.

## Run the hub

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn hub:app --reload --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Textbook summarizer (OpenAI)

Copy `textbook_summarizer/.env.example` to `.env` and set `OPENAI_API_KEY`.

## Layout

| Path | Description |
|------|-------------|
| `hub.py` | Mounts all web apps |
| `textbook_summarizer/` | FastAPI summarizer |
| `last_exit/` | Interactive fiction |
| `white_noise/` | Static white-noise UI |
| `paperplay_web/` | PaperPlay games in the browser |
| `paperplay/` | Optional PySide6 desktop suite |
