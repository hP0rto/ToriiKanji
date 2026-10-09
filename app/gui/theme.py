"""
Centralized theme system for ToriiKanji.
All colors, fonts, sizes, and spacing constants are defined here.
Widgets should import from this module instead of hardcoding style values.
"""

from PyQt6.QtGui import QColor, QFont

# ─── Colors ──────────────────────────────────────────────────────────────────

PRIMARY = "#C24338"
PRIMARY_HOVER = "#D9564B"
PRIMARY_DARK = "#A03530"

BG_DARK = "#1E1E1E"        # Main window background
BG_CARD = "#2C2C2C"        # Card / panel background
BG_HOVER = "#3C3C3C"       # Hover state background
BG_INPUT = "#2C2C2C"       # Input field background
BG_BALLOON = "#2B2B2B"     # Kanji card / balloon background

SWITCH_DISABLED_BG = "#555555"
SWITCH_DISABLED_HANDLE = "#777777"

BORDER = "#333333"
BORDER_LIGHT = "#555555"

TEXT_NORMAL = "#FFFFFF"
TEXT_MUTED = "#AAAAAA"
TEXT_HEADER = "#FFFFFF"
TEXT_DISABLED = "#666666"

GRID_LINE = "#2A2A35"

LINK = "#2A82DA"
DANGER = "#FF4444"
SUCCESS = "#44BB44"


# ─── QColor Variants (for Qt Charts and QPainter) ────────────────────────────

Q_PRIMARY = QColor(PRIMARY)
Q_BG_DARK = QColor(BG_DARK)
Q_BG_CARD = QColor(BG_CARD)
Q_BORDER = QColor(BORDER)
Q_TEXT_NORMAL = QColor(TEXT_NORMAL)
Q_TEXT_MUTED = QColor(TEXT_MUTED)
Q_TEXT_HEADER = QColor(TEXT_HEADER)
Q_GRID_LINE = QColor(GRID_LINE)
Q_BG_HOVER = QColor(BG_HOVER)
Q_TEXT_ON_PRIMARY = QColor(TEXT_NORMAL)
Q_SWITCH_DISABLED_BG = QColor(SWITCH_DISABLED_BG)
Q_SWITCH_DISABLED_HANDLE = QColor(SWITCH_DISABLED_HANDLE)


# ─── Fonts ───────────────────────────────────────────────────────────────────

FONT_FAMILY = "Segoe UI"
FONT_SIZE_XS = 9
FONT_SIZE_SM = 11
FONT_SIZE_MD = 14
FONT_SIZE_LG = 16
FONT_SIZE_XL = 22
FONT_SIZE_XXL = 28


def font(size=FONT_SIZE_MD, bold=False):
    """Create a QFont with the standard family."""
    f = QFont(FONT_FAMILY, size)
    f.setBold(bold)
    return f


# ─── Spacing / Sizing ───────────────────────────────────────────────────────

RADIUS_SM = 6
RADIUS_MD = 8
RADIUS_LG = 12
RADIUS_XL = 15

PADDING_SM = "5px 10px"
PADDING_MD = "8px 16px"
PADDING_LG = "10px 20px"

SPACING_SM = 8
SPACING_MD = 12
SPACING_LG = 16


# ─── Stylesheet Generators ──────────────────────────────────────────────────

def card_style(object_name="baseCard"):
    """Standard dark card with rounded corners and subtle border."""
    return f"""
        QFrame#{object_name} {{
            background-color: {BG_CARD};
            border-radius: {RADIUS_LG}px;
            border: 1px solid {BORDER};
            padding: 10px;
        }}
    """


def button_primary_style():
    """Primary action button (e.g., Save, Confirm)."""
    return f"""
        QPushButton {{
            background-color: {PRIMARY};
            color: {TEXT_NORMAL};
            border: none;
            padding: {PADDING_MD};
            border-radius: {RADIUS_MD}px;
            font-size: {FONT_SIZE_MD}px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {PRIMARY_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {PRIMARY_DARK};
        }}
        QPushButton:disabled {{
            background-color: {BORDER};
            color: {TEXT_DISABLED};
        }}
    """


def button_secondary_style():
    """Secondary / ghost button."""
    return f"""
        QPushButton {{
            background-color: {BG_CARD};
            color: {TEXT_NORMAL};
            border: 1px solid {BORDER_LIGHT};
            padding: {PADDING_SM};
            border-radius: {RADIUS_MD}px;
            font-size: {FONT_SIZE_MD}px;
        }}
        QPushButton:hover {{
            background-color: {BG_HOVER};
        }}
        QPushButton:disabled {{
            color: {TEXT_DISABLED};
        }}
    """


def tab_button_style():
    """Tab bar button style (checkable)."""
    return f"""
        QPushButton {{
            border: none;
            background-color: transparent;
            color: {TEXT_NORMAL};
            padding: 10px;
            font-size: {FONT_SIZE_MD}px;
            border-radius: 10px;
        }}
        QPushButton:checked {{
            background-color: {PRIMARY};
            font-weight: bold;
        }}
        QPushButton:checked:hover {{
            background-color: {PRIMARY_HOVER};
        }}
        QPushButton:hover {{
            background-color: {BG_HOVER};
        }}
    """


def input_style():
    """Standard input / line edit style."""
    return f"""
        color: {TEXT_NORMAL};
        font-size: {FONT_SIZE_LG}px;
        border: 1px solid {BORDER_LIGHT};
        border-radius: {RADIUS_SM}px;
        padding: {PADDING_SM};
        background-color: {BG_INPUT};
    """


def label_style(size=FONT_SIZE_MD, color=TEXT_NORMAL, bold=False):
    """Inline label style string."""
    weight = "bold" if bold else "normal"
    return f"color: {color}; font-size: {size}px; font-weight: {weight};"


def scrollbar_style():
    """Minimal dark scrollbar style."""
    return f"""
        QScrollBar:vertical {{
            border: none;
            background: {BG_CARD};
            width: 8px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {BORDER};
            min-height: 20px;
            border-radius: 4px;
        }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 0;
        }}
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {{
            background: none;
        }}
    """


def text_edit_style(font_size=24):
    """Text display area style."""
    return f"""
        QTextEdit {{
            font-size: {font_size}px;
            border-radius: {RADIUS_XL}px;
            background-color: {BG_CARD};
            color: {TEXT_NORMAL};
            border: 1px solid {BORDER_LIGHT};
            padding: 8px;
            text-align: center;
        }}
    """
