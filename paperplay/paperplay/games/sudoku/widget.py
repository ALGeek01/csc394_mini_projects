from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from paperplay.games.sudoku.model import SudokuState, is_solved
from paperplay.games.sudoku.puzzles import PUZZLES


class SudokuWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._state = SudokuState.from_puzzle(PUZZLES[0])

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("Sudoku")
        title.setStyleSheet("font-size: 20px; font-weight: 650;")
        root.addWidget(title)

        top = QHBoxLayout()
        top.addWidget(QLabel("Puzzle:"))
        self._puzzle = QComboBox()
        self._puzzle.addItems([f"Puzzle {i+1}" for i in range(len(PUZZLES))])
        self._puzzle.currentIndexChanged.connect(self.reset)
        top.addWidget(self._puzzle)
        top.addStretch(1)
        self._btn_new = QPushButton("Reset puzzle")
        self._btn_new.clicked.connect(self.reset)
        top.addWidget(self._btn_new)
        root.addLayout(top)

        self._status = QLabel("")
        self._status.setTextInteractionFlags(Qt.TextSelectableByMouse)
        root.addWidget(self._status)

        self._grid = QGridLayout()
        self._grid.setSpacing(2)
        root.addLayout(self._grid)

        self._cells: list[list[QLineEdit]] = []
        v = QIntValidator(1, 9)
        for r in range(9):
            row: list[QLineEdit] = []
            for c in range(9):
                e = QLineEdit("")
                e.setFixedSize(40, 40)
                e.setAlignment(Qt.AlignCenter)
                e.setMaxLength(1)
                e.setValidator(v)
                e.textChanged.connect(lambda _txt, r=r, c=c: self._on_change(r, c))
                if (r // 3 + c // 3) % 2 == 0:
                    e.setStyleSheet("background: rgba(0,0,0,0.03);")
                row.append(e)
                self._grid.addWidget(e, r, c)
            self._cells.append(row)

        btns = QHBoxLayout()
        self._btn_check = QPushButton("Check solved")
        self._btn_check.clicked.connect(self._check_solved)
        btns.addWidget(self._btn_check)
        btns.addStretch(1)
        root.addLayout(btns)

        root.addStretch(1)
        self._sync()

    def reset(self) -> None:
        self._state = SudokuState.from_puzzle(PUZZLES[self._puzzle.currentIndex()])
        self._sync()

    def _sync(self) -> None:
        for r in range(9):
            for c in range(9):
                val = self._state.grid[r][c]
                e = self._cells[r][c]
                blocked = self._state.given[r][c] != 0
                e.blockSignals(True)
                e.setText("" if val == 0 else str(val))
                e.setReadOnly(blocked)
                if blocked:
                    e.setStyleSheet("font-weight: 700; background: rgba(0,0,0,0.08);")
                else:
                    if (r // 3 + c // 3) % 2 == 0:
                        e.setStyleSheet("background: rgba(0,0,0,0.03);")
                    else:
                        e.setStyleSheet("")
                e.blockSignals(False)
        self._status.setText("Enter digits 1–9. Invalid moves are rejected.")

    def _on_change(self, r: int, c: int) -> None:
        e = self._cells[r][c]
        txt = e.text().strip()
        val = int(txt) if txt else 0
        try:
            self._state.set_cell(r, c, val)
        except ValueError:
            # revert visual
            e.blockSignals(True)
            e.setText("" if self._state.grid[r][c] == 0 else str(self._state.grid[r][c]))
            e.blockSignals(False)

    def _check_solved(self) -> None:
        if is_solved(self._state.grid):
            QMessageBox.information(self, "Sudoku", "Solved! Nice work.")
        else:
            QMessageBox.information(self, "Sudoku", "Not solved yet.")

