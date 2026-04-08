from __future__ import annotations

import string
from dataclasses import dataclass

from paperplay.persistence.crossword_schema import CrosswordPuzzle, new_empty_puzzle


def is_block(p: CrosswordPuzzle, r: int, c: int) -> bool:
    return p.blocks[r][c]


def normalize_letter(ch: str) -> str:
    s = ch.strip().upper()
    if len(s) != 1 or s not in string.ascii_uppercase:
        return ""
    return s


def compute_numbers(blocks: list[list[bool]]) -> list[list[int]]:
    h = len(blocks)
    w = len(blocks[0]) if h else 0
    numbers = [[0 for _ in range(w)] for _ in range(h)]
    n = 1
    for r in range(h):
        for c in range(w):
            if blocks[r][c]:
                continue
            starts_across = (c == 0 or blocks[r][c - 1]) and (c + 1 < w and not blocks[r][c + 1])
            starts_down = (r == 0 or blocks[r - 1][c]) and (r + 1 < h and not blocks[r + 1][c])
            if starts_across or starts_down:
                numbers[r][c] = n
                n += 1
    return numbers


def extract_entries(blocks: list[list[bool]]) -> tuple[dict[int, list[tuple[int, int]]], dict[int, list[tuple[int, int]]]]:
    """
    Returns (across, down) mapping clueNumber -> list of (r,c) cells in that entry.
    """
    h = len(blocks)
    w = len(blocks[0]) if h else 0
    nums = compute_numbers(blocks)
    across: dict[int, list[tuple[int, int]]] = {}
    down: dict[int, list[tuple[int, int]]] = {}

    for r in range(h):
        c = 0
        while c < w:
            if blocks[r][c]:
                c += 1
                continue
            start = c
            while c < w and not blocks[r][c]:
                c += 1
            if c - start >= 2:
                num = nums[r][start]
                if num:
                    across[num] = [(r, cc) for cc in range(start, c)]
    for c in range(w):
        r = 0
        while r < h:
            if blocks[r][c]:
                r += 1
                continue
            start = r
            while r < h and not blocks[r][c]:
                r += 1
            if r - start >= 2:
                num = nums[start][c]
                if num:
                    down[num] = [(rr, c) for rr in range(start, r)]

    return across, down


def validate_puzzle(p: CrosswordPuzzle) -> list[str]:
    errors: list[str] = []
    if p.schemaVersion != 1:
        errors.append("Unsupported schemaVersion.")
    if p.width <= 0 or p.height <= 0:
        errors.append("Invalid dimensions.")
        return errors
    if len(p.blocks) != p.height or any(len(r) != p.width for r in p.blocks):
        errors.append("blocks shape mismatch.")
    if len(p.solution) != p.height or any(len(r) != p.width for r in p.solution):
        errors.append("solution shape mismatch.")

    # Ensure blocks and solution agree
    for r in range(p.height):
        for c in range(p.width):
            if p.blocks[r][c] and p.solution[r][c] != "":
                errors.append(f"Solution letter in block at ({r},{c}).")
                break

    # Ensure all non-block solution cells are A-Z or empty (allow empty while editing)
    for r in range(p.height):
        for c in range(p.width):
            if not p.blocks[r][c]:
                s = p.solution[r][c]
                if s != "" and (len(s) != 1 or s.upper() not in string.ascii_uppercase):
                    errors.append(f"Bad solution letter at ({r},{c}).")
                    break

    return errors


@dataclass
class CrosswordPlayState:
    puzzle: CrosswordPuzzle
    fill: list[list[str]]

    @staticmethod
    def from_puzzle(p: CrosswordPuzzle) -> "CrosswordPlayState":
        fill = [["" for _ in range(p.width)] for _ in range(p.height)]
        for r in range(p.height):
            for c in range(p.width):
                if p.blocks[r][c]:
                    fill[r][c] = ""
        return CrosswordPlayState(puzzle=p, fill=fill)

    def set_fill(self, r: int, c: int, ch: str) -> None:
        if self.puzzle.blocks[r][c]:
            return
        self.fill[r][c] = normalize_letter(ch)

    def is_solved(self) -> bool:
        for r in range(self.puzzle.height):
            for c in range(self.puzzle.width):
                if self.puzzle.blocks[r][c]:
                    continue
                want = self.puzzle.solution[r][c].upper()
                if not want:
                    return False
                if self.fill[r][c].upper() != want:
                    return False
        return True


def make_sample_puzzle() -> CrosswordPuzzle:
    # A tiny 7x7 sample (simple word fill). Blocks + solutions.
    p = new_empty_puzzle(7, 7, title="Sample 7×7", author="PaperPlay")
    blocks = [
        [0, 0, 0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 1, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 0],
    ]
    p = CrosswordPuzzle(
        **{
            **p.__dict__,
            "blocks": [[bool(x) for x in row] for row in blocks],
            "solution": [[("" if blocks[r][c] else "") for c in range(7)] for r in range(7)],
        }
    )
    # Fill solutions for non-blocks (symmetric-ish)
    # Row 0: "SUN" block "SKY"
    sol_rows = {
        0: "SUN#SKY",
        1: "A#I#E#O",
        2: "PAPERON",
        3: "##N#R##",
        4: "PENCILS",
        5: "E#A#I#U",
        6: "INK#PAD",
    }
    sol = [["" for _ in range(7)] for _ in range(7)]
    for r, srow in sol_rows.items():
        for c, ch in enumerate(srow):
            if ch == "#":
                continue
            sol[r][c] = ch
    p = CrosswordPuzzle(**{**p.__dict__, "solution": sol})

    across = {
        1: "Star at the center of our solar system",
        4: "Overhead blue expanse",
        5: "Writing surface material",
        6: "Writing tools (plural)",
        7: "Something you write with",
        8: "Rubber stamp partner",
    }
    down = {
        1: "Opposite of moon (in this puzzle's theme)",
        2: "Stationery item",
        3: "A small, simple word",
        4: "Something you can refill",
        6: "Vowel trio, sometimes",
    }
    return CrosswordPuzzle(**{**p.__dict__, "cluesAcross": across, "cluesDown": down})

