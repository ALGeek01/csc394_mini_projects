from paperplay.games.nonogram.model import compute_clues, line_clues


def test_nonogram_line_clues() -> None:
    assert line_clues([0, 0, 0]) == [0]
    assert line_clues([1, 1, 0, 1]) == [2, 1]


def test_nonogram_compute_clues_shape() -> None:
    sol = [
        [1, 0, 1],
        [1, 1, 0],
    ]
    rows, cols = compute_clues(sol)
    assert rows == [[1, 1], [2]]
    assert cols == [[2], [1], [1]]

