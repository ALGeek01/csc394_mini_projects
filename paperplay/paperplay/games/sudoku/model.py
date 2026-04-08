from __future__ import annotations

from dataclasses import dataclass


def _valid_unit(nums: list[int]) -> bool:
    seen: set[int] = set()
    for n in nums:
        if n == 0:
            continue
        if n < 0 or n > 9:
            return False
        if n in seen:
            return False
        seen.add(n)
    return True


def is_valid_grid(grid: list[list[int]]) -> bool:
    if len(grid) != 9 or any(len(r) != 9 for r in grid):
        return False
    # rows
    for r in range(9):
        if not _valid_unit(grid[r]):
            return False
    # cols
    for c in range(9):
        if not _valid_unit([grid[r][c] for r in range(9)]):
            return False
    # boxes
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            unit = [grid[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)]
            if not _valid_unit(unit):
                return False
    return True


def is_solved(grid: list[list[int]]) -> bool:
    return is_valid_grid(grid) and all(all(n != 0 for n in row) for row in grid)


@dataclass
class SudokuState:
    given: list[list[int]]
    grid: list[list[int]]

    @staticmethod
    def from_puzzle(puzzle: list[list[int]]) -> "SudokuState":
        given = [row.copy() for row in puzzle]
        grid = [row.copy() for row in puzzle]
        if not is_valid_grid(grid):
            raise ValueError("invalid puzzle")
        return SudokuState(given=given, grid=grid)

    def set_cell(self, r: int, c: int, val: int) -> None:
        if not (0 <= r < 9 and 0 <= c < 9):
            raise ValueError("out of bounds")
        if self.given[r][c] != 0:
            raise ValueError("cannot change given cell")
        if val not in range(0, 10):
            raise ValueError("value must be 0..9")
        self.grid[r][c] = val
        if not is_valid_grid(self.grid):
            # revert and reject
            self.grid[r][c] = 0
            raise ValueError("move makes grid invalid")

