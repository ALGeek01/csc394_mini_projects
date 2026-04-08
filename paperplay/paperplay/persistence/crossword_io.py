from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from paperplay.persistence.crossword_schema import CrosswordPuzzle, SCHEMA_VERSION


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def puzzle_to_dict(p: CrosswordPuzzle) -> dict[str, Any]:
    d = asdict(p)
    # Ensure clue keys are serialized as strings for JSON stability.
    d["cluesAcross"] = {str(k): v for k, v in p.cluesAcross.items()}
    d["cluesDown"] = {str(k): v for k, v in p.cluesDown.items()}
    return d


def puzzle_from_dict(d: dict[str, Any]) -> CrosswordPuzzle:
    _require(int(d.get("schemaVersion", 0)) == SCHEMA_VERSION, "unsupported schemaVersion")
    width = int(d["width"])
    height = int(d["height"])
    blocks = d["blocks"]
    solution = d["solution"]
    _require(len(blocks) == height and all(len(r) == width for r in blocks), "bad blocks shape")
    _require(len(solution) == height and all(len(r) == width for r in solution), "bad solution shape")

    def parse_clues(raw: Any) -> dict[int, str]:
        _require(isinstance(raw, dict), "clues must be an object")
        out: dict[int, str] = {}
        for k, v in raw.items():
            out[int(k)] = str(v)
        return out

    return CrosswordPuzzle(
        schemaVersion=SCHEMA_VERSION,
        title=str(d.get("title", "")),
        author=str(d.get("author", "")),
        width=width,
        height=height,
        blocks=[[bool(x) for x in row] for row in blocks],
        solution=[[str(x) for x in row] for row in solution],
        cluesAcross=parse_clues(d.get("cluesAcross", {})),
        cluesDown=parse_clues(d.get("cluesDown", {})),
    )


def save_puzzle(path: str | Path, puzzle: CrosswordPuzzle) -> None:
    p = Path(path)
    p.write_text(json.dumps(puzzle_to_dict(puzzle), indent=2), encoding="utf-8")


def load_puzzle(path: str | Path) -> CrosswordPuzzle:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("invalid puzzle file")
    return puzzle_from_dict(data)

