from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from paperplay.games.nonogram.model import NonogramState, compute_clues
from paperplay.games.nonogram.puzzles import PUZZLES


class NonogramWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._puzzle_idx = 0
        self._state = NonogramState.from_solution(PUZZLES[0]["grid"])

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("Nonogram (Picross)")
        title.setStyleSheet("font-size: 20px; font-weight: 650;")
        root.addWidget(title)

        top = QHBoxLayout()
        top.addWidget(QLabel("Puzzle:"))
        self._puzzle = QComboBox()
        self._puzzle.addItems([p["title"] for p in PUZZLES])
        self._puzzle.currentIndexChanged.connect(self.reset)
        top.addWidget(self._puzzle)
        top.addStretch(1)
        self._btn_reset = QPushButton("Reset")
        self._btn_reset.clicked.connect(self.reset)
        top.addWidget(self._btn_reset)
        self._btn_check = QPushButton("Check solved")
        self._btn_check.clicked.connect(self._check)
        top.addWidget(self._btn_check)
        root.addLayout(top)

        self._status = QLabel("Left click toggles fill. Right click toggles X.")
        self._status.setWordWrap(True)
        root.addWidget(self._status)

        self._grid = QGridLayout()
        self._grid.setSpacing(2)
        root.addLayout(self._grid)

        root.addStretch(1)
        self._rebuild()

    def reset(self) -> None:
        self._puzzle_idx = self._puzzle.currentIndex()
        self._state = NonogramState.from_solution(PUZZLES[self._puzzle_idx]["grid"])
        self._rebuild()

    def _rebuild(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)

        sol = PUZZLES[self._puzzle_idx]["grid"]
        row_clues, col_clues = compute_clues(sol)
        h, w = len(sol), len(sol[0])

        # clue headers
        self._grid.addWidget(QLabel(""), 0, 0)
        for c in range(w):
            lab = QLabel("\n".join(str(x) for x in col_clues[c]))
            lab.setAlignment(Qt.AlignCenter)
            lab.setStyleSheet("font-size: 11px;")
            self._grid.addWidget(lab, 0, c + 1)
        for r in range(h):
            lab = QLabel(" ".join(str(x) for x in row_clues[r]))
            lab.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lab.setStyleSheet("font-size: 11px; padding-right: 6px;")
            self._grid.addWidget(lab, r + 1, 0)

        self._cells: list[list[QPushButton]] = []
        for r in range(h):
            row: list[QPushButton] = []
            for c in range(w):
                btn = QPushButton("")
                btn.setFixedSize(28, 28)
                btn.setFocusPolicy(Qt.NoFocus)
                btn.clicked.connect(lambda _=False, r=r, c=c: self._left(r, c))
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda _pos, r=r, c=c: self._right(r, c))
                row.append(btn)
                self._grid.addWidget(btn, r + 1, c + 1)
            self._cells.append(row)

        self._sync()

    def _left(self, r: int, c: int) -> None:
        self._state.toggle_fill(r, c)
        self._sync()

    def _right(self, r: int, c: int) -> None:
        self._state.toggle_x(r, c)
        self._sync()

    def _sync(self) -> None:
        for r in range(len(self._cells)):
            for c in range(len(self._cells[0])):
                v = self._state.marks[r][c]
                btn = self._cells[r][c]
                if v == 1:
                    btn.setText("")
                    btn.setStyleSheet("background: #111827; border: 1px solid rgba(0,0,0,0.2);")
                elif v == -1:
                    btn.setText("×")
                    btn.setStyleSheet("color: rgba(0,0,0,0.55); background: transparent;")
                else:
                    btn.setText("")
                    btn.setStyleSheet("")

    def _check(self) -> None:
        if self._state.is_solved():
            QMessageBox.information(self, "Nonogram", "Solved! Nice work.")
        else:
            QMessageBox.information(self, "Nonogram", "Not solved yet.")

