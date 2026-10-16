from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor
from PySide6.QtWidgets import QRadioButton

from resources.theme import LIGHT


class CheckRadioButton(QRadioButton):
    """
    A radio button that is drawn like a check box:

        selected   -> rounded blue square with a white check mark
        unselected -> rounded empty square with a thin border

    It still behaves like a radio button: Enable / Disable placed in the
    same group box exclude each other.
    """

    BOX = 20      # size of the square, in pixels
    GAP = 10      # space between the square and the text
    RADIUS = 5    # corner roundness of the square

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self._colors = LIGHT

        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)

    def set_colors(self, colors):
        """Give the button the current theme colors (LIGHT or DARK)."""
        self._colors = colors
        self.update()

    # ------------------------------------------------------------------
    # Size / click area
    # ------------------------------------------------------------------
    def sizeHint(self):
        metrics = self.fontMetrics()

        width = self.BOX + self.GAP + metrics.horizontalAdvance(self.text()) + 4
        height = max(self.BOX + 6, metrics.height() + 6)

        return QSize(width, height)

    def minimumSizeHint(self):
        return self.sizeHint()

    def hitButton(self, pos):
        # The whole row (square + text) can be clicked
        return self.rect().contains(pos)

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        c = self._colors

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.isEnabled():
            painter.setOpacity(0.5)

        checked = self.isChecked()
        hovered = self.underMouse()

        top = (self.height() - self.BOX) / 2

        # 1 px inside the edge, so the 2 px border is not cut off
        box = QRectF(1, top + 1, self.BOX - 2, self.BOX - 2)

        accent = QColor(c["accent_blue"])

        if checked:
            fill = accent.darker(110) if hovered else accent
            border = fill
        else:
            fill = QColor(c["bg_main"])
            border = accent if hovered else QColor(c["text_secondary"])

        pen = QPen(border)
        pen.setWidthF(2)
        painter.setPen(pen)
        painter.setBrush(fill)
        painter.drawRoundedRect(box, self.RADIUS, self.RADIUS)

        # White check mark
        if checked:
            x, y, size = box.left(), box.top(), box.width()

            check = QPainterPath()
            check.moveTo(x + size * 0.24, y + size * 0.52)
            check.lineTo(x + size * 0.43, y + size * 0.71)
            check.lineTo(x + size * 0.77, y + size * 0.31)

            check_pen = QPen(QColor("#FFFFFF"))
            check_pen.setWidthF(2.2)
            check_pen.setCapStyle(Qt.RoundCap)
            check_pen.setJoinStyle(Qt.RoundJoin)

            painter.setPen(check_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(check)

        # Text
        painter.setPen(QColor(
            c["text_primary"] if self.isEnabled() else c["text_secondary"]
        ))
        painter.setFont(self.font())

        text_rect = QRectF(
            self.BOX + self.GAP,
            0,
            max(10, self.width() - self.BOX - self.GAP),
            self.height(),
        )
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.text())

        painter.end()