from pathlib import Path
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize


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


def create_text_button(text: str, on_click=None) -> QPushButton:
    button = QPushButton(text)
    button.setStyleSheet("""
        QPushButton {
            background-color: #2c2c2c;
            color: white;
            border: 1px solid #555;
            padding: 8px 16px;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #3c3c3c;
        }
    """)
    if on_click:
        button.clicked.connect(on_click)
    return button