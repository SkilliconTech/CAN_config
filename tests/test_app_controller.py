
import copy

import pytest

from app.controller import AppController
from core.repository_interface import ConfigurationRepository
from models.config_model import default_log_config


class FakeRepository(ConfigurationRepository):
    """
    A fake storage system used only for testing.
    """

    def __init__(self):
        self.storage = {}

    def save(self, path, data):
        self.storage[path] = copy.deepcopy(data)

    def load(self, path):
        if path not in self.storage:
            raise FileNotFoundError(path)

        return copy.deepcopy(self.storage[path])


def make_valid_config():
    """
    Create valid test configuration data.
    """
    log_config = default_log_config()

    return {
        "app": "CAN Configuration Tool",
        "version": 1,
        "classic_can": {
            "bitrate": "500.000 kbits/s",
            "sampling_point": "75%",
            "sjw": "1",
            "enabled": True
        },
        "canfd": {
            "arbitration_bitrate": "500 kbits/s",
            "arbitration_sp": "80%",
            "arbitration_sjw": "1",
            "data_bitrate": "2000 kbits/s",
            "data_sp": "80.00%",
            "data_sjw": "1",
            "enabled": False
        },
        **log_config
    }


def test_controller_saves_configuration():
    repository = FakeRepository()
    controller = AppController(repository)

    data = make_valid_config()

    controller.save_configuration("test.ccfg", data)

    assert repository.load("test.ccfg") == data


def test_controller_loads_configuration():
    repository = FakeRepository()
    controller = AppController(repository)

    data = make_valid_config()
    repository.save("test.ccfg", data)

    loaded = controller.load_configuration("test.ccfg")

    assert loaded == data


def test_controller_reports_missing_file():
    repository = FakeRepository()
    controller = AppController(repository)

    with pytest.raises(FileNotFoundError):
        controller.load_configuration("missing.ccfg")


def test_controller_rejects_invalid_json_structure():
    repository = FakeRepository()
    controller = AppController(repository)

    repository.save("invalid.ccfg", ["not", "a", "dictionary"])

    with pytest.raises(ValueError):
        controller.load_configuration("invalid.ccfg")


def test_controller_updates_classic_can():
    repository = FakeRepository()
    controller = AppController(repository)

    settings = controller.get_classic_can()
    settings["bitrate"] = "250.000 kbits/s"

    controller.update_classic_can(settings)

    assert (
        controller.get_classic_can()["bitrate"]
        == "250.000 kbits/s"
    )


def test_controller_updates_canfd():
    repository = FakeRepository()
    controller = AppController(repository)

    settings = controller.get_canfd()
    settings["data_bitrate"] = "2000 kbits/s"

    controller.update_canfd(settings)

    assert (
        controller.get_canfd()["data_bitrate"]
        == "2000 kbits/s"
    )


def test_controller_updates_logging():
    repository = FakeRepository()
    controller = AppController(repository)

    settings = controller.get_logging_config()
    settings["logging"]["formats"] = ["asc"]

    controller.update_logging_config(settings)

    assert (
        controller.get_logging_config()["logging"]["formats"]
        == ["asc"]
    )
