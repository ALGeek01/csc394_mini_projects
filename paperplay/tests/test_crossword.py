from paperplay.games.crossword.model import compute_numbers, extract_entries
from paperplay.persistence.crossword_io import puzzle_from_dict, puzzle_to_dict
from paperplay.persistence.crossword_schema import new_empty_puzzle


def test_crossword_numbering_starts_entries() -> None:
    # 3x3 with center block, should start across/down at corners where length >=2
    blocks = [
        [False, False, False],
        [False, True, False],
        [False, False, False],
    ]
    nums = compute_numbers(blocks)
    # Top-left starts across and down
    assert nums[0][0] == 1
    across, down = extract_entries(blocks)
    assert 1 in across
    assert 1 in down


def test_crossword_roundtrip_json() -> None:
    p = new_empty_puzzle(5, 5, title="T", author="A")
    d = puzzle_to_dict(p)
    p2 = puzzle_from_dict(d)
    assert p2.width == 5 and p2.height == 5
    assert p2.title == "T"

