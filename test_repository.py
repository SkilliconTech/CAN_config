from services.config_repository import (
    save_json,
    load_json
)

# Example CAN configuration
config = {
    "bitrate": 500000,
    "enabled": True
}

# Save configuration
save_json("test_config.json", config)

# Read configuration
loaded_config = load_json("test_config.json")

print(loaded_config)