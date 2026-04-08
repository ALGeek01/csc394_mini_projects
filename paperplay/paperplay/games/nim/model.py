from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Player = Literal[1, 2]


def other(p: Player) -> Player:
    return 2 if p == 1 else 1


@dataclass
class NimState:
    pile: int
    max_take: int
    turn: Player = 1

    @staticmethod
    def new(pile: int = 21, max_take: int = 3) -> "NimState":
        if pile <= 0:
            raise ValueError("pile must be positive")
        if max_take <= 0:
            raise ValueError("max_take must be positive")
        return NimState(pile=pile, max_take=max_take, turn=1)

    def winner(self) -> Player | None:
        if self.pile == 0:
            # The player who made the last move won; turn has already advanced.
            return other(self.turn)
        return None

    def take(self, n: int) -> None:
        if self.winner() is not None:
            raise ValueError("game is over")
        if n < 1 or n > self.max_take:
            raise ValueError("illegal take")
        if n > self.pile:
            raise ValueError("not enough in pile")
        self.pile -= n
        # Always advance turn after a move so winner() can reliably compute
        # the last mover as other(self.turn) when pile hits 0.
        self.turn = other(self.turn)


def optimal_take(state: NimState) -> int:
    """
    Optimal strategy for one-pile subtraction game:
    leave a multiple of (max_take + 1) to opponent if possible.
    """
    k = state.max_take + 1
    r = state.pile % k
    if r == 0:
        return 1
    return min(r, state.max_take)

