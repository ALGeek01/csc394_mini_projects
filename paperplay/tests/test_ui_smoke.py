def test_import_widgets_smoke() -> None:
    # Importing widgets should not require a running QApplication.
    from paperplay.games.connect4.widget import Connect4Widget
    from paperplay.games.crossword.widget import CrosswordWidget
    from paperplay.games.dotsboxes.widget import DotsAndBoxesWidget
    from paperplay.games.hangman.widget import HangmanWidget
    from paperplay.games.nim.widget import NimWidget
    from paperplay.games.nonogram.widget import NonogramWidget
    from paperplay.games.sudoku.widget import SudokuWidget
    from paperplay.games.tictactoe.widget import TicTacToeWidget

    assert all(
        cls is not None
        for cls in (
            TicTacToeWidget,
            Connect4Widget,
            NimWidget,
            HangmanWidget,
            DotsAndBoxesWidget,
            SudokuWidget,
            NonogramWidget,
            CrosswordWidget,
        )
    )

