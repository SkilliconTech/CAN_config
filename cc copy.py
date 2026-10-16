import sys
import os
import copy
import json

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
from views.main_window import ConfigurationTool
from services.config_repository import (
    save_json,
    load_json
)
from models.constants import (
    DEFAULT_CLASSIC_CAN,
    DEFAULT_CANFD,
    PROJECT_EXT,
    PROJECT_FILTER,
    JSON_FILTER
)
from models.config_model import default_log_config
from views.log_config_widget import LogConfigWidget
from views.filter_dialog import FilterDialog
from views.widget_helpers import (
    make_combo,
    select_data,
    make_spin,
    make_note
)
from views.tree_delegate import ModernTreeDelegate
from views.canfd_dialog import CANFDSettingsDialog
from views.classic_can_dialog import (
    ClassicCANSettingsDialog
)
from resources.logo_widget import LogoWidget
from resources.icons import (
    ICONS_B64,
    tinted_icon,
    make_theme_icon
)
from resources.theme import (
    LIGHT,
    DARK,
    LOGO_GOLD_1,
    LOGO_GOLD_2,
    RADIUS_SM,
    RADIUS_LG,
    FONT_FAMILY
)
from services.config_validator import (
    require,
    check_keys,
    check_int,
    check_bool,
    parse_can_id,
    validate_rule,
    validate_log_config
)

# File types used by the toolbar
PROJECT_EXT = ".ccfg"
PROJECT_FILTER = "Config files (*.ccfg);;All files (*)"
JSON_FILTER = "JSON files (*.json);;All files (*)"

DEFAULT_CLASSIC_CAN = {
    "bitrate": "50.000 kbits/s",
    "sampling_point": "75%",
    "sjw": "1",
    "enabled": False,
}

# ------------------------------------------------------------------
# Modern tree look (rounded rows, chevrons, accent selection)
# ------------------------------------------------------------------
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

# ------------------------------------------------------------------
# Log configuration: validation (from d.py)
# ------------------------------------------------------------------
LOG_PAGES = {
    "Filters": "filters",
    "Triggers": "triggers",
    "Log Files": "logfiles",
    "JSON Preview": "preview",
}

def main():

    app = QApplication(sys.argv)

    app.setFont(
        QFont(FONT_FAMILY, 10)
    )

    window = ConfigurationTool()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
