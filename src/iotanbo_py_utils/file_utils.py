"""File utilities."""
import hashlib
import os
import shutil
import sys
import tarfile
import zlib
from typing import List
from typing import Optional

from pathvalidate import validate_filepath  # type: ignore[attr-defined]
from result import Err
from result import Ok
from result import Result

from .error import Error
from .error import ErrorKind


def is_path_valid_ne(path: str, os_family: str = "") -> bool:
    """Check if the path is (grammatically) valid for the specified platform.

    This does not actually perform check for path existence or possibility
    of its creation.

    Args:
        path (str): path to file or directory.
        os_family (str): OS family name, one of ("", "windows", "linux", "macos").

    Returns:
        `True` if path is valid, `False` otherwise.
    """
    if not os_family:
        if sys.platform == "win32":  # pragma: no cover
            os_family = "windows"  # pragma: no cover
        elif sys.platform == "linux":  # pragma: no cover
            os_family = "linux"  # pragma: no cover
        elif sys.platform == "darwin":  # pragma: no cover
            os_family = "macos"  # pragma: no cover
    try:
        validate_filepath(path, platform=os_family)
        return True
    except Exception:
        return False


def get_item_type_ne(path: str) -> Result[str, Error]:
    """Get the type of a file system item without raising exceptions.

    Args:
        path (str): path to a file system item.

    Returns:
        Result[str, Error]:
             Ok (str):  if item exists: 'file', 'dir, 'symlink' or 'other'.
             Err (kind == `FileNotFoundError`): if item not exists.
             Err (kind == `PermissionError`): wrong permissions.
             Err (kind == `...`): if other error(s) occurred.
    """
    try:
        # Check if item exists first
        if not os.path.exists(path):
            return Err(Error(ErrorKind.FileNotFoundError))

        # Check if symlink with specified pathname exists;
        # this check must go first because symlink is also a file
        item_type = "other"
        try:
            if os.path.islink(path):
                item_type = "symlink"
        except Exception as e:  # pragma: no cover
            # Corresponds to any kind of errors and is hard
            # to be automatically tested.
            return Err(Error.from_exception(e))  # pragma: no cover
        # Check if dir with specified pathname exists;
        if item_type == "other":
            try:
                if os.path.isdir(path):
                    item_type = "dir"
                else:  # if item exists and it is not a symlink or dir, then it is file
                    item_type = "file"
            # any kind of errors that may occur
            # while executing os.path.isdir(path)
            except Exception as e:  # pragma: no cover
                return Err(Error.from_exception(e))  # pragma: no cover
    # any kind of errors that may occur
    # while executing os.path.exists(path)
    except Exception as e:  # pragma: no cover
        return Err(Error.from_exception(e))  # pragma: no cover
    return Ok(item_type)


def _item_exists_ne(path: str, item_type: str) -> Result[bool, Error]:
    """Check if file, directory or symlink exist without raising exceptions.

    Args:
        path (str): path to the item.
        item_type (str): one of ('file', 'dir', 'symlink').

    Returns:
        Result[bool, Error]:
             Ok (True):  item of specified type exists.
             Ok (False): item does not exist.
             Err (kind == `TypeError`): item exists but has different type.
             Err (kind == `PermissionError`): wrong permissions.
             Err (kind == `...`): other error(s) occurred.
    """
    result = get_item_type_ne(path)
    if result.is_err():
        err = result.unwrap_err()
        if ErrorKind.FileNotFoundError == err.kind:
            return Ok(False)
        else:
            # other errors while getting fs item type
            return Err(err)  # pragma: no cover
    existing_items_type = result.unwrap()
    if existing_items_type == item_type:
        # item exists and is of correct type
        return Ok(True)
    # item exists but has a different type
    return Err(Error(ErrorKind.TypeError, existing_items_type))


