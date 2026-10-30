"""Shared nominal timing for Classic CAN and CAN FD."""

import copy

from models.constants import DEFAULT_CANFD


def normalize_shared_timing(data):
    result = copy.deepcopy(data)

    classic = result.get("classic_can", {})
    fd = result.get("canfd", {})

    # Separate timing is preserved unless both frame types are enabled.
    if not (
        classic.get("enabled") is True
        and fd.get("enabled") is True
    ):
        return result

    nominal = {**DEFAULT_CANFD, **fd}

    bitrates = {
        "500 kbits/s": "500.000 kbits/s",
        "1000 kbits/s": "1.000 Mbits/s",
    }

    bitrate = nominal["arbitration_bitrate"]
    sample_point = nominal["arbitration_sp"]
    sjw = nominal["arbitration_sjw"]

    if not isinstance(bitrate, str) or bitrate not in bitrates:
        raise ValueError(
            "Combined mode requires FD arbitration "
            "at 500 or 1000 kbits/s."
        )

    if sample_point not in ("80%", "80.00%"):
        raise ValueError(
            "Combined mode requires an FD arbitration "
            "sample point of 80%."
        )

    if (
        isinstance(sjw, bool)
        or not isinstance(sjw, (str, int))
        or str(sjw) not in {str(i) for i in range(1, 17)}
    ):
        raise ValueError(
            "Combined mode requires an FD arbitration "
            "SJW from 1 to 16."
        )

    return result