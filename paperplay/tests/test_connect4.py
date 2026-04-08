from paperplay.games.connect4.model import Connect4State, choose_ai_move


def test_connect4_drop_and_winner_horizontal() -> None:
    s = Connect4State.new()
    # Force a horizontal win for Player 1 on bottom row.
    for c in range(4):
        s.turn = 1
        s.drop(c)
    assert s.winner() == 1


def test_connect4_ai_blocks_immediate_win() -> None:
    s = Connect4State.new()
    # Player 1 has three in a row on bottom: cols 0,1,2; winning move would be col 3
    s.turn = 1
    s.drop(0)
    s.turn = 2
    s.drop(6)
    s.turn = 1
    s.drop(1)
    s.turn = 2
    s.drop(6)
    s.turn = 1
    s.drop(2)

    assert choose_ai_move(s, 2) == 3

