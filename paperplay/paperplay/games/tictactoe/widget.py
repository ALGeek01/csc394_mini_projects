from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from paperplay.games.tictactoe.model import TicTacToeState, choose_ai_move


class TicTacToeWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._state = TicTacToeState.new()
        self._ai_enabled = True
        self._ai_player: str = "O"

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("Tic‑Tac‑Toe")
        title.setStyleSheet("font-size: 20px; font-weight: 650;")
        root.addWidget(title)

        top = QHBoxLayout()
        self._ai_toggle = QCheckBox("Play vs AI (you are X)")
        self._ai_toggle.setChecked(True)
        self._ai_toggle.stateChanged.connect(self._on_ai_toggle)
        top.addWidget(self._ai_toggle)
        top.addStretch(1)

        self._btn_new = QPushButton("New game")
        self._btn_new.clicked.connect(self.reset)
        top.addWidget(self._btn_new)
        root.addLayout(top)

        self._status = QLabel("")
        self._status.setTextInteractionFlags(Qt.TextSelectableByMouse)
        root.addWidget(self._status)

        self._grid = QGridLayout()
        self._grid.setSpacing(8)
        root.addLayout(self._grid)

        self._cells: list[QPushButton] = []
        for r in range(3):
            for c in range(3):
                idx = r * 3 + c
                btn = QPushButton("")
                btn.setFixedSize(90, 90)
                btn.setStyleSheet("font-size: 24px; font-weight: 700;")
                btn.clicked.connect(lambda _=False, i=idx: self._click(i))
                self._cells.append(btn)
                self._grid.addWidget(btn, r, c)

        root.addStretch(1)
        self._sync()

    def reset(self) -> None:
        self._state = TicTacToeState.new("X")
        self._sync()

    def _on_ai_toggle(self) -> None:
        self._ai_enabled = self._ai_toggle.isChecked()
        self.reset()

    def _click(self, idx: int) -> None:
        try:
            self._state.play(idx)
        except ValueError:
            return
        self._sync()

        if self._ai_enabled and self._state.winner() is None and not self._state.is_draw():
            if self._state.turn == self._ai_player:
                ai_move = choose_ai_move(self._state, self._ai_player)  # type: ignore[arg-type]
                self._state.play(ai_move)
                self._sync()

    def _sync(self) -> None:
        for i, btn in enumerate(self._cells):
            v = self._state.board[i]
            btn.setText("" if v is None else v)
            btn.setEnabled(v is None and self._state.winner() is None and not self._state.is_draw())

        w = self._state.winner()
        if w is not None:
            self._status.setText(f"Winner: {w}")
        elif self._state.is_draw():
            self._status.setText("Draw.")
        else:
            self._status.setText(f"Turn: {self._state.turn}")

