"""Shell utilities."""
import subprocess
from subprocess import CompletedProcess
from typing import Any
from typing import IO
from typing import List
from typing import Optional
from typing import Union

from result import Err
from result import Ok
from result import Result

from .error import Error


STREAMTYPE = Union[None, int, IO[Any]]

PIPE = subprocess.PIPE

DEVNULL = subprocess.DEVNULL

STDOUT = subprocess.STDOUT


def execute(cmd: str, *, timeout: Optional[float] = None) -> Result[None, Error]:
    """Execute shell command, do not raise exceptions.

    The process' input is set to stdin, the output is set to stdout but is not captured.

    Args:
        cmd (str): shell command as a single string.
        timeout (Optional[float]): timeout in seconds (optional).

    Returns:
        Result[None, Error]:
            Ok(None): process successfully executed and returned 0.
            Err(kind=='CalledProcessError'): the process returned non-zero value.
            Err(kind=='TimeoutExpired'): timeout while waiting for a child process.
            Err(kind==...): other error(s) occurred.

    Example:
        >>> if execute("cd ..").is_err():
        >>>     ...  # process error
    """
    try:
        subprocess.check_call(cmd, shell=True, timeout=timeout)
        return Ok(None)
    except Exception as e:
        return Err(Error.from_exception(e))


def execute_split(
    args: List[str], *, timeout: Optional[float] = None
) -> Result[None, Error]:
    """Execute shell command with arguments that is a list of strings, do not raise exceptions.

    The process' output is invisible to the python code but
    visible from the console.

    Args:
        args (List[str]): shell command as a single string.
        timeout (Optional[float]): timeout in seconds (optional).

    Returns:
        Result[None, Error]:
            Ok(None): process successfully executed and returned 0.
            Err(kind=='FileNotFoundError'): executable not found.
            Err(kind=='CalledProcessError'): the process returned non-zero value.
            Err(kind=='TimeoutExpired'): timeout while waiting for a child process.
            Err(kind==...): other error(s) occurred.

    Example:
        >>> cmd = ["cd", ".."]
        >>> if execute_split(cmd).is_err():
        >>>     ...  # process error
    """
    try:
        subprocess.check_call(args, shell=False, timeout=timeout)
        return Ok(None)
    except Exception as e:
        return Err(Error.from_exception(e))


# https://stackoverflow.com/a/59313490/3824328 for type annotation of generic types
def execute_extended(
    cmd: str,
    *,
    timeout: Optional[float] = None,
    stdin: STREAMTYPE = PIPE,
    stdout: STREAMTYPE = PIPE,
    stderr: STREAMTYPE = PIPE,
) -> Result[CompletedProcess, Error]:  # type: ignore[type-arg]
    """Execute shell command, get the result as a `CompletedProcess` object, do not raise exceptions.

    The `CompletedProcess` object contains args, return code,
    stdout and stderr outputs.
    Note that when the sub-process exits with an error, this function still returns `Ok(CompletedProcess)`.
    IO streams: `DEVNULL` - no input or output,
    `PIPE` - IO stream that will be captured into the buffer
    if it is an output, or stdin if it is an input.

    Args:
        cmd (str): shell command as a single string.
        timeout (Optional[float]): timeout in seconds (optional).
        stdin (STREAMTYPE): one of (DEVNULL, PIPE, or output of another `CompletedProcess`).
        stdout (STREAMTYPE): one of (DEVNULL, PIPE).
        stderr (STREAMTYPE): one of (DEVNULL, PIPE or STDOUT to redirect stderr output to stdout).

    Returns:
        Result[CompletedProcess, Error]:
            Ok(CompletedProcess): the process is complete and the result available.
            Err(kind=='TimeoutExpired'): timeout while waiting for a child process.
            Err(kind==...): other error(s) occurred.

    Example:
        >>> if execute_extended("cd ..").is_err():
        >>>     ...  # process error
    """
    try:
        result = subprocess.run(
            cmd, shell=True, timeout=timeout, stdin=stdin, stdout=stdout, stderr=stderr
        )
        return Ok(result)
    except Exception as e:  # pragma: no cover
        return Err(Error.from_exception(e))  # pragma: no cover
