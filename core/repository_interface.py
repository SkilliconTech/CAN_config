
from abc import ABC, abstractmethod


class ConfigurationRepository(ABC):
    """
    Interface for saving and loading configurations.
    """

    @abstractmethod
    def save(self, path, data):
        """
        Save configuration data.
        """
        pass

    @abstractmethod
    def load(self, path):
        """
        Load and return configuration data.
        """
        pass
