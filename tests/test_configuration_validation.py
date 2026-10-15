
import copy

import pytest

from models.config_model import default_log_config
from services.config_validator import (
    validate_log_config,
    parse_can_id
)


def test_default_logging_configuration_is_valid():
    settings = default_log_config()

    validate_log_config(settings)


def test_invalid_filter_mode_is_rejected():
    settings = default_log_config()

    settings["filters"]["mode"] = "invalid_mode"

    with pytest.raises(ValueError):
        validate_log_config(settings)


def test_invalid_logging_format_is_rejected():
    settings = default_log_config()

    settings["logging"]["formats"] = ["unknown"]

    with pytest.raises(ValueError):
        validate_log_config(settings)


def test_invalid_start_trigger_is_rejected():
    settings = default_log_config()

    settings["triggers"]["start"] = {
        "type": "unknown_trigger"
    }

    with pytest.raises(ValueError):
        validate_log_config(settings)


def test_valid_can_id():
    result = parse_can_id("0x123", False)

    assert result is not None


def test_invalid_can_id():
    with pytest.raises(ValueError):
        parse_can_id("INVALID", False)


def test_can_id_outside_standard_range():
    with pytest.raises(ValueError):
        parse_can_id("0x800", False)
