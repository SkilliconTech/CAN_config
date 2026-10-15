from PySide6.QtCore import Qt, QRectF, QByteArray

from PySide6.QtGui import (
    QPainter,
    QPainterPath,
    QColor,
    QPixmap,
    QIcon,
    QTransform
)
ICONS_B64 = {
    "new": (
        "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"
        "agP9U2yG1NsAAAAASUVORK5CYII="
    ),
    "open": (
        "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"
        "SUVORK5CYII="
    ),
    "save": (
        "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"
    ),
    "import": (
        "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"
    ),
    "export": (
        "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"
    ),
}

def tinted_icon(name: str, color: str) -> QIcon:
    """Load an embedded toolbar icon and paint it in the given color."""
    data = QByteArray.fromBase64(ICONS_B64[name].encode("ascii"))
    pm = QPixmap()
    pm.loadFromData(data, "PNG")

    tinted = QPixmap(pm.size())
    tinted.fill(Qt.transparent)

    p = QPainter(tinted)
    p.drawPixmap(0, 0, pm)
    p.setCompositionMode(QPainter.CompositionMode_SourceIn)
    p.fillRect(tinted.rect(), QColor(color))
    p.end()

    return QIcon(tinted)

def make_theme_icon(dark_mode: bool, color: str, size: int = 18) -> QIcon:

    # Draw at 4x resolution so the icon stays sharp, Qt scales it down.
    scale = 4
    px = size * scale

    pixmap = QPixmap(px, px)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    pen_color = QColor(color)

    if not dark_mode:
        # ----------------------------------------------------------
        # LIGHT THEME: crescent moon, auto-scaled to fill the icon
        # ----------------------------------------------------------
        big_rect = QRectF(0, 0, px, px)

        cut_rect = QRectF(
            px * 0.38,
            -px * 0.05,
            px * 0.85,
            px * 0.85
        )

        moon = QPainterPath()
        moon.addEllipse(big_rect)

        cutout = QPainterPath()
        cutout.addEllipse(cut_rect)

        crescent = moon.subtracted(cutout)

        # Scale and center the crescent so it fills the icon
        bounds = crescent.boundingRect()
        fill = px * 0.94                      # 1.0 = touch the edges
        s = fill / max(bounds.width(), bounds.height())

        t = QTransform()
        t.translate(px / 2, px / 2)
        t.scale(s, s)
        t.translate(-bounds.center().x(), -bounds.center().y())

        crescent = t.map(crescent)

        painter.setPen(Qt.NoPen)
        painter.fillPath(crescent, pen_color)

    else:
        # ----------------------------------------------------------
        # DARK THEME: sun
        # ----------------------------------------------------------
        pen = painter.pen()
        pen.setColor(pen_color)
        pen.setWidthF(1.6 * scale)
        pen.setCapStyle(Qt.RoundCap)

        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        c = px / 2
        r = px * 0.22

        painter.drawEllipse(QRectF(c - r, c - r, r * 2, r * 2))

        ray = px * 0.16
        gap = 2 * scale

        for dx, dy in [
            (0, -1), (0, 1), (-1, 0), (1, 0),
            (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7), (-0.7, -0.7)
        ]:
            x1 = c + dx * (r + gap)
            y1 = c + dy * (r + gap)
            x2 = c + dx * (r + gap + ray)
            y2 = c + dy * (r + gap + ray)

            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    painter.end()

    return QIcon(pixmap)


