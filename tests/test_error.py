"""Test `iotanbo_py_utils.error.py`."""
from iotanbo_py_utils.error import Error
from iotanbo_py_utils.error import ErrorKind


def test_error_one_of_arithmetic_errors() -> None:
    errs = (
        Error(ErrorKind.ArithmeticError),
        Error(ErrorKind.FloatingPointError),
        Error(ErrorKind.OverflowError),
        Error(ErrorKind.ZeroDivisionError),
    )
    for err in errs:
        assert err.one_of_arithmetic_errors()

    # == negative path ==
    err = Error(ErrorKind.ValueError)
    assert not err.one_of_arithmetic_errors()


def test_error_one_of_import_errors() -> None:
    errs = (
        Error(ErrorKind.ImportError),
        Error(ErrorKind.ModuleNotFoundError),
    )
    for err in errs:
        assert err.one_of_import_errors()

    # == negative path ==
    err = Error(ErrorKind.ValueError)
    assert not err.one_of_import_errors()


def test_error_one_of_lookup_errors() -> None:
    errs = (
        Error(ErrorKind.LookupError),
        Error(ErrorKind.IndexError),
        Error(ErrorKind.KeyError),
    )
    for err in errs:
        assert err.one_of_lookup_errors()

    # == negative path ==
    err = Error(ErrorKind.ValueError)
    assert not err.one_of_lookup_errors()


def test_error_one_of_name_errors() -> None:
    errs = (
        Error(ErrorKind.NameError),
        Error(ErrorKind.UnboundLocalError),
    )
    for err in errs:
        assert err.one_of_name_errors()

    # == negative path ==
    err = Error(ErrorKind.ValueError)
    assert not err.one_of_name_errors()


def test_error_one_of_os_errors() -> None:
    errs = (
        Error(ErrorKind.OSError),
        Error(ErrorKind.BlockingIOError),
        Error(ErrorKind.ChildProcessError),
        Error(ErrorKind.ConnectionError),
        Error(ErrorKind.BrokenPipeError),
        Error(ErrorKind.ConnectionAbortedError),
        Error(ErrorKind.ConnectionRefusedError),
        Error(ErrorKind.ConnectionResetError),
        Error(ErrorKind.FileExistsError),
        Error(ErrorKind.FileNotFoundError),
        Error(ErrorKind.InterruptedError),
        Error(ErrorKind.IsADirectoryError),
        Error(ErrorKind.NotADirectoryError),
        Error(ErrorKind.PermissionError),
        Error(ErrorKind.ProcessLookupError),
        Error(ErrorKind.TimeoutError),
    )
    for err in errs:
        assert err.one_of_os_errors()

    # == negative path ==
    err = Error(ErrorKind.ValueError)
    assert not err.one_of_os_errors()


def test_error_one_of_runtime_errors() -> None:
    errs = (
        Error(ErrorKind.RuntimeError),
        Error(ErrorKind.NotImplementedError),
        Error(ErrorKind.RecursionError),
    )
    for err in errs:
        assert err.one_of_runtime_errors()

    # == negative path ==
    err = Error(ErrorKind.ValueError)
    assert not err.one_of_runtime_errors()


def test_error_one_of_syntax_errors() -> None:
    errs = (
        Error(ErrorKind.SyntaxError),
        Error(ErrorKind.IndentationError),
        Error(ErrorKind.TabError),
    )
    for err in errs:
        assert err.one_of_syntax_errors()

    # == negative path ==
    err = Error(ErrorKind.ValueError)
    assert not err.one_of_syntax_errors()


def test_error_one_of_value_errors() -> None:
    errs = (
        Error(ErrorKind.ValueError),
        Error(ErrorKind.UnicodeError),
        Error(ErrorKind.UnicodeDecodeError),
        Error(ErrorKind.UnicodeEncodeError),
        Error(ErrorKind.UnicodeTranslateError),
    )
    for err in errs:
        assert err.one_of_value_errors()

    # == negative path ==
    err = Error(ErrorKind.SyntaxError)
    assert not err.one_of_value_errors()


def test_error_one_of_warnings() -> None:
    errs = (
        Error(ErrorKind.Warning),
        Error(ErrorKind.DeprecationWarning),
        Error(ErrorKind.PendingDeprecationWarning),
        Error(ErrorKind.RuntimeWarning),
        Error(ErrorKind.SyntaxWarning),
        Error(ErrorKind.UserWarning),
        Error(ErrorKind.FutureWarning),
        Error(ErrorKind.ImportWarning),
        Error(ErrorKind.UnicodeWarning),
        Error(ErrorKind.BytesWarning),
        Error(ErrorKind.ResourceWarning),
    )
    for err in errs:
        assert err.one_of_warnings()

    # == negative path ==
    err = Error(ErrorKind.ValueError)
    assert not err.one_of_warnings()


class _CustomException(Exception):
    ...


def test_error_from_exception() -> None:
    # error from exception, preserve kind
    e = Error.from_exception(ValueError("test"))
    assert e.kind == ErrorKind.ValueError
    assert not e.cause
    assert e.msg == "test"

    # new kind replaces exception's kind
    e = Error.from_exception(ValueError("test"), new_kind=ErrorKind.Warning)
    assert e.kind == ErrorKind.Warning
    assert e.cause == ErrorKind.ValueError
    assert e.msg == "test"

    # error from custom exception, preserve kind
    try:
        raise _CustomException()
    except _CustomException as ex:
        e = Error.from_exception(ex)
        assert e.kind == "_CustomException"
        assert not e.cause
        assert e.msg == ""
