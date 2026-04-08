# LAST EXIT

**Repository:** [Last_Exit_Mini_Project](https://github.com/ALGeek01/Last_Exit_Mini_Project)

**GitHub “About” line (copy-paste):** Browser-based Python/Flask text adventure: a scientist, a sealed room, limbo, code & AI, a dream—and a final leap. Inspired by *A Dark Room*.

LAST EXIT is a small interactive fiction game for the browser. You play a computer scientist locked in a containment chamber, trying to save humanity—until the world stops behaving like reality. The story moves through denial, limbo, breaking out with programming and an emergent AI, a sunset that cannot be real, waking into a room with no exit, and an ending that turns on a leap of faith.

Stack: **Python 3**, **FastAPI** + **Uvicorn**, vanilla **HTML/CSS/JavaScript**. Story content lives in `story.json` so you can edit scenes without touching code.

## Run locally (this folder only)

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) (Uvicorn).

## Run from the course hub (all web mini projects)

From the `CSC394_Mini_Projects` directory (repo root):

```bash
pip install -r requirements.txt
uvicorn hub:app --reload --host 127.0.0.1 --port 8000
```

Then open [http://127.0.0.1:8000/last-exit/](http://127.0.0.1:8000/last-exit/).

If `python3 -m venv` fails (e.g. Python 3.14 `ensurepip` issues), try `/usr/bin/python3 -m venv .venv` on macOS or install Python 3.11–3.12 and use that for the virtual environment.

## Audio

- Click the speaker control once to **enable** sound (browsers block autoplay until you interact).
- Optional: add a loopable file as `static/ambient.ogg` or `static/ambient.mp3` for richer ambience.
- If those files are missing, the game uses a **quiet built-in hum** (Web Audio) so something still plays.

## Credits

Narrative inspired by the mood of [A Dark Room](https://adarkroom.doublespeakgames.com/) (Doublespeak Games). This project is an original student mini-project and is not affiliated with that game.
