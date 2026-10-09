from pathlib import Path

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton

from gui.theme import BG_CARD, BG_HOVER, BORDER_LIGHT, PADDING_MD, RADIUS_MD, TEXT_NORMAL


def create_icon_button(icon_path: Path, tooltip: str = "", on_click=None, size=48) -> QPushButton:
    button = QPushButton('')
    button.setIcon(QIcon(str(icon_path)))
    button.setToolTip(tooltip)
    button.setFixedSize(size, size)
    button.setIconSize(QSize(size, size))
    button.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            border: none;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
    """)
    if on_click:
        button.clicked.connect(on_click)
    return button


def create_text_button(text: str, on_click=None, style_sheet=None) -> QPushButton:
    button = QPushButton(text)
    if style_sheet is None:
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_CARD};
                color: {TEXT_NORMAL};
                border: 1px solid {BORDER_LIGHT};
                padding: {PADDING_MD};
                border-radius: {RADIUS_MD}px;
            }}
            QPushButton:hover {{
                background-color: {BG_HOVER};
            }}
        """)
    else:
        button.setStyleSheet(style_sheet)    
    
    if on_click:
        button.clicked.connect(on_click)
    return button
