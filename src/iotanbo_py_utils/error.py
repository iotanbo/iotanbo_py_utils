"""
Custom exceptions for iotanbo_py_utils
"""

from typing import Any

# Error message type alias
ErrorMsg = str

"""
ResultTuple allows returning both result and error message from a function without raising exceptions.
How it works:
* The result of function execution is returned as the first element of the tuple.
* The error message is returned as the second element of the tuple.
* If ErrorMsg is an empty string, then there is no error.
"""
ResultTuple = (Any, ErrorMsg)

# Indexes of elements inside the ResultTuple
VAL = 0  # value is the first element
ERR = 1  # error message is the second element


class IotanboError(Exception):
    """
    Generic error with an optional message, base class for
    other package-specific errors
    """
    pass
