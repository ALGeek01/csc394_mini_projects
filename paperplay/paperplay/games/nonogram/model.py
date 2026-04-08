from __future__ import annotations

from dataclasses import dataclass


def line_clues(bits: list[int]) -> list[int]:
    clues: list[int] = []
    run = 0
    for b in bits:
        if b:
            run += 1
        else:
            if run:
                clues.append(run)
                run = 0
    if run:
        clues.append(run)
    return clues or [0]


def compute_clues(solution: list[list[int]]) -> tuple[list[list[int]], list[list[int]]]:
    rows = [line_clues(r) for r in solution]
    cols = [line_clues([solution[r][c] for r in range(len(solution))]) for c in range(len(solution[0]))]
    return rows, cols


@dataclass
class NonogramState:
    solution: list[list[int]]
    marks: list[list[int]]  # 0 unknown, 1 filled, -1 X

    @staticmethod
    def from_solution(solution: list[list[int]]) -> "NonogramState":
        h = len(solution)
        w = len(solution[0]) if h else 0
        if h == 0 or w == 0 or any(len(r) != w for r in solution):
            raise ValueError("invalid solution")
        marks = [[0 for _ in range(w)] for _ in range(h)]
        return NonogramState(solution=[r.copy() for r in solution], marks=marks)

    def toggle_fill(self, r: int, c: int) -> None:
        v = self.marks[r][c]
        self.marks[r][c] = 1 if v != 1 else 0

    def toggle_x(self, r: int, c: int) -> None:
        v = self.marks[r][c]
        self.marks[r][c] = -1 if v != -1 else 0

    def is_solved(self) -> bool:
        for r in range(len(self.solution)):
            for c in range(len(self.solution[0])):
                want = 1 if self.solution[r][c] else 0
                have = 1 if self.marks[r][c] == 1 else 0
                if want != have:
                    return False
        return True

