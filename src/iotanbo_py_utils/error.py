"""
Custom exceptions for iotanbo_py_utils
"""

from typing import Any

ErrorMsg = str
ResultTuple = (Any, ErrorMsg)


class IotanboError(Exception):
    """
    Generic error with an optional message, base class for
    other package-specific errors
    """
    pass
