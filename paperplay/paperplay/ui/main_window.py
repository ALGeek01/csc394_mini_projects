from __future__ import annotations

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDockWidget,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from paperplay.games import GameInfo, get_game_catalog
from paperplay.ui.theme import DARK, LIGHT, apply_theme


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PaperPlay")
        self.resize(1100, 720)

        self._games = get_game_catalog()
        self._active_game_id: str | None = None

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._game_widgets: dict[str, QWidget] = {}

        self._build_toolbar()
        self._build_library_dock()
        self._build_context_dock()

        self._set_welcome()

    def _build_toolbar(self) -> None:
        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(tb)

        self._btn_reset = QPushButton("Reset")
        self._btn_reset.clicked.connect(self._reset_active_game)
        self._btn_reset.setEnabled(False)
        tb.addWidget(self._btn_reset)

        tb.addSeparator()

        self._theme_toggle = QCheckBox("Dark mode")
        self._theme_toggle.stateChanged.connect(self._toggle_theme)
        tb.addWidget(self._theme_toggle)

        tb.addSeparator()

        about = QPushButton("About")
        about.clicked.connect(self._show_about)
        tb.addWidget(about)

        # Start in light theme.
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, LIGHT)

    def _build_library_dock(self) -> None:
        dock = QDockWidget("Games", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetMovable)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search games…")
        self._search.textChanged.connect(self._refresh_game_list)
        layout.addWidget(self._search)

        self._game_list = QListWidget()
        self._game_list.itemActivated.connect(self._on_game_activated)
        self._game_list.itemClicked.connect(self._on_game_clicked)
        layout.addWidget(self._game_list, 1)

        dock.setWidget(root)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        self._refresh_game_list()

    def _build_context_dock(self) -> None:
        dock = QDockWidget("Details", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetMovable)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self._title = QLabel("PaperPlay")
        self._title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(self._title)

        self._desc = QLabel("Pick a game from the library to start playing.")
        self._desc.setWordWrap(True)
        layout.addWidget(self._desc)

        layout.addStretch(1)

        dock.setWidget(root)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def _set_welcome(self) -> None:
        welcome = QWidget()
        v = QVBoxLayout(welcome)
        v.setContentsMargins(30, 30, 30, 30)
        v.setSpacing(14)

        title = QLabel("PaperPlay")
        title.setStyleSheet("font-size: 28px; font-weight: 700;")
        subtitle = QLabel("A pen-and-paper game suite.")
        subtitle.setStyleSheet("font-size: 14px;")
        v.addWidget(title)
        v.addWidget(subtitle)
        v.addSpacing(12)

        hint = QLabel("Use the left panel to choose a game. Most games support 2P local play.")
        hint.setWordWrap(True)
        v.addWidget(hint)
        v.addStretch(1)

        self._stack.addWidget(welcome)
        self._stack.setCurrentWidget(welcome)

    def _refresh_game_list(self) -> None:
        q = self._search.text().strip().lower()
        self._game_list.clear()
        for g in self._games:
            if q and (q not in g.title.lower()) and (q not in g.category.lower()):
                continue
            item = QListWidgetItem(f"{g.title}  ·  {g.category}")
            item.setData(Qt.UserRole, g.game_id)
            self._game_list.addItem(item)

    def _get_game_by_id(self, game_id: str) -> GameInfo:
        for g in self._games:
            if g.game_id == game_id:
                return g
        raise KeyError(game_id)

    def _on_game_clicked(self, item: QListWidgetItem) -> None:
        game_id = item.data(Qt.UserRole)
        if not isinstance(game_id, str):
            return
        g = self._get_game_by_id(game_id)
        self._title.setText(g.title)
        self._desc.setText(g.description)

    def _on_game_activated(self, item: QListWidgetItem) -> None:
        game_id = item.data(Qt.UserRole)
        if not isinstance(game_id, str):
            return
        self.open_game(game_id)

    def open_game(self, game_id: str) -> None:
        if game_id not in self._game_widgets:
            g = self._get_game_by_id(game_id)
            widget = g.create_widget()
            self._game_widgets[game_id] = widget
            self._stack.addWidget(widget)

        self._stack.setCurrentWidget(self._game_widgets[game_id])
        self._active_game_id = game_id
        self._btn_reset.setEnabled(True)

    def _reset_active_game(self) -> None:
        if not self._active_game_id:
            return
        w = self._game_widgets.get(self._active_game_id)
        if w is None:
            return
        reset = getattr(w, "reset", None)
        if callable(reset):
            reset()

    def _toggle_theme(self) -> None:
        app = QApplication.instance()
        if app is None:
            return
        apply_theme(app, DARK if self._theme_toggle.isChecked() else LIGHT)

    def _show_about(self) -> None:
        QMessageBox.information(
            self,
            "About PaperPlay",
            "PaperPlay is a desktop suite of classic pen-and-paper style games.\n\n"
            "Built with Python + Qt (PySide6).",
        )

