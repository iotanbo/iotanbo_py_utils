"""Errors and exceptions used by the `iotanbo_py_utils` package."""
from dataclasses import dataclass
from typing import Type
from typing import TypeVar


class ErrorKind:
    """Errors that are translatable from/into Python's built-in exceptions.

    For more info about exceptions see
    https://docs.python.org/3/library/exceptions.html#exception-hierarchy.
    """

    BaseException = "BaseException"
    SystemExit = "SystemExit"
    KeyboardInterrupt = "KeyboardInterrupt"
    GeneratorExit = "GeneratorExit"
    Exception = "Exception"
    StopIteration = "StopIteration"
    StopAsyncIteration = "StopAsyncIteration"
    ArithmeticError = "ArithmeticError"
    FloatingPointError = "FloatingPointError"
    OverflowError = "OverflowError"
    ZeroDivisionError = "ZeroDivisionError"
    AssertionError = "AssertionError"
    AttributeError = "AttributeError"
    BufferError = "BufferError"
    EOFError = "EOFError"
    ImportError = "ImportError"
    ModuleNotFoundError = "ModuleNotFoundError"
    LookupError = "LookupError"
    IndexError = "IndexError"
    KeyError = "KeyError"
    MemoryError = "MemoryError"
    NameError = "NameError"
    UnboundLocalError = "UnboundLocalError"
    OSError = "OSError"
    BlockingIOError = "BlockingIOError"
    ChildProcessError = "ChildProcessError"
    ConnectionError = "ConnectionError"
    BrokenPipeError = "BrokenPipeError"
    ConnectionAbortedError = "ConnectionAbortedError"
    ConnectionRefusedError = "ConnectionRefusedError"
    ConnectionResetError = "ConnectionResetError"
    FileExistsError = "FileExistsError"
    FileNotFoundError = "FileNotFoundError"
    InterruptedError = "InterruptedError"
    IsADirectoryError = "IsADirectoryError"
    NotADirectoryError = "NotADirectoryError"
    PermissionError = "PermissionError"
    ProcessLookupError = "ProcessLookupError"
    TimeoutError = "TimeoutError"
    ReferenceError = "ReferenceError"
    RuntimeError = "RuntimeError"
    NotImplementedError = "NotImplementedError"
    RecursionError = "RecursionError"
    SyntaxError = "SyntaxError"
    IndentationError = "IndentationError"
    TabError = "TabError"
    SystemError = "SystemError"
    TypeError = "TypeError"
    ValueError = "ValueError"
    UnicodeError = "UnicodeError"
    UnicodeDecodeError = "UnicodeDecodeError"
    UnicodeEncodeError = "UnicodeEncodeError"
    UnicodeTranslateError = "UnicodeTranslateError"
    Warning = "Warning"
    DeprecationWarning = "DeprecationWarning"
    PendingDeprecationWarning = "PendingDeprecationWarning"
    RuntimeWarning = "RuntimeWarning"
    SyntaxWarning = "SyntaxWarning"
    UserWarning = "UserWarning"
    FutureWarning = "FutureWarning"
    ImportWarning = "ImportWarning"
    UnicodeWarning = "UnicodeWarning"
    BytesWarning = "BytesWarning"
    ResourceWarning = "ResourceWarning"


_ArithmeticError_group = {
    "ArithmeticError",
    "FloatingPointError",
    "OverflowError",
    "ZeroDivisionError",
}

_ImportError_group = {"ImportError", "ModuleNotFoundError"}


_LookupError_group = {"LookupError", "IndexError", "KeyError"}


_NameError_group = {"NameError", "UnboundLocalError"}


_OSError_group = {
    "OSError",
    "BlockingIOError",
    "ChildProcessError",
    "ConnectionError",
    "BrokenPipeError",
    "ConnectionAbortedError",
    "ConnectionRefusedError",
    "ConnectionResetError",
    "FileExistsError",
    "FileNotFoundError",
    "InterruptedError",
    "IsADirectoryError",
    "NotADirectoryError",
    "PermissionError",
    "ProcessLookupError",
    "TimeoutError",
}

_RuntimeError_group = {"RuntimeError", "NotImplementedError", "RecursionError"}

