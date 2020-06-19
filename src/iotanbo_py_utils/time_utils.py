"""
Author: iotanbo
"""

import time


def utc_timestamp_millis():
    return int(round(time.time() * 1000))
