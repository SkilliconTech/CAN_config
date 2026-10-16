from app.controller import AppController
from services.config_repository import JsonConfigurationRepository

controller = AppController(
    repository=JsonConfigurationRepository()
)

print("Controller created successfully!")

print("Classic CAN:")
print(controller.model.classic_can)

print("CAN FD:")
print(controller.model.canfd)

controller.model.classic_can["bitrate"] = "250.000 kbits/s"

print("Updated bitrate:")
print(controller.model.classic_can["bitrate"])
print("\nLogging configuration:")

logging_settings = controller.get_logging_config()

print(logging_settings)

logging_settings["logging"]["formats"] = ["asc"]

controller.update_logging_config(logging_settings)

print("\nUpdated logging formats:")

print(
    controller.get_logging_config()["logging"]["formats"]
)