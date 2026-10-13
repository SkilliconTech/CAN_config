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
DEFAULT_CANFD = {
    "arbitration_bitrate": "500 kbits/s",
    "arbitration_sp": "80.00%",
    "arbitration_sjw": "1",
    "data_bitrate": "500 kbits/s",
    "data_sp": "80.00%",
    "data_sjw": "1",
    "enabled": False,
}


LIGHT = {
    "bg_main": "#FFFFFF",
    "bg_panel": "#FFFFFF",
    "border": "#E7E9F1",
    "text_primary": "#1D2631",
    "text_secondary": "#6B7280",
    "accent_blue": "#4181EF",
    "toggle_icon": "#1D2631",
}

DARK = {
    "bg_main": "#14171F",
    "bg_panel": "#1B1F29",
    "border": "#2A2F3B",
    "text_primary": "#EDEFF3",
    "text_secondary": "#9AA1AE",
    "accent_blue": "#4181EF",
    "toggle_icon": "#EDEFF3",
}

LOGO_GOLD_1 = "#F2C14E"
LOGO_GOLD_2 = "#C9922A"

RADIUS_SM = 8
RADIUS_LG = 14

FONT_FAMILY = "Segoe UI"

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
# Toolbar icons (embedded, so no image files are needed)
# Black on transparent, 96x96 PNG, base64 encoded.
# ------------------------------------------------------------------
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


# ------------------------------------------------------------------
# OLD LogoWidget 
# ------------------------------------------------------------------
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


# ------------------------------------------------------------------
# Theme icon
# ------------------------------------------------------------------
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


# ------------------------------------------------------------------
# Classic CAN settings window
# ------------------------------------------------------------------
class ClassicCANSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent_window = parent
        self.setWindowTitle("CAN Channel 1 settings")
        self.resize(760, 560)

        # Keep the current Classic CAN configuration so that changes
        # made in the dialog are reflected in Current settings and
        # are available again when the dialog is opened.
        default_settings = {
            "bitrate": "50.000 kbits/s",
            "sampling_point": "75%",
            "sjw": "1",
            "enabled": False,
        }

        if parent is not None:
            self.settings = dict(
                getattr(
                    parent,
                    "classic_can_settings",
                    default_settings
                )
            )
        else:
            self.settings = dict(default_settings)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(14)

        # Bus parameter selection
        bus_mode_layout = QHBoxLayout()

        enter_bus = QRadioButton("Enter bus parameters")
        enter_bus.setChecked(True)

        bus_mode_layout.addWidget(enter_bus)
        bus_mode_layout.addSpacing(30)

        main_layout.addLayout(bus_mode_layout)

        # Bus parameters
        bus_group = QGroupBox("Bus parameters")
        bus_layout = QVBoxLayout(bus_group)
        bus_layout.setSpacing(10)

        bitrate_layout = QHBoxLayout()
        bitrate_label = QLabel("Bitrate and\nsampling point:")

        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems([
            "50.000 kbits/s, 75%",
            "100.000 kbits/s, 75%",
            "125.000 kbits/s, 75%",
            "250.000 kbits/s, 75%",
            "500.000 kbits/s, 75%",
            "1.000 Mbits/s, 75%",
        ])

        bitrate_layout.addWidget(bitrate_label)
        bitrate_layout.addWidget(self.bitrate_combo, 1)
        bus_layout.addLayout(bitrate_layout)

        sjw_layout = QHBoxLayout()
        sjw_label = QLabel("SJW:")

        self.sjw_combo = QComboBox()
        self.sjw_combo.addItems(["1", "2", "3", "4"])

        sjw_layout.addWidget(sjw_label)
        sjw_layout.addWidget(self.sjw_combo)
        sjw_layout.addStretch(1)

        bus_layout.addLayout(sjw_layout)

        main_layout.addWidget(bus_group)

        # Current settings
        current_group = QGroupBox("Current settings")
        current_layout = QVBoxLayout(current_group)

        self.current_bitrate = QLabel()
        self.current_sampling = QLabel()
        self.current_sjw = QLabel()

        current_layout.addWidget(self.current_bitrate)
        current_layout.addWidget(self.current_sampling)
        current_layout.addWidget(self.current_sjw)

        main_layout.addWidget(current_group)

        # Options and Store settings
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)

        self.enable_radio = QRadioButton("Enable")
        self.disable_radio = QRadioButton("Disable")

        if self.settings.get("enabled", False):
            self.enable_radio.setChecked(True)
        else:
            self.disable_radio.setChecked(True)

        options_layout.addWidget(self.enable_radio)
        options_layout.addWidget(self.disable_radio)
        options_layout.addStretch(1)

        bottom_layout.addWidget(options_group)

        store_group = QGroupBox("Store settings")
        store_layout = QVBoxLayout(store_group)
        store_layout.setSpacing(10)

        apply_all_layout = QHBoxLayout()
        apply_all_button = QPushButton("Apply to all")
        apply_all_description = QLabel(
            "Apply current settings to all other channels"
        )

        apply_all_layout.addWidget(apply_all_button)
        apply_all_layout.addWidget(apply_all_description)
        store_layout.addLayout(apply_all_layout)

        default_this_layout = QHBoxLayout()
        default_this_button = QPushButton("Set default for this")
        default_this_description = QLabel(
            "Store current settings as default for this channel"
        )

        default_this_layout.addWidget(default_this_button)
        default_this_layout.addWidget(default_this_description)
        store_layout.addLayout(default_this_layout)

        default_all_layout = QHBoxLayout()
        default_all_button = QPushButton("Set default for all")
        default_all_description = QLabel(
            "Store current settings as default for all channels"
        )

        default_all_layout.addWidget(default_all_button)
        default_all_layout.addWidget(default_all_description)
        store_layout.addLayout(default_all_layout)

        bottom_layout.addWidget(store_group, 1)

        main_layout.addLayout(bottom_layout)

        main_layout.addStretch(1)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(self.accept_settings)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)

        # Functional connections
        self.bitrate_combo.currentTextChanged.connect(
            self.update_current_settings
        )
        self.sjw_combo.currentTextChanged.connect(
            self.update_current_settings
        )

        apply_all_button.clicked.connect(
            self.apply_to_all
        )
        default_this_button.clicked.connect(
            self.set_default_for_this
        )
        default_all_button.clicked.connect(
            self.set_default_for_all
        )

        # Restore the previously stored values.
        self._restore_settings()
        self.update_current_settings()

    def _restore_settings(self):
        target = (
            f"{self.settings.get('bitrate', '50.000 kbits/s')}, "
            f"{self.settings.get('sampling_point', '75%')}"
        )

        index = self.bitrate_combo.findText(target)
        if index >= 0:
            self.bitrate_combo.setCurrentIndex(index)

        sjw_index = self.sjw_combo.findText(
            str(self.settings.get("sjw", "1"))
        )

        if sjw_index >= 0:
            self.sjw_combo.setCurrentIndex(sjw_index)

    def _collect_settings(self):
        selected = self.bitrate_combo.currentText()

        if "," in selected:
            bitrate, sampling_point = selected.split(",", 1)
            bitrate = bitrate.strip()
            sampling_point = sampling_point.strip()
        else:
            bitrate = selected.strip()
            sampling_point = ""

        return {
            "bitrate": bitrate,
            "sampling_point": sampling_point,
            "sjw": self.sjw_combo.currentText(),
            "enabled": self.enable_radio.isChecked(),
        }

    def update_current_settings(self):
        settings = self._collect_settings()

        self.current_bitrate.setText(
            f"Bitrate:                 {settings['bitrate']}"
        )

        self.current_sampling.setText(
            f"Sampling point:     {settings['sampling_point']}"
        )

        self.current_sjw.setText(
            f"SJW:                       {settings['sjw']}"
        )

    def apply_to_all(self):
        settings = self._collect_settings()

        if self.parent_window is not None:
            self.parent_window.classic_can_settings = dict(settings)
            self.parent_window.classic_can_all_settings = dict(settings)

    def set_default_for_this(self):
        settings = self._collect_settings()

        if self.parent_window is not None:
            self.parent_window.classic_can_default_settings = dict(settings)

    def set_default_for_all(self):
        settings = self._collect_settings()

        if self.parent_window is not None:
            self.parent_window.classic_can_default_all_settings = dict(
                settings
            )

    def accept_settings(self):
        settings = self._collect_settings()

        if self.parent_window is not None:
            self.parent_window.classic_can_settings = dict(settings)
            self.parent_window.classic_can_enabled = settings["enabled"]

        self.accept()


