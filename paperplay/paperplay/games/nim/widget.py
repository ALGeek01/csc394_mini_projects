from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from paperplay.games.nim.model import NimState, optimal_take


class NimWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._state = NimState.new()
        self._ai_enabled = True
        self._ai_player = 2

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("Nim")
        title.setStyleSheet("font-size: 20px; font-weight: 650;")
        root.addWidget(title)

        top = QHBoxLayout()
        self._ai_toggle = QCheckBox("Play vs optimal AI (you are Player 1)")
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

        self._pile_label = QLabel("")
        self._pile_label.setStyleSheet("font-size: 16px;")
        root.addWidget(self._pile_label)

        row = QHBoxLayout()
        row.addWidget(QLabel("Take:"))
        self._take = QSpinBox()
        self._take.setRange(1, self._state.max_take)
        row.addWidget(self._take)
        self._btn_take = QPushButton("Take")
        self._btn_take.clicked.connect(self._do_take)
        row.addWidget(self._btn_take)
        row.addStretch(1)
        root.addLayout(row)

        root.addStretch(1)
        self._sync()

    def reset(self) -> None:
        self._state = NimState.new()
        self._sync()

    def _on_ai_toggle(self) -> None:
        self._ai_enabled = self._ai_toggle.isChecked()
        self.reset()

    def _do_take(self) -> None:
        try:
            self._state.take(int(self._take.value()))
        except ValueError:
            return
        self._sync()

        if self._ai_enabled and self._state.winner() is None and self._state.turn == self._ai_player:
            self._state.take(optimal_take(self._state))
            self._sync()

    def _sync(self) -> None:
        w = self._state.winner()
        if w is not None:
            self._status.setText(f"Winner: Player {w}")
        else:
            self._status.setText(f"Turn: Player {self._state.turn}")

        self._pile_label.setText(f"Pile remaining: {self._state.pile}")
        self._take.setRange(1, min(self._state.max_take, max(1, self._state.pile)))
        enabled = w is None
        self._btn_take.setEnabled(enabled)
        self._take.setEnabled(enabled)

