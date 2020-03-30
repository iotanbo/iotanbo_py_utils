"""
Custom exceptions for iotanbo_py_utils
"""

ErrorMsg = str


class IotanboError(Exception):
    """
    Generic error with an optional message, base class for
    other package-specific errors
    """
    pass