# ------------------------------------------------------------------
# CAN FD settings window
# ------------------------------------------------------------------
class CANFDSettingsDialog(QDialog):
    def __init__(self, parent=None):
        self.parent_window = parent
        self.settings = dict(
            getattr(parent, "canfd_settings", DEFAULT_CANFD)
        )
        super().__init__(parent)

        self.setWindowTitle("CAN Channel 1 settings")
        self.resize(900, 700)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(14)

        # Arbitration phase parameters
        arbitration_group = QGroupBox("Arbitration phase parameters")
        arbitration_layout = QVBoxLayout(arbitration_group)
        arbitration_layout.setSpacing(10)

        arbitration_bitrate_layout = QHBoxLayout()
        arbitration_bitrate_label = QLabel("Bitrate and\nsampling point:")
        arbitration_bitrate_combo = QComboBox()
        arbitration_bitrate_combo.addItems([
            "500 kbits/s, 80%",
            "1000 kbits/s, 80%",
        ])
        

        arbitration_bitrate_layout.addWidget(arbitration_bitrate_label)
        arbitration_bitrate_layout.addWidget(arbitration_bitrate_combo, 1)
        arbitration_layout.addLayout(arbitration_bitrate_layout)

        arbitration_sjw_layout = QHBoxLayout()
        arbitration_sjw_label = QLabel("SJW:")
        arbitration_sjw_combo = QComboBox()
        arbitration_sjw_combo.addItems([str(i) for i in range(1, 17)])

        arbitration_sjw_layout.addWidget(arbitration_sjw_label)
        arbitration_sjw_layout.addWidget(arbitration_sjw_combo)
        arbitration_sjw_layout.addStretch(1)
        arbitration_layout.addLayout(arbitration_sjw_layout)

        main_layout.addWidget(arbitration_group)

        # Data phase parameters
        data_group = QGroupBox("Data phase parameters")
        data_layout = QVBoxLayout(data_group)
        data_layout.setSpacing(10)

        data_bitrate_layout = QHBoxLayout()
        data_bitrate_label = QLabel("Bitrate and\nsampling point:")
        data_bitrate_combo = QComboBox()
        data_bitrate_combo.addItems([
            "500 kbits/s, 80.00%",
            "1000 kbits/s, 80.00%",
            "2000 kbits/s, 80.00%",
            "4000 kbits/s, 80.00%",
            "5000 kbits/s, 75.00%",
            "8000 kbits/s, 80.00%",
        ])
        

        data_bitrate_layout.addWidget(data_bitrate_label)
        data_bitrate_layout.addWidget(data_bitrate_combo, 1)
        data_layout.addLayout(data_bitrate_layout)

        data_sjw_layout = QHBoxLayout()
        data_sjw_label = QLabel("SJW:")
        data_sjw_combo = QComboBox()
        data_sjw_combo.addItems([str(i) for i in range(1, 17)])

        data_sjw_layout.addWidget(data_sjw_label)
        data_sjw_layout.addWidget(data_sjw_combo)
        data_sjw_layout.addStretch(1)
        data_layout.addLayout(data_sjw_layout)

        main_layout.addWidget(data_group)

        
        # Keep references so the Current settings can read the combos
        self.arbitration_bitrate_combo = arbitration_bitrate_combo
        self.arbitration_sjw_combo = arbitration_sjw_combo
        self.data_bitrate_combo = data_bitrate_combo
        self.data_sjw_combo = data_sjw_combo

        # Current settings
        current_group = QGroupBox("Current settings")
        current_layout = QHBoxLayout(current_group)

        self.cur_arb_bitrate = QLabel()
        self.cur_arb_sp = QLabel()
        self.cur_arb_sjw = QLabel()
        self.cur_data_bitrate = QLabel()
        self.cur_data_sp = QLabel()
        self.cur_data_sjw = QLabel()

        current_left_layout = QVBoxLayout()
        current_left_layout.addWidget(self.cur_arb_bitrate)
        current_left_layout.addWidget(self.cur_arb_sp)
        current_left_layout.addWidget(self.cur_arb_sjw)

        current_right_layout = QVBoxLayout()
        current_right_layout.addWidget(self.cur_data_bitrate)
        current_right_layout.addWidget(self.cur_data_sp)
        current_right_layout.addWidget(self.cur_data_sjw)

        current_layout.addLayout(current_left_layout)
        current_layout.addLayout(current_right_layout)

        main_layout.addWidget(current_group)

        # Update the labels whenever any of the four dropdowns changes
        for combo in (
            self.arbitration_bitrate_combo,
            self.arbitration_sjw_combo,
            self.data_bitrate_combo,
            self.data_sjw_combo,
        ):
            combo.currentTextChanged.connect(self.update_current_settings)

        self.update_current_settings()
        # Options and Store settings
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)

        self.enable_radio = QRadioButton("Enable")
        self.disable_radio = QRadioButton("Disable")

        options_layout.addWidget(self.enable_radio)
        options_layout.addWidget(self.disable_radio)
        options_layout.addStretch(1)

        bottom_layout.addWidget(options_group)


        store_group = QGroupBox("Store settings")
        store_layout = QVBoxLayout(store_group)
        store_layout.setSpacing(10)

        apply_all_layout = QHBoxLayout()
        apply_all_button = QPushButton("Apply to all")
        apply_all_description = QLabel(
            "Apply current settings to all other channels"
        )
        apply_all_layout.addWidget(apply_all_button)
        apply_all_layout.addWidget(apply_all_description)
        store_layout.addLayout(apply_all_layout)

        default_this_layout = QHBoxLayout()
        default_this_button = QPushButton("Set default for this")
        default_this_description = QLabel(
            "Store current settings as default for this channel"
        )
        default_this_layout.addWidget(default_this_button)
        default_this_layout.addWidget(default_this_description)
        store_layout.addLayout(default_this_layout)

        default_all_layout = QHBoxLayout()
        default_all_button = QPushButton("Set default for all")
        default_all_description = QLabel(
            "Store current settings as default for all channels"
        )
        default_all_layout.addWidget(default_all_button)
        default_all_layout.addWidget(default_all_description)
        store_layout.addLayout(default_all_layout)

        bottom_layout.addWidget(store_group, 1)
        main_layout.addLayout(bottom_layout)

        main_layout.addStretch(1)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(self.accept_settings)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)
        self._restore_settings()

    @staticmethod
    def _split_bitrate(text):
        if "," in text:
            bitrate, sampling_point = text.split(",", 1)
            return bitrate.strip(), sampling_point.strip()
        return text.strip(), ""

    def update_current_settings(self):
        arb_bitrate, arb_sp = self._split_bitrate(
            self.arbitration_bitrate_combo.currentText()
        )
        data_bitrate, data_sp = self._split_bitrate(
            self.data_bitrate_combo.currentText()
        )

        self.cur_arb_bitrate.setText(f"Arbitration bitrate:     {arb_bitrate}")
        self.cur_arb_sp.setText(f"Arbitration SP:          {arb_sp}")
        self.cur_arb_sjw.setText(
            f"Arbitration SJW:        {self.arbitration_sjw_combo.currentText()}"
        )

        self.cur_data_bitrate.setText(f"Data phase bitrate:     {data_bitrate}")
        self.cur_data_sp.setText(f"Data phase SP:          {data_sp}")
        self.cur_data_sjw.setText(
            f"Data phase SJW:        {self.data_sjw_combo.currentText()}"
        )

    @staticmethod
    def _select(combo, text):
        index = combo.findText(text)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _restore_settings(self):
        s = self.settings

        self._select(
            self.arbitration_bitrate_combo,
            f"{s.get('arbitration_bitrate', '500 kbits/s')}, "
            f"{s.get('arbitration_sp', '80.00%')}"
        )
        self._select(
            self.arbitration_sjw_combo,
            str(s.get("arbitration_sjw", "1"))
        )
        self._select(
            self.data_bitrate_combo,
            f"{s.get('data_bitrate', '500 kbits/s')}, "
            f"{s.get('data_sp', '80.00%')}"
        )
        self._select(
            self.data_sjw_combo,
            str(s.get("data_sjw", "1"))
        )

        if s.get("enabled", False):
            self.enable_radio.setChecked(True)
        else:
            self.disable_radio.setChecked(True)

        self.update_current_settings()

    def _collect_settings(self):
        arb_bitrate, arb_sp = self._split_bitrate(
            self.arbitration_bitrate_combo.currentText()
        )
        data_bitrate, data_sp = self._split_bitrate(
            self.data_bitrate_combo.currentText()
        )

        return {
            "arbitration_bitrate": arb_bitrate,
            "arbitration_sp": arb_sp,
            "arbitration_sjw": self.arbitration_sjw_combo.currentText(),
            "data_bitrate": data_bitrate,
            "data_sp": data_sp,
            "data_sjw": self.data_sjw_combo.currentText(),
            "enabled": self.enable_radio.isChecked(),
        }

    def accept_settings(self):
        if self.parent_window is not None:
            self.parent_window.canfd_settings = self._collect_settings()

        self.accept()

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

        # Chevron for items that have children
        if has_children:
            pen = QPen(QColor(c["text_secondary"]))
            pen.setWidthF(1.6)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)

            cx = x + 14
            if expanded:
                painter.drawPolyline([
                    QPointF(cx - 4, cy - 2),
                    QPointF(cx, cy + 2),
                    QPointF(cx + 4, cy - 2),
                ])
            else:
                painter.drawPolyline([
                    QPointF(cx - 2, cy - 4),
                    QPointF(cx + 2, cy),
                    QPointF(cx - 2, cy + 4),
                ])

        # Text
        font = QFont()
        font.setFamilies(["Segoe UI Variable Text", "Segoe UI", "Arial"])
        font.setPointSizeF(10.5)
        font.setWeight(QFont.DemiBold if has_children else QFont.Normal)
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


