
CURRENT_CONFIG_VERSION = 1


def check_config_version(data):
    """
    Check whether a configuration file version is supported.
    """

    if not isinstance(data, dict):
        raise ValueError(
            "Configuration must be a JSON object."
        )

    version = data.get("version")

    if type(version) is not int:
        raise ValueError(
            "Configuration version must be an integer."
        )

    if version != CURRENT_CONFIG_VERSION:
        raise ValueError(
            f"Unsupported configuration version: {version}. "
            f"Supported version: {CURRENT_CONFIG_VERSION}."
        )

    return True
