"""Platform utilities."""
import sys


def is_linux() -> bool:  # pragma: no cover
    return sys.platform == "linux"  # pragma: no cover


def is_macos() -> bool:  # pragma: no cover
    return sys.platform == "darwin"  # pragma: no cover


def is_windows() -> bool:  # pragma: no cover
    return sys.platform == "win32"  # pragma: no cover
