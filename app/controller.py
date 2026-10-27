from models.config_model import ConfigurationModel
from services.config_validator import (
    validate_log_config,
    validate_complete_config
)
from core.repository_interface import ConfigurationRepository
from services.config_version import check_config_version


class AppController:

    def __init__(self, repository: ConfigurationRepository):
        self.model = ConfigurationModel()
        self.repository = repository

    def save_configuration(self, path, data):
        """
        Validate configuration and save it to disk.
        """

        log_config = {
            key: data[key]
            for key in ("filters", "triggers", "logging")
        }

        validate_log_config(log_config)      
        self.repository.save(path, data)

       
    def load_configuration(self, path):
        data = self.repository.load(path)

        validate_complete_config(data)

        return data

    def update_classic_can(self, settings):
     self.model.set_classic_can(settings)


    def get_classic_can(self):
     return self.model.get_classic_can()
    
    def update_canfd(self, settings):
        self.model.set_canfd(settings)

    def get_canfd(self):
        return self.model.get_canfd()

    def update_logging_config(self, settings):
        """
        Validate and update logging settings.
        """
        validate_log_config(settings)

        self.model.set_logging_config(settings)

    def get_logging_config(self):
        """
        Retrieve logging settings.
        """
        return self.model.get_logging_config()
