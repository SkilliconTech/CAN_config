
import copy

import pytest

from models.config_model import default_log_config
from models.constants import DEFAULT_CLASSIC_CAN, DEFAULT_CANFD
from services.config_validator import validate_complete_config


def make_valid_config():
    return {
        "app": "CAN Configuration Tool",
        "version": 1,
        "classic_can": copy.deepcopy(DEFAULT_CLASSIC_CAN),
        "canfd": copy.deepcopy(DEFAULT_CANFD),
        **default_log_config()
    }


def test_complete_valid_configuration():
    assert validate_complete_config(make_valid_config()) is True


def test_missing_classic_can():
    config = make_valid_config()
    del config["classic_can"]

    with pytest.raises(ValueError):
        validate_complete_config(config)


def test_invalid_canfd_structure():
    config = make_valid_config()
    config["canfd"] = "invalid"

    with pytest.raises(ValueError):
        validate_complete_config(config)


def test_unsupported_version():
    config = make_valid_config()
    config["version"] = 99

    with pytest.raises(ValueError):
        validate_complete_config(config)


def test_missing_optional_canfd():
    config = make_valid_config()
    del config["canfd"]

    assert validate_complete_config(config) is True
