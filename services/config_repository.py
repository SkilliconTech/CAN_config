from core.repository_interface import ConfigurationRepository
import json


def save_json(file_path, data):
    """
    Save a Python dictionary into a JSON file.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_json(file_path):
    """
    Read a JSON file and return its contents.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


class JsonConfigurationRepository(ConfigurationRepository):
    """
    Stores configuration data in JSON files.
    """

    def save(self, path, data):
        save_json(path, data)

    def load(self, path):
        return load_json(path)
