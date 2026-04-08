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

from paperplay.games.connect4.model import Connect4State, choose_ai_move


class Connect4Widget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._state = Connect4State.new()
        self._ai_enabled = True
        self._ai_player = 2

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("Connect 4")
        title.setStyleSheet("font-size: 20px; font-weight: 650;")
        root.addWidget(title)

        top = QHBoxLayout()
        self._ai_toggle = QCheckBox("Play vs AI (you are Player 1)")
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
        self._grid.setSpacing(6)
        root.addLayout(self._grid)

        self._drop_buttons: list[QPushButton] = []
        for c in range(self._state.cols):
            b = QPushButton("↓")
            b.setFixedHeight(34)
            b.clicked.connect(lambda _=False, col=c: self._drop(col))
            self._drop_buttons.append(b)
            self._grid.addWidget(b, 0, c)

        self._cells: list[list[QLabel]] = []
        for r in range(self._state.rows):
            row: list[QLabel] = []
            for c in range(self._state.cols):
                lab = QLabel(" ")
                lab.setAlignment(Qt.AlignCenter)
                lab.setFixedSize(48, 48)
                lab.setStyleSheet(
                    "border: 1px solid rgba(0,0,0,0.25); border-radius: 8px; font-size: 18px; font-weight: 700;"
                )
                row.append(lab)
                self._grid.addWidget(lab, r + 1, c)
            self._cells.append(row)

        root.addStretch(1)
        self._sync()

    def reset(self) -> None:
        self._state = Connect4State.new()
        self._sync()

    def _on_ai_toggle(self) -> None:
        self._ai_enabled = self._ai_toggle.isChecked()
        self.reset()

    def _drop(self, col: int) -> None:
        try:
            self._state.drop(col)
        except ValueError:
            return
        self._sync()

        if self._ai_enabled and self._state.winner() is None and not self._state.is_draw():
            if self._state.turn == self._ai_player:
                ai_col = choose_ai_move(self._state, self._ai_player)
                self._state.drop(ai_col)
                self._sync()

    def _sync(self) -> None:
        b = self._state.board
        assert b is not None
        for r in range(self._state.rows):
            for c in range(self._state.cols):
                v = b[r][c]
                self._cells[r][c].setText(" " if v == 0 else ("●" if v == 1 else "○"))

        w = self._state.winner()
        if w is not None:
            self._status.setText(f"Winner: Player {w}")
        elif self._state.is_draw():
            self._status.setText("Draw.")
        else:
            self._status.setText(f"Turn: Player {self._state.turn}")

        enable = w is None and not self._state.is_draw()
        for c, btn in enumerate(self._drop_buttons):
            btn.setEnabled(enable and b[0][c] == 0)