def create_path_ne(path: str, *, overwrite: bool = False) -> Result[None, Error]:
    """Create a path (series of directories) without raising exceptions.

    Args:
        path (str): path to a new directory.
        overwrite (bool): silently overwrite directory if it exists.

    Returns:
        Result[None, Error]:
            Ok (None): path successfully created.
            Err (kind == `FileExistsError`): directory already exists and `overwrite` is `False`.
            Err (kind == `TypeError`): item exists but is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    try:
        result = dir_exists_ne(path)
        if result.is_err():
            # unexpected error while checking for file existence
            return Err(result.unwrap_err())
        else:
            exists = result.unwrap()
            if exists:
                if not overwrite:
                    return Err(Error(ErrorKind.FileExistsError))
                else:
                    # remove existing directory and its contents
                    shutil.rmtree(path)
        os.makedirs(path)
    except PermissionError as e:  # pragma: no cover
        # This is covered on linux only
        return Err(Error.from_exception(e))  # pragma: no cover
    except Exception as e:
        if sys.platform == "darwin":
            # on macOS, OSError is raised instead of PermissionError
            # This is covered on macOS only
            if e.__class__.__name__ == 'OSError':  # pragma: no cover
                return Err(Error.from_exception(e, new_kind=ErrorKind.PermissionError))  # pragma: no cover
        return Err(Error.from_exception(e))  # pragma: no cover
    return Ok(None)


def create_symlink_ne(
    src: str,
    dest: str,
    *,
    overwrite: bool = False,
) -> Result[None, Error]:
    """Create a symlink with name `dest` to `src` without raising exceptions.

    Args:
        src (str): path to source.
        dest (str): path to symlink file.
        overwrite (bool): silently overwrite if it exists.

    Returns:
        Result[None, Error]:
            Ok (None): symlink successfully created.
            Err (kind == `ValueError`): src or dest is invalid path and
            `validate_paths=True`.
            Err (kind == `FileExistsError`): dest symlink already exists and `overwrite=False`.
            Err (kind == `FileNotFoundError`): src does not exist and
            `validate_paths=True`.
            Err (kind == `TypeError`): dest exists but is not a symlink.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    # `src` must be validated because otherwise
    # system silently creates a valid symlink to invalid fs item
    if not is_path_valid_ne(src):
        return Err(Error(ErrorKind.FileNotFoundError, f"src path '{src}' is invalid"))
    if not is_path_valid_ne(dest):
        return Err(Error(ErrorKind.FileNotFoundError, f"dest path '{dest}' is invalid"))
    try:
        # check src for existence and validity
        msg_prefix = "(src error) "
        result = get_item_type_ne(src)
        if result.is_err():
            # unexpected error while checking for src existence
            error = result.unwrap_err()
            error.msg = msg_prefix + error.msg
            return Err(error)

        # check dest for existence and validity
        msg_prefix = "(dest error) "
        result = symlink_exists_ne(dest)  # type: ignore[assignment]
        if result.is_err():
            # unexpected error while checking for dest existence
            error = result.unwrap_err()  # pragma: no cover
            error.msg = msg_prefix + error.msg  # pragma: no cover
            return Err(error)  # pragma: no cover
        else:
            dest_exists = result.unwrap()
            if dest_exists:
                if not overwrite:
                    error = Error(ErrorKind.FileExistsError)
                    error.msg = msg_prefix + error.msg
                    return Err(error)
                else:
                    # remove dest symlink
                    os.unlink(dest)
        os.symlink(src, dest)
    except Exception as e:  # pragma: no cover
        # Covered on linux only
        return Err(Error.from_exception(e))  # pragma: no cover
    return Ok(None)


def _common_validation_before_write_file(
    path: str, overwrite: bool
) -> Result[None, Error]:
    # check for file existence
    result = file_exists_ne(path)
    if result.is_err():
        # error while checking for file existence
        return Err(result.unwrap_err())
    else:
        if result.unwrap():
            # file exists
            if not overwrite:
                return Err(Error(ErrorKind.FileExistsError))
    return Ok(None)


def write_file_ne(
    path: str,
    contents: str = "",
    encoding: str = "utf-8",
    *,
    overwrite: bool = False,
    newline: str = "\n",
) -> Result[None, Error]:
    """Create a new text file and write contents into it without raising exceptions.

    Args:
        path (str): path to file.
        contents (str): string to be written into file.
        encoding (str): text file encoding ("utf-8" default).
        overwrite (bool): rewrite file if it already exists.
        newline (str): new line separator.

    Returns:
        Result[None, Error]:
            Ok (None): file written/rewritten successfully.
            Err (kind == `FileExistsError`): file already exists and
            `overwrite` is `False`.
            Err (kind == `TypeError`): path is not a file.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.

    Example:
        >>> import tempfile
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        >>>     if write_file_ne(os.path.join(tmpdir,"test.txt"), "test").is_err():
        >>>      ...  # process error
    """
    validation_result = _common_validation_before_write_file(path, overwrite)
    if validation_result.is_err():
        return Err(validation_result.unwrap_err())
    try:
        with open(path, "w", encoding=encoding, newline=newline) as f:
            f.write(contents)
        return Ok(None)
    except Exception as e:
        return Err(Error.from_exception(e))


