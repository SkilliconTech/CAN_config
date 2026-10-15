from PySide6.QtCore import Qt, QRectF

from PySide6.QtGui import (
    QPainter,
    QPainterPath,
    QLinearGradient,
    QColor
)

from PySide6.QtWidgets import QWidget

from resources.theme import (
    LOGO_GOLD_1,
    LOGO_GOLD_2
)

class LogoWidget(QWidget):
    def __init__(self, size: int = 26, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        gradient = QLinearGradient(0, 0, w, h)
        gradient.setColorAt(0.0, QColor(LOGO_GOLD_1))
        gradient.setColorAt(1.0, QColor(LOGO_GOLD_2))

        pad = w * 0.09
        path = QPainterPath()
        path.moveTo(w / 2, pad)
        path.lineTo(w - pad, h / 2)
        path.lineTo(w / 2, h - pad)
        path.lineTo(pad, h / 2)
        path.closeSubpath()

        pen = painter.pen()
        pen.setWidthF(w * 0.09)
        pen.setBrush(gradient)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        r = w * 0.14
        painter.drawEllipse(
            QRectF(
                w / 2 - r,
                h / 2 - r,
                r * 2,
                r * 2
            )
        )

        painter.end()



