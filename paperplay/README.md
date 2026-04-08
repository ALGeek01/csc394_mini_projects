# PaperPlay

PaperPlay is a desktop suite of classic pen-and-paper style games built with **Python + Qt (PySide6)**.

## Games (v1)
- Tic‑Tac‑Toe
- Connect 4
- Nim
- Hangman
- Dots and Boxes
- Sudoku
- Nonogram (Picross)
- Crossword (player + editor)

## Requirements
- Python 3.10+

## Setup
```bash
# If `python` isn't found on Windows, use `py` instead.
py -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
py -m pip install -U pip
py -m pip install -e ".[dev]"
```

## Run (desktop, PySide6)
```bash
py -m paperplay
```

## Web (browser, same hub as other CSC394 mini projects)

From the parent `CSC394_Mini_Projects` folder, start the hub and open **PaperPlay**:

```bash
uvicorn hub:app --reload --host 127.0.0.1 --port 8000
```

Then visit [http://127.0.0.1:8000/paperplay/](http://127.0.0.1:8000/paperplay/). The static UI lives in `../paperplay_web/` (HTML/CSS/JS) and mirrors this suite’s games for a consistent web experience.

## Tests
```bash
py -m pytest
```

## Crossword puzzles
Crosswords are saved as a **versioned JSON** file. See `[docs/CROSSWORD_FORMAT.md](docs/CROSSWORD_FORMAT.md)`.