def write_binary_file_ne(
    path: str,
    contents: bytes,
    *,
    overwrite: bool = False,
) -> Result[None, Error]:
    """Create and write data to binary file.

    Args:
        path (str): path to file.
        contents (bytes): file contents.
        overwrite (bool): rewrite file if it already exists.

    Returns:
        Result[None, Error]:
            Ok (None): file written/overwritten successfully.
            Err (kind == `FileExistsError`): file already exists and
            `overwrite` is `False`.
            Err (kind == `TypeError`): path is not a file.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    validation_result = _common_validation_before_write_file(path, overwrite)
    if validation_result.is_err():
        return Err(validation_result.unwrap_err())
    try:
        with open(path, "w+b") as f:
            f.write(contents)
        return Ok(None)
    except Exception as e:  # pragma: no cover
        return Err(Error.from_exception(e))  # pragma: no cover


def _common_validation_before_read_file(path: str) -> Result[None, Error]:
    result = file_exists_ne(path)
    if result.is_err():
        # other errors like file is a directory etc.
        return Err(result.unwrap_err())  # pragma: no cover
    file_exists = result.unwrap()
    if not file_exists:
        return Err(Error(ErrorKind.FileNotFoundError))
    return Ok(None)


def read_file_ne(path: str, encoding: str = "utf-8") -> Result[str, Error]:
    r"""Read a text file without raising exceptions.

    Universal new line separation mode is used, that means any of (`\r`, `\r\n`)
    will be replaced with `\n`.

    Args:
        path (str): path to file.
        encoding (str): text file encoding ("utf-8" default).

    Returns:
        Result[str, Error]:
            Ok (str): file contents.
            Err (Error.kind == FileNotFoundError`): file does not exist.
            Err (kind == `PermissionError`): wrong permissions.
            Err (Error.kind == `...`): other error(s) occurred.

    Example:
        >>> contents = read_file_ne("test.txt")
        >>> if contents.is_err():
        >>>     ...  # process error
        >>> else:
        >>>     contents = contents.unwrap()
    """
    validation = _common_validation_before_read_file(path)
    if validation.is_err():
        return Err(validation.unwrap_err())
    try:
        with open(file=path, mode="r", encoding=encoding) as f:
            return Ok(f.read())
    except Exception as e:  # pragma: no cover
        # it's hard to automate a test
        # where a file can't be read from file system
        return Err(Error.from_exception(e))  # pragma: no cover


def read_binary_file_ne(path: str) -> Result[bytes, Error]:
    """Read a binary file without raising exceptions.

    Args:
        path: path to file.

    Returns:
        Result[bytes, Error]:
            Ok (bytes): file contents.
            Err (Error.kind == FileNotFoundError`): file does not exist.
            Err (kind == `PermissionError`): wrong permissions.
            Err (Error.kind == `...`): other error(s) occurred.
    """
    validation = _common_validation_before_read_file(path)
    if validation.is_err():
        return Err(validation.unwrap_err())
    try:
        with open(file=path, mode="rb") as f:
            return Ok(f.read())
    except Exception as e:  # pragma: no cover
        # it's hard to automate a test
        # where a file can't be read from file system
        return Err(Error.from_exception(e))  # pragma: no cover


def read_file_into_lines_ne(
    path: str, encoding: str = "utf-8"
) -> Result[List[str], Error]:
    r"""Read text file into a list of strings separated by `sep`.

    Universal new line separation mode is used, that means any of (`\n`, `\r`, `\r\n`)
    will be interpreted as line separator.

    Args:
        path: path to file.
        encoding: text file encoding ("utf-8" default).

    Returns:
        Result[List[str], Error]:
            Ok (List[str]): file contents as a list of lines.
            Err (Error.kind == FileNotFoundError`): file does not exist.
            Err (kind == `PermissionError`): wrong permissions.
            Err (Error.kind == `...`): other error(s) occurred.
    """
    result = read_file_ne(path, encoding)
    if result.is_err():
        return Err(result.unwrap_err())
    contents = result.unwrap()
    if not contents:
        # file is empty
        return Ok([""])
    return Ok(contents.split(sep="\n"))


def file_exists_ne(path: str) -> Result[bool, Error]:
    """Check if file exists without raising exceptions.

    Args:
        path (str): path to file.

    Returns:
        Result[bool, Error]:
            Ok (True): file exists.
            Ok (False): file does not exist.
            Err (kind == `TypeError`): item exists but has different type.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.

    Example:
        >>> if file_exists_ne("/path/to/file.txt").expect(
        >>>     "Unexpected error while checking for file existence"
        >>> ):
        >>>     ...  # do something if file exists.

    """
    return _item_exists_ne(path, "file")


def dir_exists_ne(path: str) -> Result[bool, Error]:
    """Check if dir exists without raising exceptions.

    Args:
        path (str): path to directory.

    Returns:
        Result[bool, Error]:
            Ok (True): directory exists.
            Ok (False): directory does not exist.
            Err (kind == `TypeError`): item exists but has different type.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    return _item_exists_ne(path, "dir")


def symlink_exists_ne(path: str) -> Result[bool, Error]:
    """Check if symlink exists without raising exceptions.

    Args:
        path (str): path to symlink.

    Returns:
        Result[bool, Error]:
            Ok (True): symlink exists.
            Ok (False): symlink does not exist.
            Err (kind == `TypeError`): item exists but has different type.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    return _item_exists_ne(path, "symlink")


def remove_file_ne(
    path: str, *, fail_if_not_exists: bool = False
) -> Result[None, Error]:
    """Remove file without raising exceptions.

    Args:
        path (str): path to file.
        fail_if_not_exists (bool): if True, return Error if file not exists.

    Returns:
        Result[None, Error]:
            Ok (None): file successfully removed, or
            does not exist and `fail_if_not_exists` is `False`.
            Err (kind == `FileNotFoundError`): file does not exist and
            `fail_if_not_exists` is `True`.
            Err (kind == `TypeError`): item exists but is not a file.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    result = file_exists_ne(path)
    if result.is_err():
        # unexpected error while checking for file existence
        return Err(result.unwrap_err())
    if not result.unwrap():
        # file does not exist
        if not fail_if_not_exists:
            return Ok(None)
        return Err(Error(ErrorKind.FileNotFoundError))
    try:
        os.remove(path)
    except Exception as e:  # pragma: no cover
        # it's hard to automate a test
        # where a file can't be deleted from file system
        return Err(Error.from_exception(e))  # pragma: no cover
    return Ok(None)


def remove_dir_ne(
    path: str, *, fail_if_not_exists: bool = False
) -> Result[None, Error]:
    """Remove directory and its contents without raising exceptions.

    Args:
        path (str): path to directory.
        fail_if_not_exists (bool): if True, return Error if directory not exists.

    Returns:
        Result[None, Error]:
            Ok (None): directory successfully removed, or
            directory does not exist and `fail_if_not_exists` is `False`.
            Err (kind == `FileNotFoundError`): directory does not exist and
            `fail_if_not_exists` is `True`.
            Err (kind == `TypeError`): item exists but is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    result = dir_exists_ne(path)
    if result.is_err():
        # unexpected error while checking for directory existence
        return Err(result.unwrap_err())
    if not result.unwrap():
        # directory does not exist
        if not fail_if_not_exists:
            return Ok(None)
        return Err(Error(ErrorKind.FileNotFoundError))
    try:
        shutil.rmtree(path)
    except Exception as e:  # pragma: no cover
        # it's hard to automate a test
        # where a directory can't be deleted from file system
        return Err(Error.from_exception(e))  # pragma: no cover
    return Ok(None)


def remove_symlink_ne(
    path: str, *, fail_if_not_exists: bool = False
) -> Result[None, Error]:
    """Remove symlink from the file system without raising exceptions.

    Args:
        path (str): path to symlink.
        fail_if_not_exists (bool): if True, return Error if symlink not exists.

    Returns:
        Result[None, Error]:
            Ok (None): existing symlink successfully removed.
            Err (kind == `FileNotFoundError`): symlink does not exist and
            `fail_if_not_exists` is `True`.
            Err (kind == `TypeError`): path is not a symlink.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): if other error(s) occurred.
    """
    result = symlink_exists_ne(path)
    if result.is_err():
        # errors like path is a file
        return Err(result.unwrap_err())  # pragma: no cover
    symlink_exists = result.unwrap()
    if not symlink_exists:
        if fail_if_not_exists:
            return Err(Error(ErrorKind.FileNotFoundError))
        else:
            return Ok(None)
    try:
        os.unlink(path)
    except Exception as e:  # pragma: no cover
        # it's hard to automate a test
        # where a symlink can't be deleted from file system
        return Err(Error.from_exception(e))  # pragma: no cover
    return Ok(None)


def ensure_parent_dir_exists(path: str) -> Result[None, Error]:
    """Ensure that the parent directory of the specified item exists. Create it if it does not.

    Args:
        path (str): path to a file system item (file, directory or symlink).

    Returns:
        Result[None, Error]:
            Ok (None): parent directory exists.
            Err (kind == `FileNotFoundError`): path does not exist.
            Err (kind == `TypeError`): parent item exists but is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    if not is_path_valid_ne(path):
        return Err(Error(ErrorKind.FileNotFoundError))
    head, _ = os.path.split(path)
    result = dir_exists_ne(head)
    if result.is_err():
        # error while trying to figure out if parent dir exists
        return Err(result.unwrap_err())
    if result.unwrap():
        # parent dir already exists
        return Ok(None)
    return create_path_ne(head)


def remove_dir_contents_ne(path: str) -> Result[None, Error]:
    """Remove all directory contents without rising exceptions.

    Args:
        path (str): path to a directory.

    Returns:
        Result[None, Error]:
            Ok (None): contents removed.
            Err (kind == `FileNotFoundError`): path does not exist.
            Err (kind == `TypeError`): path is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    try:
        with os.scandir(path) as it:
            for item_name in it:
                item_path = os.path.join(path, item_name)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):  # pragma:  no cover
                        shutil.rmtree(item_path)
                except Exception as e:  # pragma:  no cover
                    # Permissions error and other
                    return Err(Error.from_exception(e))  # pragma:  no cover
            return Ok(None)
    except Exception as e:
        return Err(Error.from_exception(e))


def dir_empty_ne(path: str) -> Result[bool, Error]:
    """Check if directory is empty, do not raise exceptions.

    Args:
        path (str): path to a directory.

    Returns:
        Result[bool, Error]:
            Ok (True): directory is empty.
            Ok (False): directory is not empty.
            Err (kind == `FileNotFoundError`): path does not exist.
            Err (kind == `TypeError`): path is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    try:
        if any(os.scandir(path)):
            return Ok(False)
        return Ok(True)
    except NotADirectoryError:
        return Err(Error(ErrorKind.TypeError, cause="NotADirectoryError"))
    except Exception as e:  # pragma:  no cover
        # Permissions error and other
        return Err(Error.from_exception(e))  # pragma:  no cover


def _pre_copy_and_move_file_operations(
    src: str, dest: str, *, overwrite: bool
) -> Result[None, Error]:
    result = file_exists_ne(src)
    if result.is_err():
        return Err(result.unwrap_err())
    src_exists = result.unwrap()
    if not src_exists:
        return Err(Error(ErrorKind.FileNotFoundError, "source file does not exist"))

    de_result = file_exists_ne(dest)
    if de_result.is_err():
        return Err(de_result.unwrap_err())
    dest_exists = de_result.unwrap()
    if dest_exists:
        if not overwrite:
            return Err(Error(ErrorKind.FileExistsError, "destination already exists"))
        rm_result = remove_file_ne(dest)
        if rm_result.is_err():
            return Err(rm_result.unwrap_err())  # pragma: no cover
    return Ok(None)


def copy_file_ne(
    src: str, dest: str, *, overwrite: bool = False
) -> Result[None, Error]:
    """Copy file without exceptions.

    Args:
        src (str): source file.
        dest (str): destination file.
        overwrite (bool): silently overwrite destination if exists.

    Returns:
        Result[None, Error]:
        Ok (None): operation successful.
        Err (kind == `FileNotFoundError`): src does not exist.
        Err (kind == `FileExistsError`): destination file already exists and `overwrite=False`.
        Err (kind == `TypeError`): src or dest is not a file.
        Err (kind == `PermissionError`): wrong permissions.
        Err (kind == `...`): other error(s) occurred.
    """
    pre_result = _pre_copy_and_move_file_operations(src, dest, overwrite=overwrite)
    if pre_result.is_err():
        return pre_result
    try:
        shutil.copy(src, dest)
    except Exception as e:
        return Err(Error.from_exception(e))
    return Ok(None)


def move_file_ne(
    src: str, dest: str, *, overwrite: bool = False
) -> Result[None, Error]:
    """Move file without exceptions.

    Args:
        src (str): source file.
        dest (str): destination file.
        overwrite (bool): silently overwrite destination if exists.

    Returns:
        Result[None, Error]:
            Ok (None): operation successful.
            Err (kind == `FileNotFoundError`): src does not exist.
            Err (kind == `FileExistsError`): destination file already exists
            and `overwrite=False`.
            Err (kind == `TypeError`): src or dest is not a file.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    pre_result = _pre_copy_and_move_file_operations(src, dest, overwrite=overwrite)
    if pre_result.is_err():
        return pre_result
    try:
        shutil.move(src, dest)
    except Exception as e:  # pragma: no cover
        # permission errors etc.
        return Err(Error.from_exception(e))  # pragma: no cover
    return Ok(None)


def _pre_copy_and_move_tree_operations(
    src: str, dest: str, *, overwrite: bool
) -> Result[None, Error]:
    result = dir_exists_ne(src)
    if result.is_err():
        return Err(result.unwrap_err())
    src_exists = result.unwrap()
    if not src_exists:
        return Err(Error(ErrorKind.FileNotFoundError, "source dir does not exist"))

    de_result = dir_exists_ne(dest)
    if de_result.is_err():
        return Err(de_result.unwrap_err())
    dest_exists = de_result.unwrap()
    if dest_exists:
        if not overwrite:
            return Err(
                Error(ErrorKind.FileExistsError, "destination dir already exists")
            )
        rm_result = remove_dir_ne(dest)
        if rm_result.is_err():
            return rm_result  # pragma: no cover
    return Ok(None)


def copy_tree_ne(
    src: str,
    dest: str,
    *,
    overwrite: bool = False,
    symlinks: bool = True,
    ignore_dangling_symlinks: bool = True,
) -> Result[None, Error]:
    """Copy a directory tree without exceptions.

    Args:
        src (str): source directory.
        dest (str): destination directory.
        overwrite (bool): silently overwrite destination if exists.
        symlinks (bool): copy symlinks, not files or directories they are pointing to.
        ignore_dangling_symlinks (bool): do not fail if a symlink is invalid.

    Returns:
        Result[None, Error]:
            Ok (None): operation successful.
            Err (kind == `FileNotFoundError`): src does not exist.
            Err (kind == `FileExistsError`): destination directory already exists and `overwrite=False`.
            Err (kind == `TypeError`): src or dest is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    pre_result = _pre_copy_and_move_tree_operations(src, dest, overwrite=overwrite)
    if pre_result.is_err():
        return pre_result
    try:
        shutil.copytree(
            src,
            dest,
            symlinks=symlinks,
            ignore_dangling_symlinks=ignore_dangling_symlinks,
        )
    except Exception as e:  # pragma: no cover
        # errors while executing shutil.copytree
        return Err(Error.from_exception(e))  # pragma: no cover
    return Ok(None)


def move_tree_ne(
    src: str, dest: str, *, overwrite: bool = False
) -> Result[None, Error]:
    """Move a directory tree without exceptions.

    Note: all synlinks are moved without modification, that means
    if the moved symlink targets any of moved files or directories using absolute path,
    it becomes broken.

    Args:
        src (str): source directory.
        dest (str): destination directory.
        overwrite (bool): silently overwrite destination if exists.

    Returns:
        Result[None, Error]:
            Ok (None): operation successful.
            Err (kind == `FileNotFoundError`): src does not exist.
            Err (kind == `FileExistsError`): destination directory    already exists and `overwrite=False`.
            Err (kind == `TypeError`): src or dest is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    pre_result = _pre_copy_and_move_tree_operations(src, dest, overwrite=overwrite)
    if pre_result.is_err():
        return pre_result
    try:
        shutil.move(src, dest)
    except Exception as e:  # pragma: no cover
        # errors while executing shutil.copytree
        return Err(Error.from_exception(e))  # pragma: no cover
    return Ok(None)


def _dir_validation(path: str) -> Result[None, Error]:
    result = dir_exists_ne(path)
    if result.is_err():
        return Err(result.unwrap_err())
    path_exists = result.unwrap()
    if not path_exists:
        return Err(
            Error(ErrorKind.FileNotFoundError, f"directory '{path}' does not exist")
        )
    return Ok(None)


def get_subdir_list_ne(path: str, *, sort: bool = True) -> Result[List[str], Error]:
    """Get the list of the first-level sub-directories that the directory contains.

    Args:
        path (str): path to a directory.
        sort (bool): sort the list alphabetically.

    Returns:
        Result[List[str], Error]:
            Ok (List[str]): operation successful.
            Err (kind == `FileNotFoundError`): path does not exist.
            Err (kind == `TypeError`): path is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    validation = _dir_validation(path)
    if validation.is_err():
        return Err(validation.unwrap_err())
    # https://stackoverflow.com/questions/973473/getting-a-list-of-all-subdirectories-in-the-current-directory
    try:
        subdirs = [subdir.name for subdir in os.scandir(path) if subdir.is_dir()]
        if sort:
            return Ok(sorted(subdirs))
        return Ok(subdirs)
    except Exception as e:  # pragma: no cover
        # error while doing file system operations
        return Err(Error.from_exception(e))  # pragma: no cover


def get_subdir_list_recursively_ne(
    path: str, *, sort: bool = True, ignore_list: Optional[List[str]] = None
) -> Result[List[str], Error]:
    """Get the list of all sub-directories that the directory contains.

    Args:
        path (str): path to a directory.
        sort (bool): sort the list alphabetically.
        ignore_list (Optional[List[str]]): sub-directories to be excluded
        from the recursive search.
        each string must be a relative path without starting `.`.

    Returns:
        Result[List[str], Error]:
            Ok (List[str]): operation successful.
            Err (kind == `FileNotFoundError`): path does not exist.
            Err (kind == `TypeError`): path is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.

    Example:
        >>> ignore = ["dir-to-ignore", os.path.join("other-dir", "sub-subdir")]
        >>> result = get_subdir_list_recursively_ne("some-dir", ignore_list=ignore)
        >>> if result.is_ok():
        >>>     subdirs = result.unwrap()
    """
    validation = _dir_validation(path)
    if validation.is_err():
        return Err(validation.unwrap_err())

    if ignore_list is None:
        ignore_list = []
    root_path = path
    root_path_len = len(root_path)
    result = []
    try:
        for path, _, _ in os.walk(root_path):  # path, dirs, files
            relative_path = path[root_path_len + 1 :]
            if not relative_path:  # do not add empty paths
                continue

            ignored = False
            # Check if path is in the ignore_list
            for ignored_path in ignore_list:
                if not ignored_path:  # do not include empty strings
                    continue
                if relative_path.startswith(ignored_path):
                    ignored = True
                    break
            if not ignored:
                # Append path without base_path part to the list
                result.append(relative_path)
    except Exception as e:  # pragma: no cover
        # permissions and other system errors
        return Err(Error.from_exception(e))  # pragma: no cover
    if sort:
        return Ok(sorted(result))
    return Ok(result)


def get_file_list_ne(path: str, *, sort: bool = True) -> Result[List[str], Error]:
    """Get the list of files in the directory, no exceptions.

    Files inside sub-directories are not included. The list is sorted by default.
    The result contains list of relative paths without starting dot.

    Args:
        path (str): path to a directory.
        sort (bool): sort the list alphabetically.

    Returns:
        Result[List[str], Error]:
            Ok (List[str]): operation successful.
            Err (kind == `FileNotFoundError`): path does not exist.
            Err (kind == `TypeError`): path is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    validation = _dir_validation(path)
    if validation.is_err():  # pragma: no cover
        # scenario already covered in previous test
        return Err(validation.unwrap_err())  # pragma: no cover
    try:
        file_list = [file.name for file in os.scandir(path) if file.is_file()]
        if sort:
            return Ok(sorted(file_list))
        return Ok(file_list)
    except Exception as e:  # pragma: no cover
        # error while doing file system operations
        return Err(Error.from_exception(e))  # pragma: no cover


def get_file_list_recursively_ne(
    path: str, *, sort: bool = True, ignore_list: Optional[List[str]] = None
) -> Result[List[str], Error]:
    """Get the list of files and symlinks that the directory contains.

    This includes the files in the nested sub-directories,
    directories are not included.
    The result is a list of relative paths without starting dot.

    Args:
        path (str): path to a directory.
        sort (bool): sort the result list alphabetically.
        ignore_list (Optional[List[str]]): files and sub-directories
        to be excluded from the result and recursive search.
        each string must be a relative path without starting `.`.

    Returns:
        Result[List[str], Error]:
            Ok (List[str]): operation successful.
            Err (kind == `FileNotFoundError`): path does not exist.
            Err (kind == `TypeError`): path is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.

    Example:
        >>> ignore = ["dir-to-ignore", os.path.join("other-dir", "file-to-ignore")]
        >>> result = get_file_list_recursively_ne("some-dir", ignore_list=ignore)
        >>> if result.is_ok():
        >>>     file_list = result.unwrap()
    """
    validation = _dir_validation(path)
    if validation.is_err():
        return Err(validation.unwrap_err())

    if ignore_list is None:
        ignore_list = []

    # Get list of all sub-directories
    get_subdirs_result = get_subdir_list_recursively_ne(path, ignore_list=ignore_list)
    if get_subdirs_result.is_err():
        return Err(get_subdirs_result.unwrap_err())  # pragma: no cover
    dirs = get_subdirs_result.unwrap()
    dirs.append("")  # add root directory to the list

    # search each directory for files and add them into common list
    file_list = []
    for d in dirs:
        d_path = os.path.join(path, d)
        get_files_result = get_file_list_ne(d_path, sort=False)
        if get_files_result.is_err():
            return Err(get_files_result.unwrap_err())  # pragma: no cover
        local_file_list = get_files_result.unwrap()
        for f in local_file_list:
            if d:
                relative_file_path = os.path.join(d, f)
            else:
                relative_file_path = f
            if relative_file_path not in ignore_list:
                file_list.append(relative_file_path)
    if sort:
        return Ok(sorted(file_list))
    return Ok(file_list)


def get_aggregated_file_list_ne(
    base: str,
    subdirs: List[str],
    *,
    sort: bool = True,
    ignore_list: Optional[List[str]] = None,
) -> Result[List[str], Error]:
    """Get the list of all files of the `base` directory and the `subdirs`.

    The result contains list of relative paths to the files without starting dot.
    Symlinks are included into the result.
    This is same as `get_file_list_recursively_ne()` but is cheaper
    to use if you already have the list of the subdirs.

    Args:
        base (str): path to the base directory.
        subdirs (List[str]): relative paths to sub-directories.
        sort (bool): sort the result list alphabetically.
        ignore_list (Optional[List[str]]): files and sub-directories
        to be excluded from the result and recursive search.
        each string must be a relative path without starting `.`.

    Returns:
        Result[List[str], Error]:
            Ok (List[str]): operation successful.
            Err (kind == `FileNotFoundError`): path does not exist.
            Err (kind == `TypeError`): path is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.

    Example:
        >>> ignore = ["dir-to-ignore", os.path.join("other-dir", "file-to-ignore")]
        >>> subdirs = ["sub-1", "sub-2"]
        >>> result = get_aggregated_file_list_ne("base-dir", subdirs, ignore_list=ignore)
        >>> if result.is_ok():
        >>>     file_list = result.unwrap()
    """
    validation = _dir_validation(base)
    if validation.is_err():
        return Err(validation.unwrap_err())

    if ignore_list is None:
        ignore_list = []

    if "" not in subdirs:
        subdirs.append("")  # add base directory to the list

    # search each directory for files and add them into common list
    file_list = []
    for d in subdirs:
        d_path = os.path.join(base, d)
        get_files_result = get_file_list_ne(d_path, sort=False)
        if get_files_result.is_err():
            return Err(get_files_result.unwrap_err())  # pragma: no cover
        local_file_list = get_files_result.unwrap()
        for f in local_file_list:
            if d:
                relative_file_path = os.path.join(d, f)
            else:
                relative_file_path = f
            if relative_file_path not in ignore_list:
                file_list.append(relative_file_path)
    if sort:
        return Ok(sorted(file_list))
    return Ok(file_list)


def get_item_count_ne(path: str) -> Result[int, Error]:
    """Get number of elements in the directory, do not raise exceptions.

    Elements are files, directories, links. Only first child elements are counted.

    Args:
        path (str): path to a directory.

    Returns:
        Result[int, Error]:
            Ok (int): operation successful.
            Err (kind == `FileNotFoundError`): path does not exist.
            Err (kind == `TypeError`): path is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    validation = _dir_validation(path)
    if validation.is_err():  # pragma: no cover
        # scenario already covered in previous test
        return Err(validation.unwrap_err())  # pragma: no cover
    try:
        total_items = len([item.name for item in os.scandir(path)])
        return Ok(total_items)
    except Exception as e:  # pragma: no cover
        # error while doing file system operations
        return Err(Error.from_exception(e))  # pragma: no cover


def get_file_size_ne(path: str) -> Result[int, Error]:
    """Get file size in bytes, do not raise exceptions.

    Args:
        path (str): path to the file.

    Returns:
        Result[int, Error]:
            Ok (int): file size in bytes.
            Err (kind == `FileNotFoundError`): path does not exist.
            Err (kind == `TypeError`): path is not a file.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    validation = file_exists_ne(path)
    if validation.is_err():  # pragma: no cover
        # scenario already covered in one of previous tests
        return Err(validation.unwrap_err())  # pragma: no cover
    try:
        return Ok(os.path.getsize(path))
    except Exception as e:  # pragma: no cover
        # error while doing file system operations
        return Err(Error.from_exception(e))  # pragma: no cover


def get_file_crc32_ne(
    path: str, *, read_buf_size: int = 65536 * 2
) -> Result[int, Error]:
    """Get CRC32 of a file, do not raise exceptions.

    Args:
        path (str): path to the file.
        read_buf_size (int): read buffer size.

    Returns:
        Result[int, Error]:
            Ok (int): CRC32 as an integer.
            Err (kind == `FileNotFoundError`): path does not exist.
            Err (kind == `TypeError`): path is not a file.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    validation = file_exists_ne(path)
    if validation.is_err():  # pragma: no cover
        # scenario already covered in one of previous tests
        return Err(validation.unwrap_err())  # pragma: no cover
    try:
        crc32 = 0
        b = bytearray(read_buf_size)
        mv = memoryview(b)
        with open(path, "rb", buffering=0) as f:
            for n in iter(lambda: f.readinto(mv), 0):  # type: ignore
                crc32 = zlib.crc32(mv[:n], crc32)
            return Ok(crc32)
    except Exception as e:  # pragma: no cover
        # error while doing file system operations
        return Err(Error.from_exception(e))  # pragma: no cover


def get_file_crc32_hex_ne(
    path: str, *, read_buf_size: int = 65536 * 2
) -> Result[str, Error]:
    """Get CRC32 of a file as a hex-encoded string, do not raise exceptions.

    Args:
        path (str): path to the file.
        read_buf_size (int): read buffer size.

    Returns:
        Result[str, Error]:
            Ok (str): CRC32 as a hex-encoded sting.
            Err (kind == `FileNotFoundError`): path does not exist.
            Err (kind == `TypeError`): path is not a file.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    crc32_result = get_file_crc32_ne(path, read_buf_size=read_buf_size)
    if crc32_result.is_err():
        return Err(crc32_result.unwrap_err())  # pragma: no cover
    return Ok("%08X" % crc32_result.unwrap())


def get_file_hash_ne(
    path: str, *, algorithm: str, read_buf_size: int = 65536 * 2
) -> Result[bytes, Error]:
    """Get hash of a file as bytes, do not raise exceptions.

    The returned value can easily be converted to a hex string using `.hex()` method.

    Args:
        path (str): path to the file.
        algorithm (str): one of ("sha1", "sha256", "sha512", )
        read_buf_size (int): read buffer size.

    Returns:
        Result[bytes, Error]:
            Ok (bytes): hash as bytes.
            Err (kind == `FileNotFoundError`): path does not exist.
            Err (kind == `ValueError`): unsupported hash algorithm.
            Err (kind == `TypeError`): path is not a file.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    validation = file_exists_ne(path)
    if validation.is_err():  # pragma: no cover
        # scenario already covered in one of previous tests
        return Err(validation.unwrap_err())  # pragma: no cover
    try:
        if algorithm == "sha1":
            h = hashlib.sha1()
        elif algorithm == "sha256":
            h = hashlib.sha256()
        elif algorithm == "sha512":
            h = hashlib.sha512()
        else:
            return Err(
                Error(ErrorKind.ValueError, f"unsupported hash algorithm: {algorithm}")
            )
        # https://stackoverflow.com/a/44873382/3824328
        b = bytearray(read_buf_size)
        mv = memoryview(b)
        with open(path, "rb", buffering=0) as f:
            for n in iter(lambda: f.readinto(mv), 0):  # type: ignore
                h.update(mv[:n])
        return Ok(h.digest())
    except Exception as e:  # pragma: no cover
        # error while doing file system operations
        return Err(Error.from_exception(e))  # pragma: no cover


def gzip_file_ne(
    src: str,
    *,
    dest: str,
    arch_type: str = "gz",
    overwrite: bool = False,
    remove_src: bool = False,
) -> Result[None, Error]:
    """Create a gzip archive of specified type from the file, do not raise exceptions.

    Args:
        src (str): path to the source file.
        dest (str): path to the output file.
        arch_type (str): one of ("gz", "bz2").
        overwrite (bool): silently overwrite destination if exists.
        remove_src (bool): silently remove `src` when complete.

    Returns:
        Result[None, Error]:
            Ok (None): operation successful.
            Err (kind == `FileNotFoundError`): `src` path does not exist.
            Err (kind == `ValueError`): unsupported archive type.
            Err (kind == `TypeError`): `src` is not a file.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    pre_result = _pre_copy_and_move_file_operations(src, dest, overwrite=overwrite)
    if pre_result.is_err():
        # already covered similar case
        return pre_result  # pragma: no cover
    try:
        mode = f"w:{arch_type}"
        with tarfile.open(dest, mode) as tar:
            tar.add(src, arcname=os.path.basename(src))
        if remove_src:
            remove_src_result = remove_file_ne(src)
            if remove_src_result.is_err():
                # already covered similar case: error while deleting file
                return Err(remove_src_result.unwrap_err())  # pragma: no cover
        return Ok(None)
    except Exception as e:  # pragma: no cover
        # permissions and other errors
        return Err(Error.from_exception(e))  # pragma: no cover


def gzip_tree_ne(
    src: str,
    *,
    dest: str,
    arch_type: str = "gz",
    overwrite: bool = False,
    remove_src: bool = False,
) -> Result[None, Error]:
    """Create a gzip archive of specified type from the directory tree, do not raise exceptions.

    Args:
        src (str): path to the source directory.
        dest (str): path to the output file.
        arch_type (str): one of ("gz", "bz2").
        overwrite (bool): silently overwrite destination if exists.
        remove_src (bool): silently remove `src` when complete.

    Returns:
        Result[None, Error]:
            Ok (None): operation successful.
            Err (kind == `FileNotFoundError`): `src` path does not exist.
            Err (kind == `ValueError`): unsupported archive type.
            Err (kind == `TypeError`): `src` is not a file.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    pre_result = _pre_copy_and_move_tree_operations(src, dest, overwrite=overwrite)
    if pre_result.is_err():  # pragma: no cover
        return pre_result
    try:
        mode = f"w:{arch_type}"
        with tarfile.open(dest, mode) as tar:
            tar.add(src, arcname=os.path.basename(src))
        if remove_src:
            remove_src_result = remove_dir_ne(src)
            if remove_src_result.is_err():
                # already covered similar case: error while deleting directory
                return Err(remove_src_result.unwrap_err())  # pragma: no cover
        return Ok(None)
    except Exception as e:  # pragma: no cover
        # permissions and other errors
        return Err(Error.from_exception(e))  # pragma: no cover


def extract_gzip_archive_ne(
    src: str, *, dest: str, overwrite: bool = False, remove_src: bool = False
) -> Result[None, Error]:
    """Extract a .gz or .bz2 archive contents to a directory, do not raise exceptions.

    This function will not remove `dest` directory if it exists and `overwrite=True`,
    but its contents will be overwritten.

    Args:
        src (str): path to the source archive.
        dest (str): path to the output directory.
        overwrite (bool): silently overwrite destination if exists.
        remove_src (bool): silently remove `src` when complete.

    Returns:
        Result[None, Error]:
            Ok (None): operation successful.
            Err (kind == `FileNotFoundError`): `src` path does not exist.
            Err (kind == `FileExistsError`): `dest` directory already exists
            and `overwrite=False`.
            Err (kind == ReadError`): archive is damaged or has unsupported format.
            Err (kind == `TypeError`): `src` is not a file or
            `dest` is not a directory.
            Err (kind == `PermissionError`): wrong permissions.
            Err (kind == `...`): other error(s) occurred.
    """
    # check for src
    src_validation = file_exists_ne(src)
    if src_validation.is_err():
        return Err(src_validation.unwrap_err())  # pragma: no cover
    # check for dest
    dest_validation = dir_exists_ne(dest)
    if dest_validation.is_err():
        return Err(dest_validation.unwrap_err())  # pragma: no cover
    dest_exists = dest_validation.unwrap()
    if not dest_exists:
        # create path
        dest_path_created_result = create_path_ne(dest, overwrite=overwrite)
        if dest_path_created_result.is_err():
            return Err(dest_path_created_result.unwrap_err())  # pragma: no cover
    else:
        if not overwrite:
            return Err(
                Error(
                    ErrorKind.FileExistsError,
                    f"destination directory already exists: '{dest}'",
                )
            )
    try:
        with tarfile.open(src, "r:*") as t:
            t.extractall(dest)
        if remove_src:
            remove_src_result = remove_file_ne(src)
            if remove_src_result.is_err():
                return Err(remove_src_result.unwrap_err())  # pragma: no cover
        return Ok(None)
    except Exception as e:  # pragma: no cover
        # permissions and other errors
        return Err(Error.from_exception(e))  # pragma: no cover
