from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class GameInfo:
    game_id: str
    title: str
    category: str
    description: str
    create_widget: Callable[[], QWidget]


def get_game_catalog() -> list[GameInfo]:
    # Imported lazily to keep startup quick and avoid Qt init issues during tests.
    from paperplay.games.connect4.widget import Connect4Widget
    from paperplay.games.crossword.widget import CrosswordWidget
    from paperplay.games.dotsboxes.widget import DotsAndBoxesWidget
    from paperplay.games.hangman.widget import HangmanWidget
    from paperplay.games.nim.widget import NimWidget
    from paperplay.games.nonogram.widget import NonogramWidget
    from paperplay.games.sudoku.widget import SudokuWidget
    from paperplay.games.tictactoe.widget import TicTacToeWidget

    # Grid games and crossword will be added as they land.
    return [
        GameInfo(
            game_id="tictactoe",
            title="Tic-Tac-Toe",
            category="Classic",
            description="3×3 strategy: get three in a row. 1P vs AI or 2P local.",
            create_widget=TicTacToeWidget,
        ),
        GameInfo(
            game_id="connect4",
            title="Connect 4",
            category="Classic",
            description="Drop discs into a 7×6 grid. 1P vs AI or 2P local.",
            create_widget=Connect4Widget,
        ),
        GameInfo(
            game_id="nim",
            title="Nim",
            category="Math",
            description="Take 1..k from a pile; last move wins. Includes optimal AI.",
            create_widget=NimWidget,
        ),
        GameInfo(
            game_id="hangman",
            title="Hangman",
            category="Word",
            description="Guess the word one letter at a time before you run out of lives.",
            create_widget=HangmanWidget,
        ),
        GameInfo(
            game_id="dotsboxes",
            title="Dots and Boxes",
            category="Classic",
            description="Draw lines to complete boxes. Completing a box gives you another turn.",
            create_widget=DotsAndBoxesWidget,
        ),
        GameInfo(
            game_id="sudoku",
            title="Sudoku",
            category="Puzzle",
            description="Fill the 9×9 grid so each row, column, and 3×3 box has 1–9.",
            create_widget=SudokuWidget,
        ),
        GameInfo(
            game_id="nonogram",
            title="Nonogram (Picross)",
            category="Puzzle",
            description="Use numeric clues to fill cells and reveal the picture.",
            create_widget=NonogramWidget,
        ),
        GameInfo(
            game_id="crossword",
            title="Crossword",
            category="Word",
            description="Play crosswords or edit your own puzzles (JSON).",
            create_widget=CrosswordWidget,
        ),
    ]

