from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QRadioButton,
    QComboBox,
    QScrollArea,
    QFrame,
    QPushButton
)
from resources.theme import RADIUS_SM
from views.check_radio import CheckRadioButton
from PySide6.QtCore import Qt
from models.constants import DEFAULT_CLASSIC_CAN


class ClassicCANSettingsDialog(QWidget):
    """Classic CAN settings shown in the right content panel (not a popup)."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent_window = parent

        default_settings = dict(DEFAULT_CLASSIC_CAN)

        if parent is not None:
            self.settings = dict(
                getattr(parent, "classic_can_settings", default_settings)
            )
        else:
            self.settings = dict(default_settings)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        body = QWidget()
        scroll.setWidget(body)

        main_layout = QVBoxLayout(body)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(8)

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
        bus_layout.setSpacing(6)

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
        bottom_layout.setSpacing(12)

        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)

        self.enable_radio = CheckRadioButton("Enable")
        self.disable_radio = CheckRadioButton("Disable")

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
        store_layout.setSpacing(6)

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
        # Apply / Save / Cancel
        action_row = QHBoxLayout()
        action_row.addStretch(1)

        self.apply_button = QPushButton("Apply")
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.apply_button.clicked.connect(self.on_apply)
        self.save_button.clicked.connect(self.on_save)
        self.cancel_button.clicked.connect(self.on_cancel)

        action_row.addWidget(self.apply_button)
        action_row.addWidget(self.save_button)
        action_row.addWidget(self.cancel_button)
        main_layout.addLayout(action_row)

        # Functional connections
        self.bitrate_combo.currentTextChanged.connect(self.update_current_settings)
        self.sjw_combo.currentTextChanged.connect(self.update_current_settings)
        self.enable_radio.toggled.connect(self.update_current_settings)
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

    def on_apply(self):
        """Apply: update model only (no file write)."""
        self.apply_to_parent()
        if self.parent_window is not None:
            self.parent_window.statusBar().showMessage(
                "Classic CAN settings applied", 3000
            )

    def on_save(self):
        """Save this window's settings into the model only (not the config file)."""
        self.apply_to_parent()
        if self.parent_window is not None:
            self.parent_window.statusBar().showMessage(
                "Classic CAN settings saved", 3000
            )

    def on_cancel(self):
        """Cancel: discard form edits and reload last applied settings."""
        self.load_from_parent()
        if self.parent_window is not None:
            self.parent_window.statusBar().showMessage(
                "Classic CAN changes cancelled", 3000
            )

    def apply_to_parent(self):
        settings = self._collect_settings()
        if self.parent_window is not None:
            self.parent_window.classic_can_settings = dict(settings)
            self.parent_window.classic_can_enabled = settings["enabled"]

    def load_from_parent(self):
        if self.parent_window is None:
            return
        self.settings = dict(
            getattr(self.parent_window, "classic_can_settings", DEFAULT_CLASSIC_CAN)
        )
        self._restore_settings()
        if self.settings.get("enabled", False):
            self.enable_radio.setChecked(True)
        else:
            self.disable_radio.setChecked(True)
        self.update_current_settings()

    def set_theme(self, c):
        """Match light/dark colors used by Log Configuration."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                color: {c['text_primary']};
            }}
            QLabel {{
                color: {c['text_primary']};
                background: transparent;
            }}
            QRadioButton {{
                color: {c['text_primary']};
                background: transparent;
                spacing: 10px;
                padding: 4px 0;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 10px;
                border: 2px solid {c['border']};
                background-color: {c['bg_main']};
            }}
            QRadioButton::indicator:hover {{
                border: 2px solid {c['accent_blue']};
                background-color: {c['bg_main']};
            }}
            QRadioButton::indicator:checked {{
                border: 2px solid {c['accent_blue']};
                background-color: qradialgradient(
                    cx: 0.5, cy: 0.5, radius: 0.5,
                    fx: 0.5, fy: 0.5,
                    stop: 0 {c['accent_blue']},
                    stop: 0.40 {c['accent_blue']},
                    stop: 0.50 transparent,
                    stop: 1 transparent
                );
            }}
            QRadioButton::indicator:checked:hover {{
                border: 2px solid {c['accent_blue']};
                background-color: qradialgradient(
                    cx: 0.5, cy: 0.5, radius: 0.5,
                    fx: 0.5, fy: 0.5,
                    stop: 0 {c['accent_blue']},
                    stop: 0.40 {c['accent_blue']},
                    stop: 0.50 transparent,
                    stop: 1 transparent
                );
            }}
            QGroupBox {{
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: {RADIUS_SM}px;
                margin-top: 10px;
                padding-top: 8px;
                background-color: {c['bg_panel']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
                color: {c['text_primary']};
            }}
            QComboBox {{
                background-color: {c['bg_main']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: {RADIUS_SM}px;
                padding: 4px 6px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {c['bg_panel']};
                color: {c['text_primary']};
                selection-background-color: {c['accent_blue']};
                selection-color: #FFFFFF;
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
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
        """)
        self.enable_radio.set_colors(c)
        self.disable_radio.set_colors(c)

    