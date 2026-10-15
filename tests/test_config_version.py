
import pytest

from services.config_version import check_config_version


def test_current_version_is_supported():
    assert check_config_version({"version": 1}) is True


def test_future_version_is_rejected():
    with pytest.raises(ValueError):
        check_config_version({"version": 2})


def test_missing_version_is_rejected():
    with pytest.raises(ValueError):
        check_config_version({})


def test_invalid_version_type_is_rejected():
    with pytest.raises(ValueError):
        check_config_version({"version": "1"})


def test_boolean_version_is_rejected():
    with pytest.raises(ValueError):
        check_config_version({"version": True})