def default_log_config():
    return {
        "filters": {"mode": "all", "combine": "or", "rules": []},
        "triggers": {
            "start": {"type": "power_on"},
            "stop": {"type": "none"},
            "rearm_after_stop": False,
        },
        "logging": {
            "formats": ["asc", "mf4"],
            "file_split_size_bytes": 104857600,
            "file_split_time_seconds": 1800,
            "split_policy": "first_limit_reached",
            "on_sd_full": "stop",
            "on_write_error": "stop",
            "overwrite_existing": False,
        },
    }


def require(ok, message):
    if not ok:
        raise ValueError(message)


def check_keys(obj, expected, label):
    require(isinstance(obj, dict) and set(obj) == set(expected.split()),
            f"{label}: expected fields: {expected}")


def check_int(value, low, high, label):
    require(type(value) is int and low <= value <= high,
            f"{label}: enter an integer from {low} to {high}")


def check_bool(value, label):
    require(type(value) is bool, f"{label}: expected true or false")


def parse_can_id(value, extended):
    require(isinstance(value, str) and value.lower().startswith("0x")
            and len(value) > 2
            and all(c in "0123456789abcdefABCDEF" for c in value[2:]),
            "Use hexadecimal identifiers or masks, for example 0x123")
    result = int(value, 16)
    require(result <= (0x1FFFFFFF if extended else 0x7FF),
            "Identifier/mask exceeds selected ID width")
    return result


def validate_rule(rule):
    require(isinstance(rule, dict), "Filter must be an object")
    kind = rule.get("type")
    require(kind in ("id_list", "id_range", "id_mask"), "Invalid filter type")
    extra = {
        "id_list": "ids",
        "id_range": "id_start id_end",
        "id_mask": "match_id mask",
    }[kind]
    check_keys(rule, "filter_id enabled type extended_id " + extra, "Filter")
    require(isinstance(rule["filter_id"], str)
            and 1 <= len(rule["filter_id"].strip()) <= 64,
            "Filter name must have 1-64 characters")
    check_bool(rule["enabled"], "Filter enabled")
    check_bool(rule["extended_id"], "Extended ID")
    ext = rule["extended_id"]
    if kind == "id_list":
        require(isinstance(rule["ids"], list) and 1 <= len(rule["ids"]) <= 256,
                "Enter 1-256 IDs")
        values = [parse_can_id(v, ext) for v in rule["ids"]]
        require(len(set(values)) == len(values), "Duplicate IDs in list")
    elif kind == "id_range":
        require(parse_can_id(rule["id_start"], ext)
                <= parse_can_id(rule["id_end"], ext),
                "Range start exceeds end")
    else:
        parse_can_id(rule["match_id"], ext)
        parse_can_id(rule["mask"], ext)


