def require(ok, message):
    if not ok:
        raise ValueError(message)

def check_keys(obj, expected, label):
    require(isinstance(obj, dict) and set(obj) == set(expected.split()),
            f"{label}: expected fields: {expected}")
    
def check_int(value, low, high, label):
    require(type(value) is int and low <= value <= high,
            f"{label}: enter an integer from {low} to {high}")

def check_bool(value, label):
    require(type(value) is bool, f"{label}: expected true or false")


def parse_can_id(value, extended):
    require(isinstance(value, str) and value.lower().startswith("0x")
            and len(value) > 2
            and all(c in "0123456789abcdefABCDEF" for c in value[2:]),
            "Use hexadecimal identifiers or masks, for example 0x123")
    result = int(value, 16)
    require(result <= (0x1FFFFFFF if extended else 0x7FF),
            "Identifier/mask exceeds selected ID width")
    return result


def validate_rule(rule):
    require(isinstance(rule, dict), "Filter must be an object")
    kind = rule.get("type")
    require(kind in ("id_list", "id_range", "id_mask"), "Invalid filter type")
    extra = {
        "id_list": "ids",
        "id_range": "id_start id_end",
        "id_mask": "match_id mask",
    }[kind]
    check_keys(rule, "filter_id enabled type extended_id " + extra, "Filter")
    require(isinstance(rule["filter_id"], str)
            and 1 <= len(rule["filter_id"].strip()) <= 64,
            "Filter name must have 1-64 characters")
    check_bool(rule["enabled"], "Filter enabled")
    check_bool(rule["extended_id"], "Extended ID")
    ext = rule["extended_id"]
    if kind == "id_list":
        require(isinstance(rule["ids"], list) and 1 <= len(rule["ids"]) <= 256,
                "Enter 1-256 IDs")
        values = [parse_can_id(v, ext) for v in rule["ids"]]
        require(len(set(values)) == len(values), "Duplicate IDs in list")
    elif kind == "id_range":
        require(parse_can_id(rule["id_start"], ext)
                <= parse_can_id(rule["id_end"], ext),
                "Range start exceeds end")
    else:
        parse_can_id(rule["match_id"], ext)
        parse_can_id(rule["mask"], ext)
def validate_log_config(data):
    check_keys(data, "filters triggers logging", "Log configuration")

    # ---- filters ----
    filters = data["filters"]
    check_keys(filters, "mode combine rules", "Filters")
    require(filters["mode"] in ("all", "matching") and filters["combine"] == "or",
            "Invalid filter mode/combination")
    require(isinstance(filters["rules"], list) and len(filters["rules"]) <= 64,
            "Maximum 64 filters")
    names = set()
    for rule in filters["rules"]:
        validate_rule(rule)
        require(rule["filter_id"] not in names, "Duplicate filter name")
        names.add(rule["filter_id"])
    require(filters["mode"] != "matching"
            or any(r["enabled"] for r in filters["rules"]),
            "Matching mode needs at least one enabled filter")

    # ---- triggers ----
    triggers = data["triggers"]
    check_keys(triggers, "start stop rearm_after_stop", "Triggers")
    check_bool(triggers["rearm_after_stop"], "Rearm")
    for side, allowed in [("start", ("power_on", "can_id_match")),
                          ("stop", ("none", "can_id_match", "duration"))]:
        trigger = triggers[side]
        require(isinstance(trigger, dict) and trigger.get("type") in allowed,
                f"Invalid {side} trigger")
        kind = trigger["type"]
        check_keys(
            trigger,
            "type can_id extended_id" if kind == "can_id_match" else
            "type seconds" if kind == "duration" else "type",
            side,
        )
        if kind == "can_id_match":
            check_bool(trigger["extended_id"], "Trigger ID format")
            parse_can_id(trigger["can_id"], trigger["extended_id"])
        if kind == "duration":
            check_int(trigger["seconds"], 1, 604800, "Recording duration")
    start, stop = triggers["start"], triggers["stop"]
    require(not triggers["rearm_after_stop"]
            or (start["type"] == "can_id_match" and stop["type"] != "none"),
            "Rearm requires ID start and a configured stop")
    if start["type"] == stop["type"] == "can_id_match":
        require(
            (parse_can_id(start["can_id"], start["extended_id"]),
             start["extended_id"]) !=
            (parse_can_id(stop["can_id"], stop["extended_id"]),
             stop["extended_id"]),
            "Start and stop IDs must differ")

    # ---- log files ----
    log = data["logging"]
    check_keys(log, "formats file_split_size_bytes file_split_time_seconds "
                    "split_policy on_sd_full on_write_error overwrite_existing",
               "Logging")
    formats = log["formats"]
    require(isinstance(formats, list) and 1 <= len(formats) <= 2
            and all(isinstance(f, str) and f in ("asc", "mf4") for f in formats),
            "Select ASC and/or MF4")
    require(len(set(formats)) == len(formats), "Duplicate output format")
    check_int(log["file_split_size_bytes"], 1048576, 104857600, "File size limit")
    check_int(log["file_split_time_seconds"], 0, 3600, "File time limit")
    require(log["split_policy"] == "first_limit_reached", "Invalid split policy")
    require(log["on_sd_full"] == log["on_write_error"] == "stop",
            "Storage errors must stop logging")
    require(log["overwrite_existing"] is False,
            "Existing logs must not be overwritten")
    return data


def validate_complete_config(data):
    """
    Validate the overall configuration structure.
    """

    from services.config_version import check_config_version

    if not isinstance(data, dict):
        raise ValueError(
            "Configuration must be a JSON object."
        )

    check_config_version(data)

    if not isinstance(data.get("classic_can"), dict):
        raise ValueError(
            "Classic CAN settings are missing or invalid."
        )

    if "canfd" in data and not isinstance(data["canfd"], dict):
        raise ValueError(
            "CAN FD settings must be a JSON object."
        )

    from models.config_model import default_log_config

    log_data = default_log_config()

    for key in ("filters", "triggers", "logging"):
        if key in data:
            log_data[key] = data[key]

    validate_log_config(log_data)

    return True


