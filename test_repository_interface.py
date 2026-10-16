from core.repository_interface import ConfigurationRepository


class TestRepository(ConfigurationRepository):

    def __init__(self):
        self.data = None

    def save(self, path, data):
        self.data = data

    def load(self, path):
        return self.data


repository = TestRepository()

repository.save(
    "test",
    {"classic_can": {"bitrate": "500 kbits/s"}}
)

print(repository.load("test"))