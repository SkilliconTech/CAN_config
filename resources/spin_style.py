import os
import tempfile

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap

from resources.theme import RADIUS_SM


_ARROW_DIR = os.path.join(tempfile.gettempdir(), "can_config_arrows")


def _arrow_file(direction, color):
    """
    Draw a small chevron once and keep it as a PNG in the temp folder.
    Qt style sheets can only show arrows from image files.
    """
    path = os.path.join(_ARROW_DIR, f"{direction}_{color.lstrip('#')}.png")

    try:
        if not os.path.exists(path):
            os.makedirs(_ARROW_DIR, exist_ok=True)

            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            pen = QPen(QColor(color))
            pen.setWidthF(2.8)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)

            if direction == "up":
                points = [QPointF(6, 15), QPointF(12, 9), QPointF(18, 15)]
            else:
                points = [QPointF(6, 9), QPointF(12, 15), QPointF(18, 9)]

            painter.drawPolyline(points)
            painter.end()

            pixmap.save(path, "PNG")
    except OSError:
        pass        # without the image the buttons still work, only the arrow is missing

    return path.replace("\\", "/")


def spinbox_stylesheet(c):
    """Style sheet for QSpinBox with working, clearly visible up/down buttons."""
    up = _arrow_file("up", c["text_primary"])
    down = _arrow_file("down", c["text_primary"])
    up_off = _arrow_file("up", c["text_secondary"])
    down_off = _arrow_file("down", c["text_secondary"])

    return f"""
        QSpinBox {{
            background-color: {c['bg_main']};
            color: {c['text_primary']};
            border: 1px solid {c['border']};
            border-radius: {RADIUS_SM}px;
            padding: 4px 30px 4px 8px;
        }}
        QSpinBox:disabled {{
            color: {c['text_secondary']};
        }}

        QSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 24px;
            border-left: 1px solid {c['border']};
            border-top-right-radius: {RADIUS_SM}px;
            background-color: transparent;
        }}
        QSpinBox::down-button {{
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 24px;
            border-left: 1px solid {c['border']};
            border-bottom-right-radius: {RADIUS_SM}px;
            background-color: transparent;
        }}
        QSpinBox::up-button:hover, QSpinBox::down-button:hover,
        QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {{
            background-color: {c['border']};
        }}

        QSpinBox::up-arrow {{
            image: url("{up}");
            width: 12px;
            height: 12px;
        }}
        QSpinBox::down-arrow {{
            image: url("{down}");
            width: 12px;
            height: 12px;
        }}
        QSpinBox::up-arrow:disabled, QSpinBox::up-arrow:off {{
            image: url("{up_off}");
        }}
        QSpinBox::down-arrow:disabled, QSpinBox::down-arrow:off {{
            image: url("{down_off}");
        }}
    """