_SyntaxError_group = {"SyntaxError", "IndentationError", "TabError"}

_ValueError_group = {
    "ValueError",
    "UnicodeError",
    "UnicodeDecodeError",
    "UnicodeEncodeError",
    "UnicodeTranslateError",
}

_Warning_group = {
    "Warning",
    "DeprecationWarning",
    "PendingDeprecationWarning",
    "RuntimeWarning",
    "SyntaxWarning",
    "UserWarning",
    "FutureWarning",
    "ImportWarning",
    "UnicodeWarning",
    "BytesWarning",
    "ResourceWarning",
}


# Type of variable that can be either 'Error' or one of its subclasses.
ErrorType = TypeVar("ErrorType", bound="Error")
# Type of variable that can be either 'Exception' or one of its subclasses.
AnyException = TypeVar("AnyException", bound="Exception")


@dataclass
class Error:
    """An error object."""

    kind: str
    msg: str
    cause: str

    def __init__(self, kind: str, msg: str = "", *, cause: str = ""):
        """Create a new Error object.

        Args:
            kind (str): defines error kind, one of `iotanbo_py_utils.error.ErrorKind` or custom error kind.
            msg (str): error description. Defaults to "".
            cause (str): the cause of this error (another error or exception). Defaults to "".
        """
        self.kind = kind
        self.msg = msg
        self.cause = cause

    @classmethod
    def from_exception(
        cls: Type[ErrorType], e: AnyException, *, new_kind: str = ""
    ) -> ErrorType:
        """Create an Error object from the specified exception.

        If `new_kind` specified, its value will be assigned to the error's `kind`,
        and the exception's name will be assigned to `cause`.

        If `new_kind` not specified, the exception's name will be assigned
        to `kind`, and the `cause` will be left empty.

        Args:
            e (AnyException): an arbitrary exception that is a subclass of `Exception`.
            new_kind (str): error kind to replace the exception's name if required;
                it may be one of `iotanbo_py_utils.error.ErrorKind` or custom string.

        Returns:
            ErrorType (Error): a brand new Error object that is the best match for the specified exception.
        """
        exception_name = f"{e.__class__.__name__}"
        msg = str(e)
        if not new_kind:
            return cls(exception_name, msg, cause="")
        return cls(new_kind, msg, cause=exception_name)

    def kind_is(self, kind: str) -> bool:
        """Check if the error kind equals to certain value.

        Args:
            kind (str): kind as a sting,
                one of `iotanbo_py_utils.error.ErrorKind` or custom.

        Returns:
            bool: True if kinds match, False otherwise.

        Example:
            >>> e = Error(ErrorKind.ValueError)
            >>> assert e.kind_is(ErrorKind.ValueError)
        """
        return self.kind == kind

    def one_of_arithmetic_errors(self) -> bool:
        """Returns True if the error is an `ArithmeticError` or one of its subtypes."""
        return self.kind in _ArithmeticError_group

    def one_of_import_errors(self) -> bool:
        """Returns True if the error is an `ImportError` or one of its subtypes."""
        return self.kind in _ImportError_group

    def one_of_lookup_errors(self) -> bool:
        """Returns True if the error is a `LookupError` or one of its subtypes."""
        return self.kind in _LookupError_group

    def one_of_name_errors(self) -> bool:
        """Returns True if the error is a `NameError` or one of its subtypes."""
        return self.kind in _NameError_group

    def one_of_os_errors(self) -> bool:
        """Returns True if the error is an `OSError` or one of its subtypes."""
        return self.kind in _OSError_group

    def one_of_runtime_errors(self) -> bool:
        """Returns True if the error is a `RuntimeError` or one of its subtypes."""
        return self.kind in _RuntimeError_group

    def one_of_syntax_errors(self) -> bool:
        """Returns True if the error is a `SyntaxError` or one of its subtypes."""
        return self.kind in _SyntaxError_group

    def one_of_value_errors(self) -> bool:
        """Returns True if the error is a `ValueError` or one of its subtypes."""
        return self.kind in _ValueError_group

    def one_of_warnings(self) -> bool:
        """Returns True if the error is a `Warning` or one of its subtypes."""
        return self.kind in _Warning_group
