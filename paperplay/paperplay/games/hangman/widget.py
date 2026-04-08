from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from paperplay.games.hangman.model import HangmanState, choose_word
from paperplay.games.hangman.words import WORDS_EASY, WORDS_HARD, WORDS_MEDIUM


class HangmanWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._state: HangmanState | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("Hangman")
        title.setStyleSheet("font-size: 20px; font-weight: 650;")
        root.addWidget(title)

        top = QHBoxLayout()
        top.addWidget(QLabel("Difficulty:"))
        self._difficulty = QComboBox()
        self._difficulty.addItems(["Easy", "Medium", "Hard"])
        top.addWidget(self._difficulty)
        top.addStretch(1)
        self._btn_new = QPushButton("New word")
        self._btn_new.clicked.connect(self.reset)
        top.addWidget(self._btn_new)
        root.addLayout(top)

        self._status = QLabel("")
        self._status.setTextInteractionFlags(Qt.TextSelectableByMouse)
        root.addWidget(self._status)

        self._masked = QLabel("")
        self._masked.setStyleSheet("font-size: 22px; font-weight: 700; letter-spacing: 2px;")
        root.addWidget(self._masked)

        self._guessed = QLabel("")
        self._guessed.setWordWrap(True)
        root.addWidget(self._guessed)

        row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setMaxLength(1)
        self._input.setPlaceholderText("Type a letter…")
        self._input.returnPressed.connect(self._do_guess)
        row.addWidget(self._input, 1)
        self._btn_guess = QPushButton("Guess")
        self._btn_guess.clicked.connect(self._do_guess)
        row.addWidget(self._btn_guess)
        root.addLayout(row)

        root.addStretch(1)
        self.reset()

    def reset(self) -> None:
        words = {"Easy": WORDS_EASY, "Medium": WORDS_MEDIUM, "Hard": WORDS_HARD}[self._difficulty.currentText()]
        self._state = HangmanState.new(choose_word(words), lives=6)
        self._input.setText("")
        self._sync()

    def _do_guess(self) -> None:
        if self._state is None:
            return
        ch = self._input.text().strip()
        self._input.setText("")
        if not ch:
            return
        try:
            self._state.guess(ch[0])
        except ValueError:
            return
        self._sync()

    def _sync(self) -> None:
        s = self._state
        assert s is not None

        if s.is_won():
            self._status.setText(f"You won! Word: {s.word}")
        elif s.is_lost():
            self._status.setText(f"You lost. Word was: {s.word}")
        else:
            self._status.setText(f"Lives: {s.lives}")

        self._masked.setText(s.masked())
        self._guessed.setText("Guessed: " + ", ".join(sorted(s.guessed)) if s.guessed else "Guessed: (none)")

        enabled = not (s.is_won() or s.is_lost())
        self._btn_guess.setEnabled(enabled)
        self._input.setEnabled(enabled)

