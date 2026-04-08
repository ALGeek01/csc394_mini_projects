from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class Theme:
    name: str
    base: QColor
    window: QColor
    text: QColor
    button: QColor
    highlight: QColor
    highlighted_text: QColor


LIGHT = Theme(
    name="Light",
    base=QColor("#ffffff"),
    window=QColor("#f6f7fb"),
    text=QColor("#0f172a"),
    button=QColor("#ffffff"),
    highlight=QColor("#2563eb"),
    highlighted_text=QColor("#ffffff"),
)

DARK = Theme(
    name="Dark",
    base=QColor("#0b1220"),
    window=QColor("#0b1220"),
    text=QColor("#e5e7eb"),
    button=QColor("#111a2e"),
    highlight=QColor("#60a5fa"),
    highlighted_text=QColor("#0b1220"),
)


def apply_theme(app: QApplication, theme: Theme) -> None:
    pal = QPalette()
    pal.setColor(QPalette.Window, theme.window)
    pal.setColor(QPalette.Base, theme.base)
    pal.setColor(QPalette.AlternateBase, theme.button)
    pal.setColor(QPalette.Button, theme.button)
    pal.setColor(QPalette.WindowText, theme.text)
    pal.setColor(QPalette.Text, theme.text)
    pal.setColor(QPalette.ButtonText, theme.text)
    pal.setColor(QPalette.Highlight, theme.highlight)
    pal.setColor(QPalette.HighlightedText, theme.highlighted_text)
    app.setPalette(pal)

