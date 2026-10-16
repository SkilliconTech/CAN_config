from PySide6.QtCore import Signal
import json
import copy

from PySide6.QtWidgets import (
    QStackedWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHeaderView,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QPlainTextEdit,
    QLabel,
    QComboBox,
    QSpinBox,
    QMessageBox,
    QDialog
)
from models.config_model import default_log_config

from views.widget_helpers import (
    make_combo,
    select_data,
    make_spin,
    make_note
)

from views.filter_dialog import FilterDialog

from services.config_validator import (
    validate_log_config
)

from resources.theme import RADIUS_SM
from PySide6.QtGui import QFont

class LogConfigWidget(QStackedWidget):
    configuration_changed = Signal()
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

        # Notify when logging controls change
        for combo in (self.filter_mode, self.start, self.stop):
            combo.currentIndexChanged.connect(
                self.notify_configuration_changed
            )

        for checkbox in (
            self.start_ext,
            self.stop_ext,
            self.rearm,
            self.asc,
            self.mf4
        ):
            checkbox.toggled.connect(
                self.notify_configuration_changed
            )

        for field in (self.start_id, self.stop_id):
            field.textChanged.connect(
                self.notify_configuration_changed
            )

        for spinbox in (
            self.duration,
            self.size_limit,
            self.time_limit
        ):
            spinbox.valueChanged.connect(
                self.notify_configuration_changed
            )

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
    
    def notify_configuration_changed(self):
        self.configuration_changed.emit()
        
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
                self.notify_configuration_changed()

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
        row = self.table.currentRow()

        if row < 0:
            return

        name = self.rules[row]["filter_id"]

        answer = QMessageBox.question(
            self.window(),
            "Remove filter",
            f"Do you want to remove the filter '{name}'?\n\n"
            "This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        del self.rules[row]
        self.refresh_table()
        self.notify_configuration_changed()

    def remove_all(self):
        if not self.rules:
            return

        answer = QMessageBox.warning(
            self.window(),
            "Remove all filters",
            f"Do you want to remove all {len(self.rules)} filter(s)?\n\n"
            "This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        self.rules.clear()
        self.refresh_table()
        self.notify_configuration_changed()

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
