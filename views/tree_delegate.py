
from PySide6.QtCore import Qt, QSize, QRectF, QPointF, QByteArray
from PySide6.QtGui import (
    QPainter, QPainterPath, QLinearGradient, QColor, QPixmap, QIcon, QFont,
    QAction, QTransform, QPen
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QFrame,
    QHBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect, QSizePolicy,
    QMenuBar, QMenu, QTreeWidget, QTreeWidgetItem,
    QDialog, QGroupBox, QRadioButton, QComboBox,
    QToolBar, QToolButton, QFileDialog, QMessageBox,
    QStyledItemDelegate, QStyle,QFormLayout, QLineEdit, QCheckBox, QSpinBox, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QHeaderView, QDialogButtonBox,
    QPlainTextEdit, QStackedWidget,QListWidget,QListWidgetItem
)
from resources.theme import RADIUS_SM
from cc import LIGHT

class ModernTreeDelegate(QStyledItemDelegate):
    ROW_HEIGHT = 34

    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors = LIGHT

    def set_colors(self, colors):
        self.colors = colors

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        size.setHeight(self.ROW_HEIGHT)
        return size

    def paint(self, painter, option, index):
        c = self.colors
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        selected = bool(option.state & QStyle.State_Selected)
        hovered = bool(option.state & QStyle.State_MouseOver)
        has_children = index.model().hasChildren(index)
        expanded = bool(option.state & QStyle.State_Open)

        # Full-width row (ignores the indentation of child items)
        view = option.widget
        full_width = (
            view.viewport().width() if view is not None
            else option.rect.width()
        )
        row = QRectF(
            4,
            option.rect.top() + 2,
            full_width - 8,
            option.rect.height() - 4
        )

        painter.setPen(Qt.NoPen)

        if selected:
            bg = QColor(c["accent_blue"])
            bg.setAlpha(36)
            painter.setBrush(bg)
            painter.drawRoundedRect(row, RADIUS_SM, RADIUS_SM)

            painter.setBrush(QColor(c["accent_blue"]))
            painter.drawRoundedRect(
                QRectF(row.left(), row.top() + 7, 3, row.height() - 14),
                1.5, 1.5
            )
        elif hovered:
            painter.setBrush(QColor(c["border"]))
            painter.drawRoundedRect(row, RADIUS_SM, RADIUS_SM)

        x = option.rect.left()
        cy = option.rect.center().y()

        # Top-level items (Bus, Log, JSON Preview) share bold style + arrow
        is_top_level = not index.parent().isValid()

        # Chevron: expand/collapse for parents; right arrow for top-level leaves
        show_arrow = has_children or is_top_level
        if show_arrow:
            pen = QPen(QColor(c["text_secondary"]))
            pen.setWidthF(1.6)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)

            cx = x + 14
            if has_children and expanded:
                # Down-pointing (expanded)
                painter.drawPolyline([
                    QPointF(cx - 4, cy - 2),
                    QPointF(cx, cy + 2),
                    QPointF(cx + 4, cy - 2),
                ])
            else:
                # Right-pointing (collapsed parent, or JSON Preview)
                painter.drawPolyline([
                    QPointF(cx - 2, cy - 4),
                    QPointF(cx + 2, cy),
                    QPointF(cx - 2, cy + 4),
                ])

        # Text — DemiBold for any top-level item (same as Bus / Log)
        font = QFont()
        font.setFamilies(["Segoe UI Variable Text", "Segoe UI", "Arial"])
        font.setPointSizeF(10.5)
        font.setWeight(
            QFont.DemiBold if (has_children or is_top_level) else QFont.Normal
        )
        painter.setFont(font)
        painter.setPen(
            QColor(c["accent_blue"] if selected else c["text_primary"])
        )

        text_rect = QRectF(
            x + 28,
            option.rect.top(),
            max(10, full_width - x - 36),
            option.rect.height()
        )
        painter.drawText(
                    text_rect,
                    Qt.AlignVCenter | Qt.AlignLeft,
                    str(index.data())
                )
        
        painter.restore()