"""
Author: iotanbo
"""

import time


def utc_timestamp_millis() -> int:
    """
    Generate UTC+0 timestamp in milliseconds.
    """
    return int(round(time.time() * 1000))
