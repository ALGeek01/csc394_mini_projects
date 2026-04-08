from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

Player = Literal["X", "O"]
Cell = Player | None


def _other(p: Player) -> Player:
    return "O" if p == "X" else "X"


_WIN_LINES: tuple[tuple[int, int, int], ...] = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


@dataclass
class TicTacToeState:
    board: list[Cell]
    turn: Player

    @staticmethod
    def new(start: Player = "X") -> "TicTacToeState":
        return TicTacToeState(board=[None] * 9, turn=start)

    def winner(self) -> Player | None:
        b = self.board
        for a, c, d in _WIN_LINES:
            if b[a] is not None and b[a] == b[c] == b[d]:
                return b[a]
        return None

    def is_draw(self) -> bool:
        return self.winner() is None and all(x is not None for x in self.board)

    def legal_moves(self) -> Iterable[int]:
        if self.winner() is not None:
            return []
        return [i for i, c in enumerate(self.board) if c is None]

    def play(self, idx: int) -> None:
        if idx < 0 or idx >= 9:
            raise ValueError("move out of range")
        if self.winner() is not None or self.is_draw():
            raise ValueError("game is over")
        if self.board[idx] is not None:
            raise ValueError("cell already taken")
        self.board[idx] = self.turn
        if self.winner() is None and not self.is_draw():
            self.turn = _other(self.turn)


def choose_ai_move(state: TicTacToeState, ai_player: Player) -> int:
    """
    Deterministic minimax (small state space); returns a move index 0..8.
    """

    def score(s: TicTacToeState) -> int:
        w = s.winner()
        if w == ai_player:
            return 1
        if w is not None and w != ai_player:
            return -1
        if s.is_draw():
            return 0

        maximizing = s.turn == ai_player
        best = -2 if maximizing else 2
        for m in s.legal_moves():
            nxt = TicTacToeState(board=s.board.copy(), turn=s.turn)
            nxt.play(m)
            v = score(nxt)
            if maximizing:
                best = max(best, v)
                if best == 1:
                    break
            else:
                best = min(best, v)
                if best == -1:
                    break
        return best

    best_move = None
    best_val = -2
    for m in state.legal_moves():
        nxt = TicTacToeState(board=state.board.copy(), turn=state.turn)
        nxt.play(m)
        v = score(nxt)
        if v > best_val or best_move is None:
            best_val = v
            best_move = m

    if best_move is None:
        raise ValueError("no legal moves")
    return best_move