def validate_log_config(data):
    check_keys(data, "filters triggers logging", "Log configuration")

    # ---- filters ----
    filters = data["filters"]
    check_keys(filters, "mode combine rules", "Filters")
    require(filters["mode"] in ("all", "matching") and filters["combine"] == "or",
            "Invalid filter mode/combination")
    require(isinstance(filters["rules"], list) and len(filters["rules"]) <= 64,
            "Maximum 64 filters")
    names = set()
    for rule in filters["rules"]:
        validate_rule(rule)
        require(rule["filter_id"] not in names, "Duplicate filter name")
        names.add(rule["filter_id"])
    require(filters["mode"] != "matching"
            or any(r["enabled"] for r in filters["rules"]),
            "Matching mode needs at least one enabled filter")

    # ---- triggers ----
    triggers = data["triggers"]
    check_keys(triggers, "start stop rearm_after_stop", "Triggers")
    check_bool(triggers["rearm_after_stop"], "Rearm")
    for side, allowed in [("start", ("power_on", "can_id_match")),
                          ("stop", ("none", "can_id_match", "duration"))]:
        trigger = triggers[side]
        require(isinstance(trigger, dict) and trigger.get("type") in allowed,
                f"Invalid {side} trigger")
        kind = trigger["type"]
        check_keys(
            trigger,
            "type can_id extended_id" if kind == "can_id_match" else
            "type seconds" if kind == "duration" else "type",
            side,
        )
        if kind == "can_id_match":
            check_bool(trigger["extended_id"], "Trigger ID format")
            parse_can_id(trigger["can_id"], trigger["extended_id"])
        if kind == "duration":
            check_int(trigger["seconds"], 1, 604800, "Recording duration")
    start, stop = triggers["start"], triggers["stop"]
    require(not triggers["rearm_after_stop"]
            or (start["type"] == "can_id_match" and stop["type"] != "none"),
            "Rearm requires ID start and a configured stop")
    if start["type"] == stop["type"] == "can_id_match":
        require(
            (parse_can_id(start["can_id"], start["extended_id"]),
             start["extended_id"]) !=
            (parse_can_id(stop["can_id"], stop["extended_id"]),
             stop["extended_id"]),
            "Start and stop IDs must differ")

    # ---- log files ----
    log = data["logging"]
    check_keys(log, "formats file_split_size_bytes file_split_time_seconds "
                    "split_policy on_sd_full on_write_error overwrite_existing",
               "Logging")
    formats = log["formats"]
    require(isinstance(formats, list) and 1 <= len(formats) <= 2
            and all(isinstance(f, str) and f in ("asc", "mf4") for f in formats),
            "Select ASC and/or MF4")
    require(len(set(formats)) == len(formats), "Duplicate output format")
    check_int(log["file_split_size_bytes"], 1048576, 2146435072, "File size limit")
    check_int(log["file_split_time_seconds"], 0, 604800, "File time limit")
    require(log["split_policy"] == "first_limit_reached", "Invalid split policy")
    require(log["on_sd_full"] == log["on_write_error"] == "stop",
            "Storage errors must stop logging")
    require(log["overwrite_existing"] is False,
            "Existing logs must not be overwritten")
    return data


# ------------------------------------------------------------------
# Small widget helpers
# ------------------------------------------------------------------
def make_combo(items):
    w = QComboBox()
    for label, value in items:
        w.addItem(label, value)
    return w


def select_data(widget, value):
    widget.setCurrentIndex(widget.findData(value))


def make_spin(low, high, suffix=""):
    w = QSpinBox()
    w.setRange(low, high)
    w.setSuffix(suffix)
    return w


def make_note(text):
    w = QLabel(text)
    w.setWordWrap(True)
    return w


# ------------------------------------------------------------------
# Filter rule editor
# ------------------------------------------------------------------
class FilterDialog(QDialog):
    def __init__(self, parent, rule):
        super().__init__(parent)
        self.setWindowTitle("Filter rule")
        self.resize(500, 320)

        form = QFormLayout(self)
        self.name_edit = QLineEdit(rule["filter_id"])
        self.enabled_box = QCheckBox("Enabled")
        self.enabled_box.setChecked(rule["enabled"])
        self.ext = QCheckBox("Extended (29-bit) identifier")
        self.ext.setChecked(rule["extended_id"])
        self.kind = make_combo([
            ("ID list", "id_list"),
            ("ID range", "id_range"),
            ("ID mask", "id_mask"),
        ])
        select_data(self.kind, rule["type"])
        self.first, self.second = QLineEdit(), QLineEdit()
        self.label1, self.label2 = QLabel(), QLabel()

        for label, w in [("Name", self.name_edit), ("", self.enabled_box),
                         ("", self.ext), ("Type", self.kind),
                         (self.label1, self.first), (self.label2, self.second)]:
            form.addRow(label, w)

        form.addRow(make_note(
            "Use 0x-prefixed IDs. Mask: (ID & mask) == (match ID & mask). "
            "A zero mask accepts every ID of the selected identifier format."
        ))

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.check)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self.kind.currentIndexChanged.connect(self.update_fields)
        self.update_fields()

        if rule["type"] == "id_list":
            self.first.setText(", ".join(rule["ids"]))
        else:
            self.first.setText(rule.get("id_start", rule.get("match_id", "")))
            self.second.setText(rule.get("id_end", rule.get("mask", "")))

    def update_fields(self):
        kind = self.kind.currentData()
        self.label1.setText({
            "id_list": "IDs (comma separated)",
            "id_range": "First ID",
            "id_mask": "Match ID",
        }[kind])
        self.label2.setText("Last ID" if kind == "id_range" else "Mask")
        self.second.setVisible(kind != "id_list")
        self.label2.setVisible(kind != "id_list")

    def rule(self):
        kind = self.kind.currentData()
        result = dict(
            filter_id=self.name_edit.text().strip(),
            enabled=self.enabled_box.isChecked(),
            type=kind,
            extended_id=self.ext.isChecked(),
        )
        a, b = self.first.text().strip(), self.second.text().strip()
        if kind == "id_list":
            result["ids"] = [v.strip() for v in a.split(",")]
        elif kind == "id_range":
            result.update(id_start=a, id_end=b)
        else:
            result.update(match_id=a, mask=b)
        return result

    def check(self):
        try:
            validate_rule(self.rule())
            self.accept()
        except ValueError as error:
            QMessageBox.warning(self, "Invalid filter", str(error))


