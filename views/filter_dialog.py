from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QDialogButtonBox,
    QMessageBox
)

from views.widget_helpers import (
    make_combo,
    select_data,
    make_spin,
    make_note
)

from services.config_validator import (
    validate_rule
)

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
