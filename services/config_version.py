CURRENT_CONFIG_VERSION = 2          # version written by the app
SUPPORTED_CONFIG_VERSIONS = (1, 2)  # versions the app can read


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

    if version not in SUPPORTED_CONFIG_VERSIONS:
        raise ValueError(
            f"Unsupported configuration version: {version}. "
            f"Supported versions: "
            f"{', '.join(str(v) for v in SUPPORTED_CONFIG_VERSIONS)}."
        )

    return True