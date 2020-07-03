"""
Custom exceptions for iotanbo_py_utils
"""

from typing import Any

ErrorMsg = str
"""
Type alias indicating that the string is an error message.
"""


ResultTuple = (Any, ErrorMsg)
"""
First element of ResultTuple is actual result, second is an error message.
Empty ErrorMsg indicates no error.
"""

# # Indexes of elements inside the ResultTuple
# VAL = 0  # value is the first element
# ERR = 1  # error message is the second element


class IotanboError(Exception):
    """
    Error specific to 'iotanbo_py_utils'.
    """
    pass


class WebSvcError:
    """
    Common web service errors as strings up to 16 bytes long.
    """

    LENGTH_ERROR = 'LENGTH_ERROR'
    """
    Entity length out of range.
    """

    EMPTY_ERROR = 'EMPTY_ERROR'
    """
    Entity is empty while not supposed to be so.
    """

    CLOSED = 'CLOSED'
    """
    Connection or handler is closed either normally or due to an error.
    """

    PING = 'PING'
    """
    'PING' msg received instead of data (not an error in most cases).
    """

    PONG = 'PONG'
    """
    'PONG' msg received instead of data (not an error in most cases).
    """

    WS_SEND_ERROR = 'WS_SEND_ERROR'
    """
    Error while sending data via Websocket.
    """

    WS_CONN_ERROR = 'WS_CONN_ERROR'
    """
    Websocket connection error.
    """

    NONCE_ERROR = 'NONCE_ERROR'

    AUTHEN_ERROR = 'AUTHEN_ERROR'
    """
    Authentication error.
    """
    PERMISS_ERROR = 'PERMISS_ERROR'
    """
    Permission error.
    """

    SERVER_ERROR = 'SERVER_ERROR'
    """
    Generic server error.
    """

    NOT_EXISTS = 'NOT_EXISTS'
    WRITE_ERROR = 'WRITE_ERROR'
    UNKNOWN_CMD = 'UNKNOWN_CMD'
    CMD_FMT_ERROR = 'CMD_FMT_ERROR'
    DATABASE_ERROR = 'DATABASE_ERROR'
    FILEEX_LEN_ERR = 'FILEEX_LEN_ERR'
    """
    File extension is too long.
    """
