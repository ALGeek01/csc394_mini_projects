from paperplay.games.nim.model import NimState, optimal_take


def test_nim_optimal_take_leaves_multiple() -> None:
    s = NimState.new(pile=10, max_take=3)
    t = optimal_take(s)
    assert 1 <= t <= 3
    s.take(t)
    assert s.pile % 4 == 0


def test_nim_winner_after_taking_last() -> None:
    s = NimState.new(pile=1, max_take=3)
    s.take(1)
    assert s.winner() == 1

