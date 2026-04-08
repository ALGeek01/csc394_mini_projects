from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

Player = Literal[1, 2]


def other(p: Player) -> Player:
    return 2 if p == 1 else 1


@dataclass
class DotsAndBoxesState:
    """
    Board is defined by a dot grid of size (dots_rows x dots_cols).
    Boxes are (dots_rows-1) x (dots_cols-1).

    Edges:
      - h[r][c] is the horizontal edge between dot(r,c) and dot(r,c+1), for r in [0..dots_rows-1], c in [0..dots_cols-2]
      - v[r][c] is the vertical edge between dot(r,c) and dot(r+1,c), for r in [0..dots_rows-2], c in [0..dots_cols-1]
    Each edge is 0 (empty) or 1/2 (claimed by player).
    """

    dots_rows: int = 5
    dots_cols: int = 5
    turn: Player = 1
    h: list[list[int]] | None = None
    v: list[list[int]] | None = None
    boxes: list[list[int]] | None = None  # owner of completed box (0 if none)
    score1: int = 0
    score2: int = 0

    def __post_init__(self) -> None:
        if self.dots_rows < 2 or self.dots_cols < 2:
            raise ValueError("Need at least 2x2 dots")
        if self.h is None:
            self.h = [[0 for _ in range(self.dots_cols - 1)] for _ in range(self.dots_rows)]
        if self.v is None:
            self.v = [[0 for _ in range(self.dots_cols)] for _ in range(self.dots_rows - 1)]
        if self.boxes is None:
            self.boxes = [[0 for _ in range(self.dots_cols - 1)] for _ in range(self.dots_rows - 1)]

    @staticmethod
    def new(dots_rows: int = 5, dots_cols: int = 5) -> "DotsAndBoxesState":
        return DotsAndBoxesState(dots_rows=dots_rows, dots_cols=dots_cols, turn=1)

    def is_over(self) -> bool:
        assert self.h is not None and self.v is not None
        return all(e != 0 for row in self.h for e in row) and all(e != 0 for row in self.v for e in row)

    def winner(self) -> Player | None:
        if not self.is_over():
            return None
        if self.score1 > self.score2:
            return 1
        if self.score2 > self.score1:
            return 2
        return None

    def legal_moves(self) -> Iterable[tuple[str, int, int]]:
        assert self.h is not None and self.v is not None
        for r in range(self.dots_rows):
            for c in range(self.dots_cols - 1):
                if self.h[r][c] == 0:
                    yield ("h", r, c)
        for r in range(self.dots_rows - 1):
            for c in range(self.dots_cols):
                if self.v[r][c] == 0:
                    yield ("v", r, c)

    def play_edge(self, kind: str, r: int, c: int) -> int:
        """
        Plays an edge. Returns number of boxes completed by this move.
        If a player completes >=1 boxes, they keep the turn; otherwise turn switches.
        """
        if self.is_over():
            raise ValueError("game is over")
        assert self.h is not None and self.v is not None and self.boxes is not None

        if kind == "h":
            if not (0 <= r < self.dots_rows and 0 <= c < self.dots_cols - 1):
                raise ValueError("out of bounds")
            if self.h[r][c] != 0:
                raise ValueError("edge already taken")
            self.h[r][c] = int(self.turn)
        elif kind == "v":
            if not (0 <= r < self.dots_rows - 1 and 0 <= c < self.dots_cols):
                raise ValueError("out of bounds")
            if self.v[r][c] != 0:
                raise ValueError("edge already taken")
            self.v[r][c] = int(self.turn)
        else:
            raise ValueError("kind must be 'h' or 'v'")

        completed = 0
        for br, bc in self._affected_boxes(kind, r, c):
            if self.boxes[br][bc] == 0 and self._is_box_complete(br, bc):
                self.boxes[br][bc] = int(self.turn)
                completed += 1
                if self.turn == 1:
                    self.score1 += 1
                else:
                    self.score2 += 1

        if completed == 0:
            self.turn = other(self.turn)
        return completed

    def _affected_boxes(self, kind: str, r: int, c: int) -> list[tuple[int, int]]:
        boxes: list[tuple[int, int]] = []
        if kind == "h":
            # horizontal edge is top of box at (r, c) (if r < boxes_rows)
            if r < self.dots_rows - 1:
                boxes.append((r, c))
            # and bottom of box at (r-1, c) (if r > 0)
            if r > 0:
                boxes.append((r - 1, c))
        else:  # v
            # vertical edge is left of box at (r, c) (if c < boxes_cols)
            if c < self.dots_cols - 1:
                boxes.append((r, c))
            # and right of box at (r, c-1) (if c > 0)
            if c > 0:
                boxes.append((r, c - 1))
        return boxes

    def _is_box_complete(self, br: int, bc: int) -> bool:
        assert self.h is not None and self.v is not None
        # box at (br, bc) is bounded by:
        # top h[br][bc], bottom h[br+1][bc], left v[br][bc], right v[br][bc+1]
        return (
            self.h[br][bc] != 0
            and self.h[br + 1][bc] != 0
            and self.v[br][bc] != 0
            and self.v[br][bc + 1] != 0
        )

