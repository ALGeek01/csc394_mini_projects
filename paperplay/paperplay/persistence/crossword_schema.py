from __future__ import annotations

from dataclasses import dataclass


SCHEMA_VERSION = 1


@dataclass(frozen=True)
class CrosswordClues:
    across: dict[int, str]
    down: dict[int, str]


@dataclass(frozen=True)
class CrosswordPuzzle:
    schemaVersion: int
    title: str
    author: str
    width: int
    height: int
    blocks: list[list[bool]]  # True if block
    solution: list[list[str]]  # uppercase letters or "" for block
    cluesAcross: dict[int, str]
    cluesDown: dict[int, str]


def new_empty_puzzle(width: int = 9, height: int = 9, title: str = "Untitled", author: str = "") -> CrosswordPuzzle:
    if width < 3 or height < 3:
        raise ValueError("min size is 3x3")
    blocks = [[False for _ in range(width)] for _ in range(height)]
    solution = [["" for _ in range(width)] for _ in range(height)]
    return CrosswordPuzzle(
        schemaVersion=SCHEMA_VERSION,
        title=title,
        author=author,
        width=width,
        height=height,
        blocks=blocks,
        solution=solution,
        cluesAcross={},
        cluesDown={},
    )

