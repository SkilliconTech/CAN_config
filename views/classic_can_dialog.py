from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QRadioButton,
    QComboBox,
    QPushButton,
    QMessageBox
)

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
        print(
          "Model Classic CAN:",
           self.parent_window.controller.get_classic_can()
        )