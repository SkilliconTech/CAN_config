import copy

from models.constants import (
    DEFAULT_CLASSIC_CAN,
    DEFAULT_CANFD
)
def default_log_config():
    return {
        "filters": {"mode": "all", "combine": "or", "rules": []},
        "triggers": {
            "start": {"type": "power_on"},
            "stop": {"type": "none"},
            "rearm_after_stop": False,
        },
        "logging": {
            "formats": ["asc", "mf4"],
            "file_split_size_bytes": 104857600,
            "file_split_time_seconds": 1800,
            "split_policy": "first_limit_reached",
            "on_sd_full": "stop",
            "on_write_error": "stop",
            "overwrite_existing": False,
        },
    }

class ConfigurationModel:
    """
    Stores the CAN Configuration Tool settings.
    """

    def __init__(self):

        self.classic_can = copy.deepcopy(
            DEFAULT_CLASSIC_CAN
        )

        self.canfd = copy.deepcopy(
            DEFAULT_CANFD
        )

        self.logging = default_log_config()

    def reset(self):
        """
        Restore all settings to defaults.
        """
        self.__init__()

    def get_configuration(self):
        """
        Return a copy of all settings.
        """
        return {
            "classic_can": copy.deepcopy(
                self.classic_can
            ),
            "canfd": copy.deepcopy(
                self.canfd
            ),
            "logging_config": copy.deepcopy(
                self.logging
            )
        }
    def set_classic_can(self, settings):
     """
     Update Classic CAN settings.
     """
     self.classic_can = copy.deepcopy(settings)


    def get_classic_can(self):
     """
     Return a copy of Classic CAN settings.
     """
     return copy.deepcopy(self.classic_can)

    def set_canfd(self, settings):
        """
        Update CAN FD settings.
        """
        self.canfd = copy.deepcopy(settings)

    def get_canfd(self):
        """
        Return a copy of CAN FD settings.
        """
        return copy.deepcopy(self.canfd)
    
    def set_logging_config(self, settings):
        """
        Store logging configuration.
        """
        self.logging = copy.deepcopy(settings)

    def get_logging_config(self):
        """
        Return a copy of logging configuration.
        """
        return copy.deepcopy(self.logging)