# ------------------------------------------------------------------
# Filters / Triggers / Log Files / JSON Preview pages
# ------------------------------------------------------------------
class LogConfigWidget(QStackedWidget):
    PAGES = ("filters", "triggers", "logfiles", "preview")

    def __init__(self, get_full_config, show_status, parent=None):
        super().__init__(parent)
        self.get_full_config = get_full_config
        self.show_status = show_status
        self.rules = []

        # ---------------- Filters page ----------------
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)

        self.filter_mode = make_combo([
            ("Log all frames", "all"),
            ("Log matching frames (OR)", "matching"),
        ])
        layout.addWidget(self.filter_mode)
        layout.addWidget(make_note(
            "Filters control storage. Trigger detection still sees excluded frames."
        ))

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Enabled", "Identifier", "Type", "Condition"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(lambda _: self.edit_filter())
        layout.addWidget(self.table)

        row = QHBoxLayout()
        for label, slot in [("Add", self.add_filter), ("Edit", self.edit_filter),
                            ("Remove", self.remove_filter),
                            ("Remove All", self.remove_all)]:
            button = QPushButton(label)
            button.clicked.connect(slot)
            row.addWidget(button)
        layout.addLayout(row)
        self.addWidget(page)

        # ---------------- Triggers page ----------------
        page = QWidget()
        form = QFormLayout(page)
        form.setContentsMargins(0, 0, 0, 0)

        self.start = make_combo([
            ("After initialization (power-on)", "power_on"),
            ("CAN ID match", "can_id_match"),
        ])
        self.stop = make_combo([
            ("No configured stop", "none"),
            ("CAN ID match", "can_id_match"),
            ("Recording duration", "duration"),
        ])
        self.start_id, self.stop_id = QLineEdit("0x123"), QLineEdit("0x124")
        self.start_ext = QCheckBox("Extended ID")
        self.stop_ext = QCheckBox("Extended ID")
        self.duration = make_spin(1, 604800, " seconds")
        self.rearm = QCheckBox("Wait for a new start ID after a normal stop")

        for label, w in [("Start recording", self.start),
                         ("Start ID", self.start_id), ("", self.start_ext),
                         ("Stop recording", self.stop),
                         ("Stop ID", self.stop_id), ("", self.stop_ext),
                         ("Recording duration", self.duration),
                         ("Rearm", self.rearm)]:
            form.addRow(label, w)

        form.addRow(make_note(
            "Trigger frames are stored if they pass filters. Duration starts at "
            "recording start; repeated start frames do not extend it. SD full or "
            "write failure stops without rearming. Power loss may lose buffered data."
        ))
        self.addWidget(page)

        # ---------------- Log Files page ----------------
        page = QWidget()
        form = QFormLayout(page)
        form.setContentsMargins(0, 0, 0, 0)

        self.asc = QCheckBox("ASC")
        self.mf4 = QCheckBox("MF4 (ASAM MDF 4)")
        self.size_limit = make_spin(1048576, 2146435072, " bytes")
        self.time_limit = make_spin(0, 604800, " seconds")
        self.time_limit.setSpecialValueText("Disabled")

        for label, w in [("Formats", self.asc), ("", self.mf4),
                         ("File size limit", self.size_limit),
                         ("File duration limit", self.time_limit)]:
            form.addRow(label, w)

        form.addRow(make_note(
            "Split at the first enabled limit, separately for each output format. "
            "Never overwrite existing logs. MF4 requests a real MDF 4 writer in "
            "firmware; renaming ASC does not create MF4."
        ))
        self.addWidget(page)

        # ---------------- JSON Preview page ----------------
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFont(QFont("Consolas", 10))
        self.addWidget(self.preview)

        for w in (self.start, self.stop):
            w.currentIndexChanged.connect(self.update_controls)

        self.apply(default_log_config())

    # ---------------- page switching ----------------
    def show_page(self, name):
        self.setCurrentIndex(self.PAGES.index(name))
        if name == "preview":
            self.refresh_preview()

    def update_controls(self):
        for selector, field, ext in [
            (self.start, self.start_id, self.start_ext),
            (self.stop, self.stop_id, self.stop_ext),
        ]:
            is_id = selector.currentData() == "can_id_match"
            field.setEnabled(is_id)
            ext.setEnabled(is_id)

        self.duration.setEnabled(self.stop.currentData() == "duration")

        can_rearm = (self.start.currentData() == "can_id_match"
                     and self.stop.currentData() != "none")
        self.rearm.setEnabled(can_rearm)
        if not can_rearm:
            self.rearm.setChecked(False)

    # ---------------- data in / out ----------------
    def collect(self):
        data = default_log_config()
        data["filters"].update(
            mode=self.filter_mode.currentData(),
            rules=copy.deepcopy(self.rules),
        )

        for side, selector, field, ext in [
            ("start", self.start, self.start_id, self.start_ext),
            ("stop", self.stop, self.stop_id, self.stop_ext),
        ]:
            trigger = {"type": selector.currentData()}
            if trigger["type"] == "can_id_match":
                trigger.update(can_id=field.text().strip(),
                               extended_id=ext.isChecked())
            elif trigger["type"] == "duration":
                trigger["seconds"] = self.duration.value()
            data["triggers"][side] = trigger

        data["triggers"]["rearm_after_stop"] = self.rearm.isChecked()
        data["logging"].update(
            formats=[name for name, w in [("asc", self.asc), ("mf4", self.mf4)]
                     if w.isChecked()],
            file_split_size_bytes=self.size_limit.value(),
            file_split_time_seconds=self.time_limit.value(),
        )
        return data

    def apply(self, data):
        validate_log_config(data)

        select_data(self.filter_mode, data["filters"]["mode"])
        self.rules = copy.deepcopy(data["filters"]["rules"])
        self.refresh_table()

        for side, selector, field, ext in [
            ("start", self.start, self.start_id, self.start_ext),
            ("stop", self.stop, self.stop_id, self.stop_ext),
        ]:
            trigger = data["triggers"][side]
            select_data(selector, trigger["type"])
            field.setText(trigger.get(
                "can_id", "0x123" if side == "start" else "0x124"))
            ext.setChecked(trigger.get("extended_id", False))

        self.duration.setValue(data["triggers"]["stop"].get("seconds", 600))
        self.rearm.setChecked(data["triggers"]["rearm_after_stop"])

        self.asc.setChecked("asc" in data["logging"]["formats"])
        self.mf4.setChecked("mf4" in data["logging"]["formats"])
        self.size_limit.setValue(data["logging"]["file_split_size_bytes"])
        self.time_limit.setValue(data["logging"]["file_split_time_seconds"])

        self.update_controls()
        if self.currentIndex() == self.PAGES.index("preview"):
            self.refresh_preview()

    # ---------------- filter table ----------------
    def refresh_table(self):
        self.table.setRowCount(len(self.rules))
        for row, r in enumerate(self.rules):
            if r["type"] == "id_list":
                condition = ", ".join(r["ids"])
            elif r["type"] == "id_range":
                condition = f"{r['id_start']} – {r['id_end']}"
            else:
                condition = f"Match {r['match_id']}; mask {r['mask']}"

            for col, value in enumerate([
                r["filter_id"],
                "Yes" if r["enabled"] else "No",
                "Extended" if r["extended_id"] else "Standard",
                r["type"],
                condition,
            ]):
                self.table.setItem(row, col, QTableWidgetItem(value))

    def edit_rule(self, index=None):
        parent = self.window()

        if index is None:
            if len(self.rules) >= 64:
                QMessageBox.warning(parent, "Limit", "Maximum 64 filters")
                return
            n = 1
            while any(r["filter_id"] == f"F{n}" for r in self.rules):
                n += 1
            rule = dict(filter_id=f"F{n}", enabled=True, type="id_list",
                        extended_id=False, ids=["0x123"])
        else:
            rule = self.rules[index]

        dialog = FilterDialog(parent, rule)
        while dialog.exec():
            rule = dialog.rule()
            if any(r["filter_id"] == rule["filter_id"]
                   for i, r in enumerate(self.rules) if i != index):
                QMessageBox.warning(parent, "Duplicate name",
                                    "Choose a unique filter name")
                continue
            if index is None:
                self.rules.append(rule)
            else:
                self.rules[index] = rule
            self.refresh_table()
            break

    def add_filter(self):
        self.edit_rule()

    def edit_filter(self):
        if self.table.currentRow() >= 0:
            self.edit_rule(self.table.currentRow())

    def remove_filter(self):
        if self.table.currentRow() >= 0:
            del self.rules[self.table.currentRow()]
            self.refresh_table()

    def remove_all(self):
        if self.rules and QMessageBox.question(
                self.window(), "Remove filters", "Remove all filters?"
        ) == QMessageBox.Yes:
            self.rules.clear()
            self.refresh_table()

    # ---------------- JSON preview ----------------
    def refresh_preview(self):
        self.preview.setPlainText(json.dumps(self.get_full_config(), indent=2))
        try:
            validate_log_config(self.collect())
            self.show_status(
                "Valid configuration; device must verify firmware capabilities.")
        except ValueError as error:
            self.show_status(str(error))

    # ---------------- theme ----------------
    def set_theme(self, c):
        self.setStyleSheet(f"""
            QLabel, QCheckBox {{
                color: {c['text_primary']};
                background: transparent;
            }}
            QLabel:disabled, QCheckBox:disabled {{
                color: {c['text_secondary']};
            }}
            QLineEdit, QSpinBox, QComboBox, QPlainTextEdit {{
                background-color: {c['bg_main']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: {RADIUS_SM}px;
                padding: 4px 6px;
            }}
            QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {{
                color: {c['text_secondary']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {c['bg_panel']};
                color: {c['text_primary']};
                selection-background-color: {c['accent_blue']};
                selection-color: #FFFFFF;
            }}
            QTableWidget {{
                background-color: {c['bg_main']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: {RADIUS_SM}px;
                gridline-color: {c['border']};
                selection-background-color: {c['accent_blue']};
                selection-color: #FFFFFF;
            }}
            QHeaderView::section {{
                background-color: {c['bg_panel']};
                color: {c['text_secondary']};
                border: none;
                border-bottom: 1px solid {c['border']};
                padding: 6px;
            }}
            QPushButton {{
                background-color: {c['bg_panel']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: {RADIUS_SM}px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                border: 1px solid {c['accent_blue']};
            }}
        """)



