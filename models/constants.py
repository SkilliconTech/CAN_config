# Default Classic CAN settings
DEFAULT_CLASSIC_CAN = {
    "bitrate": "100.000 kbits/s",
    "sampling_point": "75%",
    "sjw": "1",
    "enabled": False,
}

# Default CAN FD settings
DEFAULT_CANFD = {
    "arbitration_bitrate": "500 kbits/s",
    "arbitration_sp": "80.00%",
    "arbitration_sjw": "1",
    "data_bitrate": "500 kbits/s",
    "data_sp": "80.00%",
    "data_sjw": "1",
    "enabled": False,
}

# Configuration file extensions
PROJECT_EXT = ".ccfg"

PROJECT_FILTER = "Config files (*.ccfg);;All files (*)"

JSON_FILTER = "JSON files (*.json);;All files (*)"

LOG_PAGES = {
    "Filters": "filters",
    "Triggers": "triggers",
    "Log Files": "logfiles",
    "JSON Preview": "preview",
}