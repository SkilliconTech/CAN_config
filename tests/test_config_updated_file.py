import json
from pathlib import Path

from services.config_validator import validate_complete_config
from services.config_version import CURRENT_CONFIG_VERSION

ROOT = Path(__file__).resolve().parent.parent


def test_config_updated_json_is_valid():
    data = json.loads((ROOT / "config_updated.json").read_text(encoding="utf-8"))
    assert data["version"] == CURRENT_CONFIG_VERSION == 2
    assert validate_complete_config(data) is True