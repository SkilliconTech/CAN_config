
import os
import tempfile

from core.repository_interface import ConfigurationRepository
from services.config_repository import JsonConfigurationRepository


repository = JsonConfigurationRepository()

assert isinstance(repository, ConfigurationRepository)

test_data = {
    "app": "CAN Configuration Tool",
    "version": 1,
    "classic_can": {
        "bitrate": "500 kbits/s",
        "enabled": True
    }
}

# Create a temporary file for testing.
with tempfile.TemporaryDirectory() as folder:
    path = os.path.join(folder, "test_config.json")

    repository.save(path, test_data)

    loaded_data = repository.load(path)

    assert loaded_data == test_data

print("JSON Repository test passed!")
