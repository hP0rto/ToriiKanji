from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtGui import QKeySequence
from PyQt6.QtCore import Qt

class HotkeyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._sequence = None

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key.Key_unknown:
            return
        
        sequence = []

        if modifiers & Qt.KeyboardModifier.ControlModifier:
            sequence.append("Ctrl")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            sequence.append("Shift")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            sequence.append("Alt")
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            sequence.append("Meta")

        key_text = event.text().upper()
        if not key_text and key >= Qt.Key.Key_F1 and key <= Qt.Key.Key_F35:
            key_text = f"F{key - Qt.Key.Key_F1 + 1}"

        if key_text:
            sequence.append(key_text)

        self.setText("+".join(sequence))
