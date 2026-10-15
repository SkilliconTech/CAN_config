from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QComboBox,
    QRadioButton,
    QPushButton
)
from models.constants import DEFAULT_CANFD
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
            self.parent_window.canfd_settings = (
                self._collect_settings()
            )

        self.accept()

