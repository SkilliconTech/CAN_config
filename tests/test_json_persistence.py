
import json

import pytest

from app.controller import AppController
from models.config_model import default_log_config
from models.constants import DEFAULT_CLASSIC_CAN, DEFAULT_CANFD
from services.config_repository import JsonConfigurationRepository


def make_test_config():
    return {
        "app": "CAN Configuration Tool",
        "version": 1,
        "classic_can": dict(DEFAULT_CLASSIC_CAN),
        "canfd": dict(DEFAULT_CANFD),
        **default_log_config()
    }


def test_save_creates_json_file(tmp_path):
    repository = JsonConfigurationRepository()
    controller = AppController(repository)

    path = tmp_path / "test.ccfg"
    data = make_test_config()

    controller.save_configuration(str(path), data)

    assert path.exists()


def test_save_and_load_preserves_data(tmp_path):
    repository = JsonConfigurationRepository()
    controller = AppController(repository)

    path = tmp_path / "test.ccfg"
    data = make_test_config()

    controller.save_configuration(str(path), data)
    loaded = controller.load_configuration(str(path))

    assert loaded == data


def test_saved_file_contains_valid_json(tmp_path):
    repository = JsonConfigurationRepository()
    controller = AppController(repository)

    path = tmp_path / "test.ccfg"

    controller.save_configuration(
        str(path),
        make_test_config()
    )

    with open(path, "r", encoding="utf-8") as file:
        saved = json.load(file)

    assert saved["app"] == "CAN Configuration Tool"
    assert saved["version"] == 1
    assert "classic_can" in saved
    assert "canfd" in saved
    assert "filters" in saved
    assert "triggers" in saved
    assert "logging" in saved


def test_loading_missing_file_raises_error(tmp_path):
    repository = JsonConfigurationRepository()
    controller = AppController(repository)

    path = tmp_path / "missing.ccfg"

    with pytest.raises(FileNotFoundError):
        controller.load_configuration(str(path))


def test_loading_corrupted_json_raises_error(tmp_path):
    repository = JsonConfigurationRepository()
    controller = AppController(repository)

    path = tmp_path / "corrupted.ccfg"
    path.write_text("{ invalid JSON !!!", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        controller.load_configuration(str(path))


def test_loading_non_dictionary_json_raises_error(tmp_path):
    repository = JsonConfigurationRepository()
    controller = AppController(repository)

    path = tmp_path / "invalid.ccfg"
    path.write_text('["not", "a", "configuration"]', encoding="utf-8")

    with pytest.raises(ValueError):
        controller.load_configuration(str(path))
