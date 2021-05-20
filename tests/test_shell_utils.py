"""Tests for shell_utils.py."""
from iotanbo_py_utils import shell_utils as sh


def test_execute() -> None:
    # Ok(None) when command is valid
    assert sh.execute("echo HELLO").is_ok()  # this should be OK on all platforms

    # CalledProcessError when process returned non-zero result
    assert sh.execute("bad_cmd").unwrap_err().kind == "CalledProcessError"


def test_execute_split() -> None:
    cmd = ["echo", "HELLO"]
    # unsuccessfull_cmd = ["exit", "-1"]
    not_existing_cmd = ["bad_cmd"]
    # Ok(None) when command is valid
    assert sh.execute_split(cmd).is_ok()  # this should be OK on all platforms

    # CalledProcessError when process returned non-zero result
    # assert sh.execute_split(unsuccessfull_cmd).unwrap_err().kind == "CalledProcessError"

    # FileNotFoundError when executable not found
    assert sh.execute_split(not_existing_cmd).unwrap_err().kind == "FileNotFoundError"


def test_execute_extended() -> None:
    # Ok(CompletedProcess) when command is valid
    result = sh.execute_extended("echo HELLO!")
    cmd_result = result.unwrap()
    assert cmd_result.returncode == 0
    assert not cmd_result.stderr
    assert not cmd_result.stdout == "HELLO!".encode()

    # Ok(CompletedProcess) when process returned non-zero result
    result = sh.execute_extended("bad_cmd")
    cmd_result = result.unwrap()
    assert cmd_result.returncode != 0
    assert cmd_result.stderr
    assert not cmd_result.stdout
