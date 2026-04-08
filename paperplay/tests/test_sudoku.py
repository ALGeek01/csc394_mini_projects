from paperplay.games.sudoku.model import SudokuState, is_valid_grid


def test_sudoku_rejects_invalid_move() -> None:
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    s = SudokuState.from_puzzle(puzzle)
    assert is_valid_grid(s.grid)
    # Put a 5 in row 0 col 2 would duplicate 5 in row 0.
    try:
        s.set_cell(0, 2, 5)
        assert False, "expected invalid move"
    except ValueError:
        pass