class ConfigurationTool(QMainWindow):

    def __init__(self):
        super().__init__()

        self.dark_mode = False
        self.current_file_path = None      # file used by Save / Ctrl+S
        # Classic CAN runtime configuration/state
        self.classic_can_settings = {
            "bitrate": "50.000 kbits/s",
            "sampling_point": "75%",
            "sjw": "1",
            "enabled": False,
        }
        self.classic_can_default_settings = dict(
            self.classic_can_settings
        )
        self.classic_can_default_all_settings = dict(
            self.classic_can_settings
        )
        self.classic_can_all_settings = dict(
            self.classic_can_settings
        )
        self.classic_can_enabled = False
        self.canfd_settings = dict(DEFAULT_CANFD)

        self.setWindowTitle("Configuration Tool")
        self.resize(1400, 850)

        # ------------------------------------------------------------------
        # Toolbar (New / Open / Save / Import / Export)
        # ------------------------------------------------------------------
        self._create_toolbar()

        # ------------------------------------------------------------------
        # Central layout
        # ------------------------------------------------------------------
        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---------------- Left sidebar ----------------
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(300)
        self.sidebar.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(
            20,
            24,
            20,
            24
        )
        sidebar_layout.setSpacing(0)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(10)

        # --------------------------------------------------------------
        # Configuration Tool text
        # --------------------------------------------------------------
        self.brand_label = QLabel(
            "Configuration Tool"
        )

        brand_font = QFont()
        brand_font.setFamilies(["Segoe UI Variable Display", "Segoe UI", "Arial"])
        brand_font.setPointSizeF(12.5)
        brand_font.setWeight(QFont.DemiBold)

        self.brand_label.setFont(
            brand_font
        )

        brand_row.addWidget(
            self.brand_label
        )

        brand_row.addStretch(1)

        sidebar_layout.addLayout(
            brand_row
        )
        sidebar_layout.addSpacing(14)
        section_font = QFont()
        section_font.setFamilies(["Segoe UI Variable Text", "Segoe UI", "Arial"])
        section_font.setPointSizeF(10.5)
        section_font.setWeight(QFont.DemiBold)

        # ================================================================
        # SECTION 1: Imported Files  (own frame + own layout)
        # ================================================================
        self.imported_section = QFrame()
        self.imported_section.setObjectName("importedSection")
        self.imported_section.setAttribute(Qt.WA_StyledBackground, True)
        imported_layout = QVBoxLayout(self.imported_section)
        imported_layout.setContentsMargins(10, 10, 10, 10)
        imported_layout.setSpacing(6)

        self.imported_label = QLabel("Imported Files")
        self.imported_label.setFont(section_font)
        imported_layout.addWidget(self.imported_label)

        self.imported_list = QListWidget()
        self.imported_list.setObjectName("importedList")
        self.imported_list.setUniformItemSizes(True)
        self.imported_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.imported_list.setSpacing(2)
        self.imported_list.setMaximumHeight(120)   # keep the list compact
        self.imported_list.itemClicked.connect(self.on_imported_file_clicked)
        imported_layout.addWidget(self.imported_list)
        sidebar_layout.addWidget(self.imported_section, 0)

        sidebar_layout.addSpacing(12)

        # ================================================================
        # SECTION 2: Bus / Log Configuration  (own frame + own layout)
        # ================================================================
        self.config_section = QFrame()
        self.config_section.setObjectName("configSection")
        self.config_section.setAttribute(Qt.WA_StyledBackground, True)
        config_layout = QVBoxLayout(self.config_section)
        config_layout.setContentsMargins(10, 10, 10, 10)
        config_layout.setSpacing(6)

        self.config_label = QLabel("Configuration")
        self.config_label.setFont(section_font)
        config_layout.addWidget(self.config_label)

        self.new_tree = QTreeWidget()
        self.new_tree.setHeaderHidden(True)
        self.new_tree.setVisible(True)
        self.new_tree.setRootIsDecorated(False)
        self.new_tree.setIndentation(16)
        self.new_tree.setAnimated(True)
        self.new_tree.setExpandsOnDoubleClick(False)
        self.new_tree.setUniformRowHeights(True)
        self.new_tree.setMouseTracking(True)
        self.new_tree.viewport().setAttribute(Qt.WA_Hover, True)
        self.new_tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.new_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tree_delegate = ModernTreeDelegate(self.new_tree)
        self.new_tree.setItemDelegate(self.tree_delegate)
        self.new_tree.itemClicked.connect(self.on_tree_item_clicked)
        config_layout.addWidget(self.new_tree, 1)

        # stretch 1 = grow and fill remaining space under Imported Files
        sidebar_layout.addWidget(self.config_section, 1)
        self.imported_files = []
        
      

        root_layout.addWidget(
            self.sidebar
        )

        # ---------------- Main area ----------------
        main_area = QWidget()
        main_area.setObjectName(
            "mainArea"
        )

        main_area.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        main_layout = QVBoxLayout(
            main_area
        )

        main_layout.setContentsMargins(
            32,
            28,
            32,
            28
        )

        main_layout.setSpacing(24)

        topbar = QHBoxLayout()

        self.title_label = QLabel(
            "Configuration Tool"
        )

        title_font = QFont(
            FONT_FAMILY,
            21,
            QFont.Bold
         )

        self.title_label.setFont(
            title_font
        )

        topbar.addWidget(
            self.title_label
        )

        topbar.addStretch(1)

        self.theme_toggle = QPushButton()
        self.theme_toggle.setObjectName(
            "themeToggle"
        )

        self.theme_toggle.setFixedSize(
            42,
            42
        )

        self.theme_toggle.setCursor(
            Qt.PointingHandCursor
        )

        self.theme_toggle.setIconSize(
            QSize(18, 18)
        )

        self.theme_toggle.clicked.connect(
            self.toggle_theme
        )

        topbar.addWidget(
            self.theme_toggle
        )

        main_layout.addLayout(
            topbar
        )

        self.content_panel = QFrame()
        self.content_panel.setObjectName(
            "contentPanel"
        )

        self.content_panel.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        self.content_panel.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        content_layout = QVBoxLayout(self.content_panel)
        content_layout.setContentsMargins(24, 24, 24, 24)

        self.log_pages = LogConfigWidget(
            get_full_config=self._collect_config,
            show_status=lambda msg: self.statusBar().showMessage(msg, 8000),
        )
        self.log_pages.setVisible(False)
        content_layout.addWidget(self.log_pages)

        shadow = QGraphicsDropShadowEffect(
            self
        )

        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(2)

        shadow.setColor(
            QColor(
                16,
                24,
                40,
                40
            )
        )

        self.content_panel.setGraphicsEffect(
            shadow
        )

        main_layout.addWidget(
            self.content_panel,
            1
        )

        root_layout.addWidget(
            main_area,
            1
        )

        self.apply_theme()
        self._show_device_tree()      # show the device tree on startup

    # ------------------------------------------------------------------
    # Toolbar
    # ------------------------------------------------------------------
    def _create_toolbar(self):
        self.toolbar = QToolBar("Main toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setIconSize(QSize(18, 18))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.act_new = QAction("New", self)
        self.act_new.setShortcut("Ctrl+N")
        self.act_new.setToolTip("New configuration (Ctrl+N)")
        self.act_new.triggered.connect(self.on_new)

        self.act_open = QAction("Open", self)
        self.act_open.setShortcut("Ctrl+O")
        self.act_open.setToolTip("Open configuration (Ctrl+O)")
        self.act_open.triggered.connect(self.on_open)

        self.act_save = QAction("Save", self)
        self.act_save.setShortcut("Ctrl+S")
        self.act_save.setToolTip("Save (Ctrl+S)")
        self.act_save.triggered.connect(self.on_save)

        self.act_save_as = QAction("Save As...", self)
        self.act_save_as.setShortcut("Ctrl+Shift+S")
        self.act_save_as.setToolTip("Save As (Ctrl+Shift+S)")
        self.act_save_as.triggered.connect(self.on_save_as)

        self.act_import = QAction("Import", self)
        self.act_import.setToolTip("Import settings from a JSON file")
        self.act_import.triggered.connect(self.on_import)

        self.act_export = QAction("Export", self)
        self.act_export.setToolTip("Export settings to a JSON file")
        self.act_export.triggered.connect(self.on_export)

        # Make the Ctrl+S / Ctrl+Shift+S shortcuts work anywhere in the window
        self.addAction(self.act_save)
        self.addAction(self.act_save_as)

        # Save button: click = Save, small arrow = Save As
        save_menu = QMenu(self)
        save_menu.addAction(self.act_save_as)

        self.save_button = QToolButton()
        self.save_button.setDefaultAction(self.act_save)
        self.save_button.setMenu(save_menu)
        self.save_button.setPopupMode(QToolButton.MenuButtonPopup)
        self.save_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.save_button.setIconSize(QSize(18, 18))

        self.toolbar.addAction(self.act_new)
        self.toolbar.addAction(self.act_open)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.save_button)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_import)
        self.toolbar.addAction(self.act_export)

    def _refresh_toolbar_theme(self, c):
        for action, name in (
            (self.act_new, "new"),
            (self.act_open, "open"),
            (self.act_save, "save"),
            (self.act_import, "import"),
            (self.act_export, "export"),
        ):
            action.setIcon(tinted_icon(name, c["toggle_icon"]))

        self.toolbar.setStyleSheet(
            f"""
            QToolBar {{
                background-color: {c['bg_panel']};
                border: none;
                border-bottom: 1px solid {c['border']};
                spacing: 2px;
                padding: 1px 6px;
            }}
            QToolBar::separator {{
                background-color: {c['border']};
                width: 1px;
                margin: 4px 4px;
            }}
            QToolButton {{
                color: {c['text_primary']};
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: {RADIUS_SM}px;
                padding: 2px 8px;
                font-size: 9pt;
            }}
            QToolButton:hover {{
                border: 1px solid {c['accent_blue']};
            }}
            QToolButton::menu-button {{
                border: none;
                width: 12px;
            }}
            """
        )

        self.statusBar().setStyleSheet(
            f"QStatusBar {{ background-color: {c['bg_panel']};"
            f" color: {c['text_secondary']}; }}"
        )

    # ------------------------------------------------------------------
    # Window title
    # ------------------------------------------------------------------
    def _update_title(self):
        name = (
            f" - {os.path.basename(self.current_file_path)}"
            if self.current_file_path else ""
        )
        self.setWindowTitle(f"Configuration Tool{name}")

    # ------------------------------------------------------------------
    # Configuration data (used by Save / Open / Import / Export)
    # ------------------------------------------------------------------
    def _collect_config(self) -> dict:
        data = {
            "app": "CAN Configuration Tool",
            "version": 1,
            "classic_can": dict(self.classic_can_settings),
            "canfd": dict(self.canfd_settings),
        }
        data.update(self.log_pages.collect())   # filters, triggers, logging
        return data
    def _apply_config(self, data):
        if not isinstance(data, dict) or not isinstance(
            data.get("classic_can"), dict
        ):
            raise ValueError("This is not a valid configuration file.")
        log_data = default_log_config()
        for key in ("filters", "triggers", "logging"):
            if key in data:
                log_data[key] = data[key]
        validate_log_config(log_data)

        settings = dict(DEFAULT_CLASSIC_CAN)
        settings.update(data["classic_can"])

        self.classic_can_settings = settings
        self.classic_can_enabled = bool(settings.get("enabled", False))
        canfd = dict(DEFAULT_CANFD)
        if isinstance(data.get("canfd"), dict):
            canfd.update(data["canfd"])
        self.canfd_settings = canfd
        self.log_pages.apply(log_data)

    def _write_json(self, path: str) -> bool:
        data = self._collect_config()

        try:
            validate_log_config({k: data[k] for k in ("filters", "triggers", "logging")})
        except ValueError as e:
            QMessageBox.warning(self, "Invalid configuration", str(e))
            return False

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            return True
        except OSError as e:
            QMessageBox.critical(
                self, "Save error", f"Could not write file:\n{e}"
            )
            return False

    def _read_json(self, path: str) -> bool:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._apply_config(data)
            return True
        except (OSError, json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
            QMessageBox.critical(
                self, "Load error", f"Could not load file:\n{e}"
            )
            return False
    # ------------------------------------------------------------------
    # Imported files list
    # ------------------------------------------------------------------
    def _add_imported_file(self, path: str):
        """Add a JSON file to the sidebar list if not already present."""
        path = os.path.normpath(os.path.abspath(path))
        if path in self.imported_files:
            for i in range(self.imported_list.count()):
                item = self.imported_list.item(i)
                if item.data(Qt.UserRole) == path:
                    self.imported_list.setCurrentItem(item)
                    break
            return

        self.imported_files.append(path)
        item = QListWidgetItem(os.path.basename(path))
        item.setData(Qt.UserRole, path)
        item.setToolTip(path)
        self.imported_list.addItem(item)
        self.imported_list.setCurrentItem(item)

    def on_imported_file_clicked(self, item: QListWidgetItem):
        path = item.data(Qt.UserRole)
        if not path:
            return
        if self._read_json(path):
            self.statusBar().showMessage(f"Loaded: {path}", 3000)
            self._show_device_tree()
    # ------------------------------------------------------------------
    # Toolbar actions
    # ------------------------------------------------------------------

    def on_new(self):
        self.classic_can_settings = dict(DEFAULT_CLASSIC_CAN)
        self.classic_can_enabled = False
        self.current_file_path = None
        self._update_title()
        self._show_device_tree()
        self.statusBar().showMessage("New configuration", 3000)
        self.canfd_settings = dict(DEFAULT_CANFD)
        self.log_pages.apply(default_log_config())
        self.imported_list.clearSelection()

    def on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open configuration", "", PROJECT_FILTER
        )
        if not path:
            return

        if self._read_json(path):
            self.current_file_path = path
            self._update_title()
            self._show_device_tree()
            self.statusBar().showMessage(f"Opened: {path}", 3000)

    def on_save(self):
        # First time: no path yet, so ask for it. After that: save silently.
        if self.current_file_path is None:
            self.on_save_as()
            return

        if self._write_json(self.current_file_path):
            self.statusBar().showMessage(
                f"Saved: {self.current_file_path}", 3000
            )

    def on_save_as(self):
        start = self.current_file_path or ("config" + PROJECT_EXT)
        path, _ = QFileDialog.getSaveFileName(
            self, "Save As", start, PROJECT_FILTER
        )
        if not path:
            return

        if not os.path.splitext(path)[1]:
            path += PROJECT_EXT

        if self._write_json(path):
            self.current_file_path = path
            self._update_title()
            self.statusBar().showMessage(f"Saved: {path}", 3000)

    def on_import(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import JSON", "", JSON_FILTER
        )
        if not path:
            return

        if self._read_json(path):
            self._add_imported_file(path)
            self._show_device_tree()
            self.statusBar().showMessage(f"Imported: {path}", 3000)

    def on_export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export JSON", "config_export.json", JSON_FILTER
        )
        if not path:
            return

        if not os.path.splitext(path)[1]:
            path += ".json"

        if self._write_json(path):
            self.statusBar().showMessage(f"Exported: {path}", 3000)

    # ------------------------------------------------------------------
    # Device tree
    # ------------------------------------------------------------------
    def _show_device_tree(self):
        self.new_tree.clear()

        bus_item = QTreeWidgetItem(["Bus Configuration"])
        bus_item.addChild(QTreeWidgetItem(["Classic CAN"]))
        bus_item.addChild(QTreeWidgetItem(["CAN FD"]))

        self.new_tree.addTopLevelItem(bus_item)
        log_item = QTreeWidgetItem(["Log Configuration"])
        log_item.addChild(QTreeWidgetItem(["Filters"]))
        log_item.addChild(QTreeWidgetItem(["Triggers"]))
        log_item.addChild(QTreeWidgetItem(["Log Files"]))
        log_item.addChild(QTreeWidgetItem(["JSON Preview"]))
        self.new_tree.addTopLevelItem(log_item)

        bus_item.setExpanded(False)
        self.new_tree.setVisible(True)

    def on_tree_item_clicked(self, item, column):
        if item.childCount() > 0:
            item.setExpanded(not item.isExpanded())
            return
        page = LOG_PAGES.get(item.text(0))
        if page:
            self.title_label.setText(item.text(0))   # big title shows the page name
            self.log_pages.show_page(page)
            self.log_pages.setVisible(True)
            return

        if item.text(0) == "Classic CAN":
            dialog = ClassicCANSettingsDialog(self)
            dialog.exec()
        elif item.text(0) == "CAN FD":
            dialog = CANFDSettingsDialog(self)
            dialog.exec()

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def toggle_theme(self):

        self.dark_mode = not self.dark_mode

        self.apply_theme()

    def apply_theme(self):

        c = (
            DARK
            if self.dark_mode
            else LIGHT
        )

        self.sidebar.setStyleSheet(
            f"""
            #sidebar {{
                background-color: {c['bg_panel']};
                border-right: 1px solid {c['border']};
            }}
            """
        )

        self.brand_label.setStyleSheet(
            f"color: {c['text_primary']};"
        )

        # Section titles — primary + bold (only once)
        self.imported_label.setStyleSheet(
            f"color: {c['text_primary']}; font-weight: 600;"
        )
        self.config_label.setStyleSheet(
            f"color: {c['text_primary']}; font-weight: 600;"
        )

        # Visible section boxes (only once)
        section_style = f"""
            background-color: {c['bg_main']};
            border: 2px solid {c['border']};
            border-radius: {RADIUS_LG}px;
        """
        self.imported_section.setStyleSheet(
            f"#importedSection {{ {section_style} }}"
        )
        self.config_section.setStyleSheet(
            f"#configSection {{ {section_style} }}"
        )

        self.centralWidget().layout().itemAt(
            1
        ).widget().setStyleSheet(
            f"""
            #mainArea {{
                background-color: {c['bg_main']};
            }}
            """
        )

        self.title_label.setStyleSheet(
            f"color: {c['text_primary']};"
        )

        self.theme_toggle.setStyleSheet(
            f"""
            #themeToggle {{
                background-color: {c['bg_panel']};
                border: 1px solid {c['border']};
                border-radius: {RADIUS_SM}px;
            }}

            #themeToggle:hover {{
                border: 1px solid {c['accent_blue']};
            }}
            """
        )

        self.theme_toggle.setIcon(
            make_theme_icon(
                self.dark_mode,
                c["toggle_icon"]
            )
        )

        self.content_panel.setStyleSheet(
            f"""
            #contentPanel {{
                background-color: {c['bg_panel']};
                border: 1px solid {c['border']};
                border-radius: {RADIUS_LG}px;
            }}
            """
        )

        # Imported list — transparent inside its section (only once)
        self.imported_list.setStyleSheet(
            f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: 0;
                padding: 2px;
            }}
            QListWidget::item {{
                color: {c['text_primary']};
                border-radius: {RADIUS_SM}px;
                padding: 6px 8px;
            }}
            QListWidget::item:hover {{
                background-color: {c['border']};
            }}
            QListWidget::item:selected {{
                background-color: {c['accent_blue']};
                color: #FFFFFF;
            }}
            """
        )

        self.new_tree.setStyleSheet(
            f"""
            QTreeWidget {{
                background-color: transparent;
                border: none;
                outline: 0;
            }}
            """
        )
        self.tree_delegate.set_colors(c)
        self.new_tree.viewport().update()

        self._refresh_toolbar_theme(c)
        self.log_pages.set_theme(c)

def main():

    app = QApplication(
        sys.argv
    )

    app.setFont(
        QFont(
            FONT_FAMILY,
            10
        )
    )

    window = ConfigurationTool()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()