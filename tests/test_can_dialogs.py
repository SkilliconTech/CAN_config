from PySide6.QtWidgets import QWidget

from views.classic_can_dialog import ClassicCANSettingsDialog
from views.canfd_dialog import CANFDSettingsDialog


def test_classic_can_page_opens(qtbot):

    page = ClassicCANSettingsDialog()

    qtbot.addWidget(page)

    assert isinstance(page, QWidget)


def test_canfd_page_opens(qtbot):

    page = CANFDSettingsDialog()

    qtbot.addWidget(page)

    assert isinstance(page, QWidget)


def test_canfd_dialog_default_settings(qtbot):

    dialog = CANFDSettingsDialog()

    qtbot.addWidget(dialog)

    settings = dialog._collect_settings()

    assert settings["arbitration_bitrate"] == "500 kbits/s"
    assert settings["data_bitrate"] == "500 kbits/s"
    assert settings["enabled"] is False


def test_canfd_dialog_data_bitrate_change(qtbot):

    dialog = CANFDSettingsDialog()

    qtbot.addWidget(dialog)

    combo = dialog.data_bitrate_combo

    index = combo.findText("2000 kbits/s, 80.00%")

    assert index >= 0

    combo.setCurrentIndex(index)

    settings = dialog._collect_settings()

    assert settings["data_bitrate"] == "2000 kbits/s"