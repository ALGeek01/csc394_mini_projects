from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from paperplay.games.dotsboxes.model import DotsAndBoxesState


class DotsAndBoxesWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._state = DotsAndBoxesState.new(5, 5)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("Dots and Boxes")
        title.setStyleSheet("font-size: 20px; font-weight: 650;")
        root.addWidget(title)

        top = QHBoxLayout()
        top.addWidget(QLabel("Board:"))
        self._size = QComboBox()
        self._size.addItems(["4×4 dots", "5×5 dots", "6×6 dots"])
        self._size.setCurrentIndex(1)
        self._size.currentIndexChanged.connect(self.reset)
        top.addWidget(self._size)
        top.addStretch(1)
        self._btn_new = QPushButton("New game")
        self._btn_new.clicked.connect(self.reset)
        top.addWidget(self._btn_new)
        root.addLayout(top)

        self._status = QLabel("")
        self._status.setTextInteractionFlags(Qt.TextSelectableByMouse)
        root.addWidget(self._status)

        self._grid = QGridLayout()
        self._grid.setHorizontalSpacing(2)
        self._grid.setVerticalSpacing(2)
        root.addLayout(self._grid)

        root.addStretch(1)
        self._rebuild_board()
        self._sync()

    def reset(self) -> None:
        sizes = [(4, 4), (5, 5), (6, 6)]
        r, c = sizes[self._size.currentIndex()]
        self._state = DotsAndBoxesState.new(r, c)
        self._rebuild_board()
        self._sync()

    def _rebuild_board(self) -> None:
        # Clear grid
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)

        self._h_btns: list[list[QPushButton]] = []
        self._v_btns: list[list[QPushButton]] = []
        self._box_labels: list[list[QLabel]] = []

        dr, dc = self._state.dots_rows, self._state.dots_cols
        # Layout uses a (2*dr-1) x (2*dc-1) grid:
        # dots at even-even, h edges at even-odd, v edges at odd-even, boxes at odd-odd
        for rr in range(2 * dr - 1):
            for cc in range(2 * dc - 1):
                if rr % 2 == 0 and cc % 2 == 0:
                    dot = QLabel("•")
                    dot.setAlignment(Qt.AlignCenter)
                    dot.setFixedSize(14, 14)
                    self._grid.addWidget(dot, rr, cc, alignment=Qt.AlignCenter)
                elif rr % 2 == 0 and cc % 2 == 1:
                    # horizontal edge button maps to h[r][c]
                    r = rr // 2
                    c = cc // 2
                    btn = QPushButton("")
                    btn.setFixedSize(44, 14)
                    btn.setStyleSheet("border-radius: 6px;")
                    btn.clicked.connect(lambda _=False, r=r, c=c: self._play("h", r, c))
                    while len(self._h_btns) <= r:
                        self._h_btns.append([])
                    self._h_btns[r].append(btn)
                    self._grid.addWidget(btn, rr, cc)
                elif rr % 2 == 1 and cc % 2 == 0:
                    # vertical edge button maps to v[r][c]
                    r = rr // 2
                    c = cc // 2
                    btn = QPushButton("")
                    btn.setFixedSize(14, 44)
                    btn.setStyleSheet("border-radius: 6px;")
                    btn.clicked.connect(lambda _=False, r=r, c=c: self._play("v", r, c))
                    while len(self._v_btns) <= r:
                        self._v_btns.append([])
                    self._v_btns[r].append(btn)
                    self._grid.addWidget(btn, rr, cc)
                else:
                    # box label maps to boxes[r][c]
                    r = rr // 2
                    c = cc // 2
                    lab = QLabel("")
                    lab.setAlignment(Qt.AlignCenter)
                    lab.setFixedSize(44, 44)
                    lab.setStyleSheet("border: 1px solid rgba(0,0,0,0.08); border-radius: 8px;")
                    while len(self._box_labels) <= r:
                        self._box_labels.append([])
                    self._box_labels[r].append(lab)
                    self._grid.addWidget(lab, rr, cc)

    def _play(self, kind: str, r: int, c: int) -> None:
        try:
            self._state.play_edge(kind, r, c)
        except ValueError:
            return
        self._sync()

    def _sync(self) -> None:
        s = self._state
        assert s.h is not None and s.v is not None and s.boxes is not None

        # Update edge buttons
        for r in range(s.dots_rows):
            for c in range(s.dots_cols - 1):
                btn = self._h_btns[r][c]
                owner = s.h[r][c]
                btn.setEnabled(owner == 0 and not s.is_over())
                btn.setStyleSheet(
                    "border-radius: 6px; background: "
                    + ("transparent" if owner == 0 else ("#2563eb" if owner == 1 else "#ef4444"))
                    + ";"
                )

        for r in range(s.dots_rows - 1):
            for c in range(s.dots_cols):
                btn = self._v_btns[r][c]
                owner = s.v[r][c]
                btn.setEnabled(owner == 0 and not s.is_over())
                btn.setStyleSheet(
                    "border-radius: 6px; background: "
                    + ("transparent" if owner == 0 else ("#2563eb" if owner == 1 else "#ef4444"))
                    + ";"
                )

        # Update boxes
        for r in range(s.dots_rows - 1):
            for c in range(s.dots_cols - 1):
                lab = self._box_labels[r][c]
                owner = s.boxes[r][c]
                if owner == 0:
                    lab.setText("")
                    lab.setStyleSheet("border: 1px solid rgba(0,0,0,0.08); border-radius: 8px;")
                else:
                    lab.setText("1" if owner == 1 else "2")
                    lab.setStyleSheet(
                        "border-radius: 8px; color: white; font-weight: 700; background: "
                        + ("#2563eb" if owner == 1 else "#ef4444")
                        + ";"
                    )

        if s.is_over():
            w = s.winner()
            if w is None:
                self._status.setText(f"Game over. Draw. Score 1:{s.score1}  2:{s.score2}")
            else:
                self._status.setText(f"Game over. Winner: Player {w}. Score 1:{s.score1}  2:{s.score2}")
        else:
            self._status.setText(f"Turn: Player {s.turn}. Score 1:{s.score1}  2:{s.score2}")

