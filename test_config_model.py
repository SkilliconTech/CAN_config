from models.config_model import ConfigurationModel

config = ConfigurationModel()

print("Classic CAN:")
print(config.classic_can)

print("\nCAN FD:")
print(config.canfd)

print("\nLogging:")
print(config.logging)

config.classic_can["bitrate"] = "250.000 kbits/s"

print("\nModified bitrate:")
print(config.classic_can["bitrate"])

config.reset()

print("\nAfter reset:")
print(config.classic_can["bitrate"])