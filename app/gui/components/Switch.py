from PyQt6.QtCore import (
    QObject, QSize, QPointF, QPropertyAnimation, QEasingCurve,
    pyqtProperty, pyqtSlot, Qt, 
)
from PyQt6.QtGui import QPainter, QPalette, QLinearGradient, QGradient, QColor
from PyQt6.QtWidgets import QAbstractButton


class SwitchPrivate(QObject):
    def __init__(self, q, parent=None):
        super().__init__(parent=parent)
        self.mPointer = q
        self.mPosition = 0.0
        self.mGradient = QLinearGradient()
        self.mGradient.setSpread(QGradient.Spread.PadSpread)

        self.animation = QPropertyAnimation(self)
        self.animation.setTargetObject(self)
        self.animation.setPropertyName(b'position')
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutExpo)

        self.animation.finished.connect(self.mPointer.update)

    @pyqtProperty(float)
    def position(self):
        return self.mPosition

    @position.setter
    def position(self, value):
        self.mPosition = value
        self.mPointer.update()

    def draw(self, painter: QPainter):
        r = self.mPointer.rect()
        margin = r.height() // 10

        painter.setPen(Qt.PenStyle.NoPen)
    
        if not self.mPointer.isEnabled():
        # Estado desabilitado → cinza
            bg_color = QColor("#555555")   # fundo cinza escuro
            handle_color = QColor("#777777")  # bolinha cinza claro
        else:
            # Estado normal
            bg_color = QColor("#3C3C3C")   # secundária (fundo apagado)
            active_color = QColor("#C24338")  # primária (ativo)
            current_color = bg_color if not self.mPointer.isChecked() else active_color

            handle_color = QColor("#FFFFFF")  # bolinha branca
            bg_color = current_color


        painter.setBrush(bg_color)
        painter.drawRoundedRect(r, r.height() / 2, r.height() / 2)
        
        painter.setBrush(handle_color)
        x = r.height() / 2.0 + self.mPosition * (r.width() - r.height())
        painter.drawEllipse(QPointF(x, r.height() / 2),
                            r.height() / 2 - margin,
                            r.height() / 2 - margin)

    @pyqtSlot(bool, name='animate')
    def animate(self, checked: bool):
        direction = (
            QPropertyAnimation.Direction.Forward
            if checked else QPropertyAnimation.Direction.Backward
        )
        self.animation.setDirection(direction)
        self.animation.start()


class Switch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.dPtr = SwitchPrivate(self)
        self.setCheckable(True)
        self.clicked.connect(self.dPtr.animate)
    
    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self.dPtr.mPosition = 1.0 if checked else 0.0
        self.update()

    def sizeHint(self):
        return QSize(64, 32)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.dPtr.draw(painter)

    def resizeEvent(self, event):
        self.update()
