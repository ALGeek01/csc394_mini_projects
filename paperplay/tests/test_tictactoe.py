from paperplay.games.tictactoe.model import TicTacToeState, choose_ai_move


def test_tictactoe_winner_rows() -> None:
    s = TicTacToeState.new()
    s.board = ["X", "X", "X", None, None, None, None, None, None]
    assert s.winner() == "X"


def test_tictactoe_play_and_turn() -> None:
    s = TicTacToeState.new("X")
    s.play(0)
    assert s.board[0] == "X"
    assert s.turn == "O"


def test_tictactoe_ai_takes_winning_move() -> None:
    s = TicTacToeState.new("O")
    s.board = ["O", "O", None, None, "X", None, "X", None, None]
    move = choose_ai_move(s, "O")
    assert move == 2

