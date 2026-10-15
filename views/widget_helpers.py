from PySide6.QtWidgets import (
    QComboBox,
    QSpinBox,
    QLabel
)
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