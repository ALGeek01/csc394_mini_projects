from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

Player = Literal[1, 2]
Cell = Player | 0


def other(p: Player) -> Player:
    return 2 if p == 1 else 1


@dataclass
class Connect4State:
    rows: int = 6
    cols: int = 7
    board: list[list[Cell]] | None = None
    turn: Player = 1

    def __post_init__(self) -> None:
        if self.board is None:
            self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    @staticmethod
    def new() -> "Connect4State":
        return Connect4State()

    def copy(self) -> "Connect4State":
        assert self.board is not None
        return Connect4State(rows=self.rows, cols=self.cols, board=[r.copy() for r in self.board], turn=self.turn)

    def legal_moves(self) -> Iterable[int]:
        assert self.board is not None
        return [c for c in range(self.cols) if self.board[0][c] == 0 and self.winner() is None]

    def drop(self, col: int) -> tuple[int, int]:
        if col < 0 or col >= self.cols:
            raise ValueError("column out of range")
        if self.winner() is not None or self.is_draw():
            raise ValueError("game is over")
        assert self.board is not None
        if self.board[0][col] != 0:
            raise ValueError("column is full")
        for r in range(self.rows - 1, -1, -1):
            if self.board[r][col] == 0:
                self.board[r][col] = self.turn
                placed = (r, col)
                if self.winner() is None and not self.is_draw():
                    self.turn = other(self.turn)
                return placed
        raise ValueError("column is full")

    def is_draw(self) -> bool:
        assert self.board is not None
        return self.winner() is None and all(self.board[0][c] != 0 for c in range(self.cols))

    def winner(self) -> Player | None:
        assert self.board is not None
        b = self.board

        def in_bounds(r: int, c: int) -> bool:
            return 0 <= r < self.rows and 0 <= c < self.cols

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(self.rows):
            for c in range(self.cols):
                p = b[r][c]
                if p == 0:
                    continue
                for dr, dc in directions:
                    ok = True
                    for k in range(1, 4):
                        rr, cc = r + dr * k, c + dc * k
                        if not in_bounds(rr, cc) or b[rr][cc] != p:
                            ok = False
                            break
                    if ok:
                        return p  # type: ignore[return-value]
        return None


def choose_ai_move(state: Connect4State, ai: Player) -> int:
    """
    Deterministic, fast heuristic AI:
    - win if possible
    - block opponent win
    - prefer center-ish columns
    """
    legal = list(state.legal_moves())
    if not legal:
        raise ValueError("no legal moves")

    def would_win(col: int, p: Player) -> bool:
        s = state.copy()
        s.turn = p
        s.drop(col)
        return s.winner() == p

    for c in legal:
        if would_win(c, ai):
            return c
    opp = other(ai)
    for c in legal:
        if would_win(c, opp):
            return c

    center = state.cols // 2
    return sorted(legal, key=lambda c: (abs(c - center), c))[0]

