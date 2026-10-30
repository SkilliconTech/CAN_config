from models.config_model import ConfigurationModel
from services.config_validator import (
    validate_log_config,
    validate_complete_config,
)
from core.repository_interface import ConfigurationRepository
from services.can_timing import normalize_shared_timing


class AppController:

    def __init__(self, repository: ConfigurationRepository):
        self.model = ConfigurationModel()
        self.repository = repository

    def save_configuration(self, path, data):
        validate_complete_config(data)

        self.repository.save(
            path,
            normalize_shared_timing(data),
        )

    def load_configuration(self, path):
        data = self.repository.load(path)

        validate_complete_config(data)

        return normalize_shared_timing(data)

    def update_bus_settings(self, classic, canfd):
        data = normalize_shared_timing({
            "classic_can": classic,
            "canfd": canfd,
        })

        self.model.set_classic_can(data["classic_can"])
        self.model.set_canfd(data["canfd"])

    def update_classic_can(self, settings):
        self.update_bus_settings(
            settings,
            self.model.get_canfd(),
        )

    def get_classic_can(self):
        return self.model.get_classic_can()

    def update_canfd(self, settings):
        self.update_bus_settings(
            self.model.get_classic_can(),
            settings,
        )

    def get_canfd(self):
        return self.model.get_canfd()

    def update_logging_config(self, settings):
        validate_log_config(settings)
        self.model.set_logging_config(settings)

    def get_logging_config(self):
        return self.model.get_logging_config()