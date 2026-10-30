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

# ---------------------------------------------------------------------------
# Two enabled filters must not match the same CAN identifier
# ---------------------------------------------------------------------------
def _rule_patterns(rule):
    """Turn a filter into ('m', match, mask) and ('r', start, end) pieces."""
    ext = rule["extended_id"]
    full = 0x1FFFFFFF if ext else 0x7FF
    kind = rule["type"]
    if kind == "id_list":
        return [("m", parse_can_id(v, ext), full) for v in rule["ids"]]
    if kind == "id_range":
        return [("r", parse_can_id(rule["id_start"], ext),
                      parse_can_id(rule["id_end"], ext))]
    return [("m", parse_can_id(rule["match_id"], ext),
                  parse_can_id(rule["mask"], ext))]


def _range_blocks(start, end):
    """Split [start, end] into aligned blocks (base, size)."""
    while start <= end:
        size = (start & -start) if start else 1 << 30
        while start + size - 1 > end:
            size >>= 1
        yield start, size
        start += size


def _patterns_overlap(p, q):
    if p[0] == "r" and q[0] == "r":
        return p[1] <= q[2] and q[1] <= p[2]
    if p[0] == "m" and q[0] == "m":
        return ((p[1] ^ q[1]) & p[2] & q[2]) == 0
    r, m = (p, q) if p[0] == "r" else (q, p)
    for base, size in _range_blocks(r[1], r[2]):
        if ((base ^ m[1]) & m[2] & ~(size - 1)) == 0:
            return True
    return False


def _rules_overlap(a, b):
    if a["extended_id"] != b["extended_id"]:
        return False
    pa, pb = _rule_patterns(a), _rule_patterns(b)
    if a["type"] == "id_list" and b["type"] == "id_list":
        return bool({p[1] for p in pa} & {q[1] for q in pb})
    return any(_patterns_overlap(p, q) for p in pa for q in pb)


def find_identifier_conflict(rules):
    """Names of the first two enabled filters sharing an identifier, or None."""
    active = [r for r in rules if r["enabled"]]
    for i, a in enumerate(active):
        for b in active[i + 1:]:
            if _rules_overlap(a, b):
                return a["filter_id"], b["filter_id"]
    return None


def find_conflict_with(rule, others):
    """Name of an enabled filter in 'others' that shares an identifier."""
    if not rule["enabled"]:
        return None
    for b in others:
        if b["enabled"] and _rules_overlap(rule, b):
            return b["filter_id"]
    return None

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

# ---------------------------------------------------------------------------
# CAN bus settings. These tables must match the dropdowns in the
# Classic CAN and CAN FD pages. If you change a dropdown, change it here too.
# Each bitrate maps to the sampling point(s) allowed with it.
# ---------------------------------------------------------------------------
CLASSIC_BITRATES = {
    "100.000 kbits/s": ("75%",),
    "125.000 kbits/s": ("75%",),
    "250.000 kbits/s": ("75%",),
    "500.000 kbits/s": ("75%",),
    "1.000 Mbits/s": ("75%",),
}
CLASSIC_SJW = ("1", "2", "3", "4")

# older files may contain "80.00%" for arbitration, so both are accepted
CANFD_ARBITRATION = {
    "500 kbits/s": ("80%", "80.00%"),
    "1000 kbits/s": ("80%", "80.00%"),
}
CANFD_DATA = {
    "500 kbits/s": ("80.00%",),
    "1000 kbits/s": ("80.00%",),
    "2000 kbits/s": ("80.00%",),
    "4000 kbits/s": ("80.00%",),
    "5000 kbits/s": ("75.00%",),
    "8000 kbits/s": ("80.00%",),
}
CANFD_SJW = tuple(str(i) for i in range(1, 17))


def _check_choice(settings, key, allowed, label):
    # a missing value is allowed: the app fills in the default
    if key not in settings:
        return
    value = settings[key]
    ok = (isinstance(value, (str, int)) and not isinstance(value, bool)
          and str(value) in allowed)
    require(ok, f"{label}: '{value}' is not valid. "
                f"Allowed values: {', '.join(allowed)}")


def _check_pair(settings, bitrate_key, sp_key, table, label):
    """Check a bitrate and its sampling point together."""
    if bitrate_key in settings:
        bitrate = settings[bitrate_key]
        require(isinstance(bitrate, str) and bitrate in table,
                f"{label} bitrate '{bitrate}' is not supported. "
                f"Allowed values: {', '.join(table)}")

    if sp_key in settings:
        sp = settings[sp_key]
        if bitrate_key in settings:
            allowed = table[settings[bitrate_key]]
        else:
            allowed = tuple({s for sps in table.values() for s in sps})
        require(isinstance(sp, str) and sp in allowed,
                f"{label} sampling point '{sp}' is not valid"
                f"{' for ' + str(settings[bitrate_key]) if bitrate_key in settings else ''}. "
                f"Allowed: {', '.join(allowed)}")


def validate_classic_can(settings):
    require(isinstance(settings, dict),
            "Classic CAN settings must be a JSON object.")
    _check_pair(settings, "bitrate", "sampling_point",
                CLASSIC_BITRATES, "Classic CAN")
    _check_choice(settings, "sjw", CLASSIC_SJW, "Classic CAN SJW")
    if "enabled" in settings:
        check_bool(settings["enabled"], "Classic CAN enabled")


def validate_canfd(settings):
    require(isinstance(settings, dict),
            "CAN FD settings must be a JSON object.")
    _check_pair(settings, "arbitration_bitrate", "arbitration_sp",
                CANFD_ARBITRATION, "CAN FD arbitration")
    _check_choice(settings, "arbitration_sjw", CANFD_SJW,
                  "CAN FD arbitration SJW")
    _check_pair(settings, "data_bitrate", "data_sp",
                CANFD_DATA, "CAN FD data")
    _check_choice(settings, "data_sjw", CANFD_SJW, "CAN FD data SJW")
    if "enabled" in settings:
        check_bool(settings["enabled"], "CAN FD enabled")

def validate_can_mode(classic, canfd):
    """The logger has one CAN channel: only one mode may be enabled."""
    classic_on = isinstance(classic, dict) and classic.get("enabled") is True
    fd_on = isinstance(canfd, dict) and canfd.get("enabled") is True
    require(
        not (classic_on and fd_on),
        "Classic CAN and CAN FD are both enabled. This logger has one CAN "
        "channel, so only one mode can be active. Set one of them to Disable."
    )

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

    # Both flags may be true: they select frame types to record.
    for key in ("classic_can", "canfd"):
        if key in data and "enabled" in data[key]:
            check_bool(
                data[key]["enabled"],
                f"{key} enabled",
            )

    from services.can_timing import normalize_shared_timing

    normalize_shared_timing(data)

    # NEW: reject incorrect CAN values
    validate_classic_can(data["classic_can"])
    if "canfd" in data:
        validate_canfd(data["canfd"])
    

    from models.config_model import default_log_config

    log_data = default_log_config()

    for key in ("filters", "triggers", "logging"):
        if key in data:
            log_data[key] = data[key]

    validate_log_config(log_data)

    return True