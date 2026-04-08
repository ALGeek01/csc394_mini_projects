from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from paperplay.games.crossword.model import CrosswordPlayState, compute_numbers, extract_entries, make_sample_puzzle, validate_puzzle
from paperplay.persistence.crossword_io import load_puzzle, save_puzzle
from paperplay.persistence.crossword_schema import CrosswordPuzzle, new_empty_puzzle


class CrosswordWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._puzzle: CrosswordPuzzle = make_sample_puzzle()
        self._play = CrosswordPlayState.from_puzzle(self._puzzle)
        self._mode: str = "play"  # play | edit
        self._path: Path | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("Crossword")
        title.setStyleSheet("font-size: 20px; font-weight: 650;")
        root.addWidget(title)

        top = QHBoxLayout()
        self._btn_play = QPushButton("Play")
        self._btn_play.clicked.connect(lambda: self._set_mode("play"))
        self._btn_edit = QPushButton("Edit")
        self._btn_edit.clicked.connect(lambda: self._set_mode("edit"))
        top.addWidget(self._btn_play)
        top.addWidget(self._btn_edit)
        top.addSpacing(12)

        self._btn_new = QPushButton("New")
        self._btn_new.clicked.connect(self._new_puzzle)
        top.addWidget(self._btn_new)

        self._btn_load = QPushButton("Load…")
        self._btn_load.clicked.connect(self._load)
        top.addWidget(self._btn_load)

        self._btn_save = QPushButton("Save…")
        self._btn_save.clicked.connect(self._save_as)
        top.addWidget(self._btn_save)

        top.addStretch(1)
        self._btn_check = QPushButton("Check solved")
        self._btn_check.clicked.connect(self._check_solved)
        top.addWidget(self._btn_check)
        root.addLayout(top)

        self._status = QLabel("")
        self._status.setWordWrap(True)
        root.addWidget(self._status)

        body = QHBoxLayout()
        root.addLayout(body, 1)

        self._grid_wrap = QWidget()
        self._grid = QGridLayout(self._grid_wrap)
        self._grid.setSpacing(2)
        body.addWidget(self._grid_wrap, 1)

        self._tabs = QTabWidget()
        self._across = QTableWidget(0, 2)
        self._across.setHorizontalHeaderLabels(["#", "Clue (Across)"])
        self._across.horizontalHeader().setStretchLastSection(True)
        self._down = QTableWidget(0, 2)
        self._down.setHorizontalHeaderLabels(["#", "Clue (Down)"])
        self._down.horizontalHeader().setStretchLastSection(True)
        self._tabs.addTab(self._across, "Across")
        self._tabs.addTab(self._down, "Down")
        self._tabs.setMinimumWidth(360)
        body.addWidget(self._tabs)

        edit_bar = QHBoxLayout()
        root.addLayout(edit_bar)
        edit_bar.addWidget(QLabel("W:"))
        self._w = QSpinBox()
        self._w.setRange(3, 21)
        self._w.setValue(self._puzzle.width)
        edit_bar.addWidget(self._w)
        edit_bar.addWidget(QLabel("H:"))
        self._h = QSpinBox()
        self._h.setRange(3, 21)
        self._h.setValue(self._puzzle.height)
        edit_bar.addWidget(self._h)
        self._btn_resize = QPushButton("Resize")
        self._btn_resize.clicked.connect(self._resize_puzzle)
        edit_bar.addWidget(self._btn_resize)
        edit_bar.addStretch(1)

        self._cells: list[list[QLineEdit]] = []
        self._set_mode("play")
        self._rebuild()

    def reset(self) -> None:
        self._play = CrosswordPlayState.from_puzzle(self._puzzle)
        self._rebuild()

    def _set_mode(self, mode: str) -> None:
        self._mode = mode
        self._btn_play.setEnabled(mode != "play")
        self._btn_edit.setEnabled(mode != "edit")
        self._btn_resize.setEnabled(mode == "edit")
        self._w.setEnabled(mode == "edit")
        self._h.setEnabled(mode == "edit")
        self._across.setEditTriggers(self._across.AllEditTriggers if mode == "edit" else self._across.NoEditTriggers)
        self._down.setEditTriggers(self._down.AllEditTriggers if mode == "edit" else self._down.NoEditTriggers)
        self._status.setText(
            "Play mode: type letters into cells."
            if mode == "play"
            else "Edit mode: right-click cells to toggle blocks; type solution letters; edit clues."
        )
        self._rebuild()

    def _new_puzzle(self) -> None:
        self._path = None
        self._puzzle = new_empty_puzzle(9, 9, title="Untitled", author="PaperPlay")
        self._play = CrosswordPlayState.from_puzzle(self._puzzle)
        self._w.setValue(self._puzzle.width)
        self._h.setValue(self._puzzle.height)
        self._rebuild()

    def _resize_puzzle(self) -> None:
        if self._mode != "edit":
            return
        w = int(self._w.value())
        h = int(self._h.value())
        self._puzzle = new_empty_puzzle(w, h, title=self._puzzle.title, author=self._puzzle.author)
        self._play = CrosswordPlayState.from_puzzle(self._puzzle)
        self._rebuild()

    def _load(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load crossword", "", "Crossword JSON (*.json)")
        if not path:
            return
        try:
            p = load_puzzle(path)
            errs = validate_puzzle(p)
            if errs:
                raise ValueError("; ".join(errs))
        except Exception as e:
            QMessageBox.warning(self, "Load failed", str(e))
            return
        self._path = Path(path)
        self._puzzle = p
        self._play = CrosswordPlayState.from_puzzle(self._puzzle)
        self._w.setValue(self._puzzle.width)
        self._h.setValue(self._puzzle.height)
        self._rebuild()

    def _save_as(self) -> None:
        if self._mode != "edit":
            QMessageBox.information(self, "Crossword", "Switch to Edit mode to save puzzles.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save crossword", "", "Crossword JSON (*.json)")
        if not path:
            return
        self._pull_clues_from_tables()
        errs = validate_puzzle(self._puzzle)
        if errs:
            QMessageBox.warning(self, "Cannot save", "\n".join(errs))
            return
        try:
            save_puzzle(path, self._puzzle)
        except Exception as e:
            QMessageBox.warning(self, "Save failed", str(e))
            return
        self._path = Path(path)
        QMessageBox.information(self, "Saved", f"Saved to:\n{path}")

    def _check_solved(self) -> None:
        if self._mode != "play":
            return
        if self._play.is_solved():
            QMessageBox.information(self, "Crossword", "Solved! Nice work.")
        else:
            QMessageBox.information(self, "Crossword", "Not solved yet.")

    def _rebuild(self) -> None:
        # Clear grid
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)

        self._cells = []
        nums = compute_numbers(self._puzzle.blocks)

        for r in range(self._puzzle.height):
            row: list[QLineEdit] = []
            for c in range(self._puzzle.width):
                e = QLineEdit("")
                e.setFixedSize(34, 34)
                e.setMaxLength(1)
                e.setAlignment(Qt.AlignCenter)
                e.setContextMenuPolicy(Qt.CustomContextMenu)
                e.customContextMenuRequested.connect(lambda _pos, r=r, c=c: self._toggle_block(r, c))
                e.textChanged.connect(lambda _txt, r=r, c=c: self._on_cell_changed(r, c))
                row.append(e)
                self._grid.addWidget(e, r, c)
            self._cells.append(row)

        self._push_clues_to_tables()
        self._sync_cells(nums)

    def _toggle_block(self, r: int, c: int) -> None:
        if self._mode != "edit":
            return
        blocks = [row.copy() for row in self._puzzle.blocks]
        blocks[r][c] = not blocks[r][c]
        sol = [row.copy() for row in self._puzzle.solution]
        if blocks[r][c]:
            sol[r][c] = ""
        self._puzzle = CrosswordPuzzle(**{**self._puzzle.__dict__, "blocks": blocks, "solution": sol})
        self._rebuild()

    def _on_cell_changed(self, r: int, c: int) -> None:
        if self._puzzle.blocks[r][c]:
            return
        e = self._cells[r][c]
        txt = e.text().strip()
        if self._mode == "play":
            self._play.set_fill(r, c, txt)
        else:
            # edit: sets solution letter
            letter = txt.upper()[:1] if txt else ""
            sol = [row.copy() for row in self._puzzle.solution]
            sol[r][c] = letter if letter.isalpha() else ""
            self._puzzle = CrosswordPuzzle(**{**self._puzzle.__dict__, "solution": sol})

    def _sync_cells(self, nums: list[list[int]]) -> None:
        for r in range(self._puzzle.height):
            for c in range(self._puzzle.width):
                e = self._cells[r][c]
                if self._puzzle.blocks[r][c]:
                    e.blockSignals(True)
                    e.setText("")
                    e.setReadOnly(True)
                    e.setStyleSheet("background: #111827; border: 1px solid rgba(0,0,0,0.25);")
                    e.blockSignals(False)
                    continue

                val = self._play.fill[r][c] if self._mode == "play" else self._puzzle.solution[r][c]
                e.blockSignals(True)
                e.setText(val)
                e.setReadOnly(False)
                num = nums[r][c]
                # simple number indicator via placeholder; keeps UI light
                e.setPlaceholderText(str(num) if num else "")
                e.setStyleSheet("font-weight: 700;" if self._mode == "edit" else "")
                e.blockSignals(False)

    def _push_clues_to_tables(self) -> None:
        across_entries, down_entries = extract_entries(self._puzzle.blocks)
        across_nums = sorted(across_entries.keys())
        down_nums = sorted(down_entries.keys())

        def fill_table(table: QTableWidget, nums: list[int], clues: dict[int, str]) -> None:
            table.blockSignals(True)
            table.setRowCount(len(nums))
            for i, n in enumerate(nums):
                itemn = QTableWidgetItem(str(n))
                itemn.setFlags(itemn.flags() & ~Qt.ItemIsEditable)
                table.setItem(i, 0, itemn)
                clue = QTableWidgetItem(clues.get(n, ""))
                table.setItem(i, 1, clue)
            table.blockSignals(False)

        fill_table(self._across, across_nums, self._puzzle.cluesAcross)
        fill_table(self._down, down_nums, self._puzzle.cluesDown)

    def _pull_clues_from_tables(self) -> None:
        def read_table(table: QTableWidget) -> dict[int, str]:
            out: dict[int, str] = {}
            for r in range(table.rowCount()):
                n_item = table.item(r, 0)
                c_item = table.item(r, 1)
                if n_item is None:
                    continue
                n = int(n_item.text())
                clue = c_item.text().strip() if c_item else ""
                if clue:
                    out[n] = clue
            return out

        self._puzzle = CrosswordPuzzle(
            **{
                **self._puzzle.__dict__,
                "cluesAcross": read_table(self._across),
                "cluesDown": read_table(self._down),
            }
        )

