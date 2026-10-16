from PySide6.QtCore import Qt, QRectF, QSize
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor
from PySide6.QtWidgets import QRadioButton, QCheckBox

from resources.theme import LIGHT


BOX = 20      # size of the square, in pixels
GAP = 10      # space between the square and the text
RADIUS = 5    # corner roundness of the square


def _size_hint(widget):
    metrics = widget.fontMetrics()

    width = BOX + GAP + metrics.horizontalAdvance(widget.text()) + 4
    height = max(BOX + 6, metrics.height() + 6)

    return QSize(width, height)


def _paint(widget, c):
    """
    Draw a rounded square (blue with a white check mark when selected)
    followed by the text of the widget. 'c' is the theme color dictionary.
    """
    painter = QPainter(widget)
    painter.setRenderHint(QPainter.Antialiasing)

    if not widget.isEnabled():
        painter.setOpacity(0.5)

    checked = widget.isChecked()
    hovered = widget.underMouse()

    top = (widget.height() - BOX) / 2

    # 1 px inside the edge, so the 2 px border is not cut off
    box = QRectF(1, top + 1, BOX - 2, BOX - 2)

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
    painter.drawRoundedRect(box, RADIUS, RADIUS)

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
        c["text_primary"] if widget.isEnabled() else c["text_secondary"]
    ))
    painter.setFont(widget.font())

    text_rect = QRectF(
        BOX + GAP,
        0,
        max(10, widget.width() - BOX - GAP),
        widget.height(),
    )
    painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, widget.text())

    painter.end()


class CheckRadioButton(QRadioButton):
    """
    A radio button drawn like a check box:

        selected   -> rounded blue square with a white check mark
        unselected -> rounded empty square with a thin border

    It still behaves like a radio button: Enable / Disable placed in the
    same group box exclude each other.
    """

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self._colors = LIGHT

        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)

    def set_colors(self, colors):
        """Give the button the current theme colors (LIGHT or DARK)."""
        self._colors = colors
        self.update()

    def sizeHint(self):
        return _size_hint(self)

    def minimumSizeHint(self):
        return self.sizeHint()

    def hitButton(self, pos):
        # The whole row (square + text) can be clicked
        return self.rect().contains(pos)

    def paintEvent(self, event):
        _paint(self, self._colors)


class CheckStyleCheckBox(QCheckBox):
    """
    A normal check box (it can be ticked and unticked independently),
    drawn in the same style as CheckRadioButton.
    """

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self._colors = LIGHT

        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)

    def set_colors(self, colors):
        """Give the check box the current theme colors (LIGHT or DARK)."""
        self._colors = colors
        self.update()

    def sizeHint(self):
        return _size_hint(self)

    def minimumSizeHint(self):
        return self.sizeHint()

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def paintEvent(self, event):
        _paint(self, self._colors)