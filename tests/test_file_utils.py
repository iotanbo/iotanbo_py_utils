"""Test `file_utils.py`."""
import os
import sys

import pytest

from iotanbo_py_utils import file_utils
from iotanbo_py_utils import platform
from iotanbo_py_utils.error import ErrorKind


join = os.path.join


# Path that is invalid on all platforms
INVALID_PATH = ""
NOT_EXISTING_FILE = "/tmp/not_existing_file.txt"
NOT_EXISTING_DIR = "/tmp/not_existing_dir"
NOT_EXISTING_SYMLINK = "/tmp/not_existing_symlink"


@pytest.fixture(scope="session")
def existing_dir(tmpdir_factory: pytest.TempdirFactory) -> str:
    ed = str(tmpdir_factory.mktemp("existing_dir"))
    print("\n*** Created temporary dir for current session: ", ed)
    return ed


@pytest.fixture(scope="session")
def existing_text_file(existing_dir: str) -> str:
    ef = join(existing_dir, "existing_file.txt")
    assert file_utils.write_file_ne(ef, "test").is_ok()
    print("\n*** Created temporary text file for current session: ", ef)
    return ef


@pytest.fixture(scope="session")
def existing_text_file_symlink(existing_dir: str, existing_text_file: str) -> str:
    es = existing_dir + "/existing_text_file_symlink.txt"
    assert file_utils.create_symlink_ne(existing_text_file, es).is_ok()
    print("\n*** Created temporary symlink for current session: ", es)
    return es


# @pytest.fixture(scope="session")
# def not_existing_dir() -> str:
#     return "/tmp/this_dir_does_not_exist"


# @pytest.fixture(scope="session")
# def not_existing_file() -> str:
#     return "/tmp/this_file_does_not_exist"


def test_is_path_valid_ne() -> None:

    # Windows-style path to file
    # ! BY THE WAY: THESE ARE PERFECTLY VALID FILE NAMES ON LINUX!
    # TODO: ELABORATE
    paths_valid_on_windows_only = [
        "C:\\one\\two\\tmpfile.txt",
        "E:\\",
    ]

    for p in paths_valid_on_windows_only:
        assert not file_utils.is_path_valid_ne(p, "linux")
        assert not file_utils.is_path_valid_ne(p, "macos")
        assert file_utils.is_path_valid_ne(p, "windows")

    paths_valid_on_any_platform = [
        "file",
        "file.txt",
        ".hidden_file",
        "folder/file",
        "folder/file.txt",
        "folder/.hidden_file",
        "/",
        "/tmp/pytest-of-iotanbo/pytest-1/existing_dir0/tmpfile.txt",
    ]

    for p in paths_valid_on_any_platform:
        assert file_utils.is_path_valid_ne(p, "linux")
        assert file_utils.is_path_valid_ne(p, "macos")
        assert file_utils.is_path_valid_ne(p, "windows")

    paths_invalid_windows_only = [
        "invalid*1",
        "invalid?2",
        "invalid<>3",
        "invalid:4",
    ]
    for p in paths_invalid_windows_only:
        assert file_utils.is_path_valid_ne(p, "linux")
        assert file_utils.is_path_valid_ne(p, "macos")
        assert not file_utils.is_path_valid_ne(p, "windows")

    paths_invalid_on_any_platform = [
        INVALID_PATH,
    ]
    for p in paths_invalid_on_any_platform:
        assert not file_utils.is_path_valid_ne(p, "linux")
        assert not file_utils.is_path_valid_ne(p, "macos")
        assert not file_utils.is_path_valid_ne(p, "windows")


def test_get_item_type_ne(
    existing_text_file: str,
    existing_dir: str,
    existing_text_file_symlink: str,
) -> None:
    assert "file" == file_utils.get_item_type_ne(existing_text_file).expect(
        "Can't get file type"
    )
    assert "dir" == file_utils.get_item_type_ne(existing_dir).expect(
        "Can't get dir type"
    )
    assert "symlink" == file_utils.get_item_type_ne(existing_text_file_symlink).expect(
        "Can't get symlink type"
    )
    # negative path
    assert (
        file_utils.get_item_type_ne(NOT_EXISTING_FILE)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )


def test__item_exists_ne(
    existing_text_file: str, existing_dir: str, existing_text_file_symlink: str
) -> None:
    # Ok(True) must be returned if items with correct type exist
    assert file_utils._item_exists_ne(existing_text_file, "file").expect(
        "existing text file reported as not-existent."
    )
    assert file_utils._item_exists_ne(existing_dir, "dir").expect(
        "existing dir reported as not-existent."
    )
    assert file_utils._item_exists_ne(existing_text_file_symlink, "symlink").expect(
        "existing symlink reported as not-existent."
    )

    # Ok(False) must be returned if items of specified type do not exist
    assert not file_utils._item_exists_ne(NOT_EXISTING_FILE, "file").expect(
        "not-existing text file detection failed."
    )
    assert not file_utils._item_exists_ne(NOT_EXISTING_DIR, "dir").expect(
        "not-existing dir detection failed."
    )
    assert not file_utils._item_exists_ne(NOT_EXISTING_SYMLINK, "symlink").expect(
        "not-existing symlink detection failed."
    )

    # negative path
    # fail with `ErrorKind.TypeError` if the item exists but has different type
    assert (
        file_utils._item_exists_ne(existing_text_file_symlink, "file")
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )
    assert (
        file_utils._item_exists_ne(existing_text_file_symlink, "dir")
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )
    assert (
        file_utils._item_exists_ne(existing_text_file, "symlink")
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )
    # Ok(False) if the path is not valid
    assert not file_utils._item_exists_ne(INVALID_PATH, "file").unwrap()


def test_create_remove_file_ne(
    existing_dir: str, existing_text_file_symlink: str
) -> None:

    text_file = join(existing_dir, "dummy_text_file.txt")
    # Ok(None) if created new file
    assert file_utils.write_file_ne(text_file, "test").is_ok()

    assert file_utils.file_exists_ne(text_file).unwrap()
    # Ok(None) when removing existent file
    assert file_utils.remove_file_ne(text_file).is_ok()
    # Ok(None) when removing non-existent file and `fail_if_not_exists=False`
    assert file_utils.remove_file_ne(text_file).is_ok()

    # negative path

    # `FileNotFoundError` when removing non-existent file
    # and `fail_if_not_exists=True`
    assert (
        file_utils.remove_file_ne(text_file, fail_if_not_exists=True)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )
    # `TypeError` when trying to remove a directory
    assert (
        file_utils.remove_file_ne(existing_dir)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # `TypeError` when trying to remove a symlink
    assert (
        file_utils.remove_file_ne(existing_text_file_symlink)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )


def test_write_read_binary_file(
    existing_dir: str, existing_text_file: str, existing_text_file_symlink: str
) -> None:
    bin_file_contents = b"test\x00\x01\x02\x03"
    bin_file_contents2 = b"test\xf0\xf1\xf2\xf3"
    bin_file_path = join(existing_dir, "dummy_file.bin")
    assert file_utils.write_binary_file_ne(bin_file_path, bin_file_contents).is_ok()
    assert file_utils.file_exists_ne(bin_file_path).unwrap()
    assert file_utils.read_binary_file_ne(bin_file_path).unwrap() == bin_file_contents

    # negative path
    # FileExistsError if file exists and overwrite=False
    assert (
        file_utils.write_binary_file_ne(bin_file_path, bin_file_contents)
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )
    assert file_utils.read_binary_file_ne(bin_file_path).unwrap() == bin_file_contents

    # Ok(None) if file exists and overwrite=False
    assert file_utils.write_binary_file_ne(
        bin_file_path, bin_file_contents2, overwrite=True
    ).is_ok()
    assert file_utils.read_binary_file_ne(bin_file_path).unwrap() == bin_file_contents2


def test_create_remove_dir_ne(
    existing_dir: str, existing_text_file: str, existing_text_file_symlink: str
) -> None:
    valid_path = join(existing_dir, "valid", "path")
    # Ok(None) when created a new path
    assert file_utils.create_path_ne(valid_path).is_ok()
    assert file_utils.dir_exists_ne(valid_path).unwrap()

    # Ok(None) when trying to create path and it already exists
    # and `overwrite` is `True`
    assert file_utils.create_path_ne(valid_path, overwrite=True).is_ok()

    # Ok(None) when removing existent directory
    assert file_utils.remove_dir_ne(valid_path).is_ok()

    # Ok(None) when removing non-existent directory and `fail_if_not_exists=False`
    assert file_utils.remove_dir_ne(valid_path).is_ok()

    # negative path

    # `FileNotFoundError` when removing non-existent directory
    # and `fail_if_not_exists=True`
    assert (
        file_utils.remove_dir_ne(valid_path, fail_if_not_exists=True)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )
    # `TypeError` when trying to remove a file
    assert (
        file_utils.remove_dir_ne(existing_text_file)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # `TypeError` when trying to remove a symlink
    assert (
        file_utils.remove_dir_ne(existing_text_file_symlink)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # `TypeError` when trying to create path and file with same name exists
    assert (
        file_utils.create_path_ne(existing_text_file)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # `FileExistsError` when trying to create path and it already exists
    # and `overwrite` is `False`
    assert (
        file_utils.create_path_ne(existing_dir)
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )


def test_create_remove_symlink_ne(existing_text_file: str, existing_dir: str) -> None:
    # Create and remove symlink to file
    text_file_symlink = join(existing_dir, "file_symlink.txt")
    assert file_utils.create_symlink_ne(existing_text_file, text_file_symlink).is_ok()
    assert file_utils.symlink_exists_ne(text_file_symlink).unwrap()

    # Ok(None) when trying to create symlink and it already exists
    # and `overwrite` is `True`
    assert file_utils.create_symlink_ne(
        existing_text_file, text_file_symlink, overwrite=True
    ).is_ok()

    assert file_utils.symlink_exists_ne(text_file_symlink).unwrap()

    # FileExistsError when trying to create symlink and it already exists
    # and `overwrite` is `True`
    assert (
        file_utils.create_symlink_ne(existing_text_file, text_file_symlink)
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )

    assert file_utils.remove_symlink_ne(text_file_symlink).is_ok()

    # negative path
    # Ok(False) when symlink does not exist
    assert not file_utils.symlink_exists_ne(text_file_symlink).unwrap()

    # Even though path validation is not done,
    # OS can't create symlink and returns error
    assert file_utils.create_symlink_ne(existing_text_file, INVALID_PATH).is_err()

    # Create and remove symlink to dir
    dir_symlink = join(existing_dir, "symlink_to_parent_dir")
    assert file_utils.create_symlink_ne(existing_dir, dir_symlink).is_ok()
    assert file_utils.symlink_exists_ne(dir_symlink)
    assert file_utils.remove_symlink_ne(dir_symlink).is_ok()

    # Ok(None) when symlink does not exist and `fail_if_not_exists` is False
    assert file_utils.remove_symlink_ne(NOT_EXISTING_SYMLINK).is_ok()

    # Ok(None) when path is invalid
    assert file_utils.remove_symlink_ne(INVALID_PATH).is_ok()

    # negative path
    assert not file_utils.symlink_exists_ne(dir_symlink).unwrap()

    # Ok(False) when path is invalid
    assert not file_utils.symlink_exists_ne(INVALID_PATH).unwrap()

    # `FileNotFoundError` when symlink does not exist and
    # `fail_if_not_exists` is True
    assert (
        file_utils.remove_symlink_ne(NOT_EXISTING_SYMLINK, fail_if_not_exists=True)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )

    # Ok(None) if path is invalid
    assert file_utils.remove_symlink_ne(INVALID_PATH).is_ok()

    # `FileNotFoundError` when src does not exist
    assert (
        file_utils.create_symlink_ne(NOT_EXISTING_FILE, text_file_symlink)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )

    # `FileNotFoundError` when src path is invalid
    assert (
        file_utils.create_symlink_ne(INVALID_PATH, text_file_symlink)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )

    # `FileNotFoundError` when dest path is invalid
    assert (
        file_utils.create_symlink_ne(existing_text_file, INVALID_PATH)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )


def test_os_symlink(existing_dir: str, existing_text_file: str) -> None:

    # FileNotFoundError if src exists and path to dest is invalid
    with pytest.raises(FileNotFoundError):
        os.symlink(existing_text_file, INVALID_PATH)

    # Strangely, macOS allows creating symlinks to empty and invalid paths
    if sys.platform == "linux":
        symlink_dest = join(existing_dir, "symlink_dest")
        with pytest.raises(FileNotFoundError):
            os.symlink(INVALID_PATH, symlink_dest)

    if sys.platform == "linux":
        symlink_to_empty = join(existing_dir, "symlink_to_empty")
        with pytest.raises(FileNotFoundError):
            os.symlink("", symlink_to_empty)


def test_read_write_text_file_ne(existing_dir: str) -> None:
    tmpfile = join(existing_dir, "tmpfile.txt")
    assert file_utils.write_file_ne(tmpfile, "test").is_ok()
    # Ok(None) when trying to overwrite file that already exists
    # and overwrite=True
    assert file_utils.write_file_ne(tmpfile, "test", overwrite=True).is_ok()

    # FileExistsError when trying to overwrite file that already exists
    # and overwrite=False
    assert (
        file_utils.write_file_ne(tmpfile, "test2")
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )

    assert "test" == file_utils.read_file_ne(tmpfile).expect("Can't read text file")
    assert file_utils.remove_file_ne(tmpfile).is_ok()

    # Check 'universal' newline mode: any of `\r`, `\r\n` will be replaced
    # with `\n`
    multiline_win_file = join(existing_dir, "multiline_win_file.txt")
    multiline_win_contents = b"one\rtwo\r"

    assert file_utils.write_binary_file_ne(
        multiline_win_file, multiline_win_contents
    ).is_ok()

    assert file_utils.read_file_ne(multiline_win_file).unwrap() == "one\ntwo\n"

    # negative path

    # FileNotFoundError when trying to create file with invalid path
    assert (
        file_utils.write_file_ne(INVALID_PATH, "test")
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )

    # TypeError when trying to overwrite file that is a directory
    # and overwrite=True
    assert (
        file_utils.write_file_ne(existing_dir, "test2", overwrite=True)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # trying to read from non-existing file will result in error
    assert file_utils.read_file_ne(NOT_EXISTING_FILE).is_err()

    # trying to read from invalid path when validating it will result in error
    assert file_utils.read_file_ne(INVALID_PATH).is_err()

    assert file_utils.read_binary_file_ne(NOT_EXISTING_FILE).is_err()
    assert file_utils.read_binary_file_ne(INVALID_PATH).is_err()


def test_read_file_into_lines_ne(existing_dir: str) -> None:
    win_sep_contents = b"one\r\ntwo\r\n"
    old_mac_sep_contents = b"one\rtwo\r"
    unix_sep_contents = b"one\ntwo\n"
    mixed_sep_contents = b"one\ntwo\r"
    single_line_contents = b"one"
    invalid_unicode_contents = b"one\x00\x01\x02\xFF\xFE\ntwo"

    empty_file = join(existing_dir, "empty_file.txt")
    assert file_utils.write_binary_file_ne(empty_file, b"").is_ok()

    win_sep_file = join(existing_dir, "win_sep_file.txt")
    assert file_utils.write_binary_file_ne(win_sep_file, win_sep_contents).is_ok()

    old_mac_sep_file = join(existing_dir, "old_mac_sep_file.txt")
    assert file_utils.write_binary_file_ne(
        old_mac_sep_file, old_mac_sep_contents
    ).is_ok()

    unix_sep_file = join(existing_dir, "unix_sep_file.txt")
    assert file_utils.write_binary_file_ne(unix_sep_file, unix_sep_contents).is_ok()

    mixed_sep_file = join(existing_dir, "mixed_sep_file.txt")
    assert file_utils.write_binary_file_ne(mixed_sep_file, mixed_sep_contents).is_ok()

    single_line_file = join(existing_dir, "single_line_file.txt")
    assert file_utils.write_binary_file_ne(
        single_line_file, single_line_contents
    ).is_ok()

    invalid_unicode_file = join(existing_dir, "invalid_unicode_file.txt")
    assert file_utils.write_binary_file_ne(
        invalid_unicode_file, invalid_unicode_contents
    ).is_ok()

    assert file_utils.read_file_into_lines_ne(empty_file).unwrap() == [""]

    assert file_utils.read_file_into_lines_ne(win_sep_file).unwrap() == [
        "one",
        "two",
        "",
    ]

    assert file_utils.read_file_into_lines_ne(old_mac_sep_file).unwrap() == [
        "one",
        "two",
        "",
    ]

    assert file_utils.read_file_into_lines_ne(unix_sep_file).unwrap() == [
        "one",
        "two",
        "",
    ]

    assert file_utils.read_file_into_lines_ne(single_line_file).unwrap() == ["one"]

    # negative path
    assert (
        file_utils.read_file_into_lines_ne(invalid_unicode_file)
        .unwrap_err()
        .kind_is(ErrorKind.UnicodeDecodeError)
    )


def test_split() -> None:
    assert ["one\ntwo", ""] == "one\ntwo\r".split(sep="\r")


def test_create_remove_read_without_permissions(existing_text_file: str) -> None:
    """! DO NOT RUN AS ROOT!

    This test will run under linux only. On other platforms it is ignored.
    """
    if not platform.is_linux():
        return
        # raise AssertionError("This test must be run under linux only.")

    file = "/root/not_allowed.txt"
    directory = "/root/not_allowed_dir"
    symlink = "/root/not_allowed_symlink"
    existing_file_with_no_permission = "/var/log/syslog"

    # `PermissionError` when trying to create file without appropriate premissions
    assert (
        file_utils.write_file_ne(file, "test")
        .unwrap_err()
        .kind_is(ErrorKind.PermissionError)
    )

    # `PermissionError` when trying to create directory without appropriate premissions
    assert (
        file_utils.create_path_ne(directory)
        .unwrap_err()
        .kind_is(ErrorKind.PermissionError)
    )

    # `PermissionError` when trying to create symlink without appropriate premissions
    assert (
        file_utils.create_symlink_ne(existing_text_file, symlink)
        .unwrap_err()
        .kind_is(ErrorKind.PermissionError)
    )

    # `PermissionError` when trying to remove file without appropriate premissions
    assert (
        file_utils.remove_file_ne(existing_file_with_no_permission)
        .unwrap_err()
        .kind_is(ErrorKind.PermissionError)
    )

    # `PermissionError` when trying to read file without appropriate premissions
    # ! This is tricky to automate
    # assert file_utils.read_file_ne(
    #     existing_file_with_no_permission).unwrap_err().kind_is(
    #     ErrorKind.PermissionError)

    # `PermissionError` when trying to remove dir without appropriate premissions
    assert (
        file_utils.remove_dir_ne("/var/log/private")
        .unwrap_err()
        .kind_is(ErrorKind.PermissionError)
    )

    # `PermissionError` when trying to remove symlink without appropriate premissions
    # ! This is tricky to automate
    # assert file_utils.remove_symlink_ne(
    #     existing_file_with_no_permission).unwrap_err().kind_is(ErrorKind.PermissionError)


def test_file_exists_ne(
    existing_text_file: str, existing_dir: str, existing_text_file_symlink: str
) -> None:
    # Ok(True) if file exists
    assert file_utils.file_exists_ne(existing_text_file).expect(
        "error while checking for file existence"
    )
    # Ok(False) if file does not exist
    assert not file_utils.file_exists_ne(NOT_EXISTING_FILE).expect(
        "error while checking for existence of non-existent file"
    )

    # negative path

    # fail if it is a dir
    assert (
        file_utils.file_exists_ne(existing_dir)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # fail if it is a symlink
    assert (
        file_utils.file_exists_ne(existing_text_file_symlink)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )


def test_dir_exists_ne(
    existing_text_file: str, existing_dir: str, existing_text_file_symlink: str
) -> None:
    # Ok(True) if dir exists
    assert file_utils.dir_exists_ne(existing_dir).expect(
        "error while checking for dir existence"
    )
    # Ok(False) if dir does not exist
    assert not file_utils.dir_exists_ne(NOT_EXISTING_DIR).expect(
        "error while checking for existence of non-existent dir"
    )

    # negative path

    # fail if it is a file
    assert (
        file_utils.dir_exists_ne(existing_text_file)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # fail if it is a symlink
    assert (
        file_utils.dir_exists_ne(existing_text_file_symlink)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )


def test_symlink_exists_ne(
    existing_text_file: str, existing_dir: str, existing_text_file_symlink: str
) -> None:
    # Ok(True) if symlink exists
    assert file_utils.symlink_exists_ne(existing_text_file_symlink).expect(
        "error while checking for symlink existence"
    )
    # Ok(False) if symlink does not exist
    assert not file_utils.symlink_exists_ne(NOT_EXISTING_SYMLINK).expect(
        "error while checking for existence of non-existent symlink"
    )

    # negative path

    # fail if it is a file
    assert (
        file_utils.symlink_exists_ne(existing_text_file)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # fail if it is a dir
    assert (
        file_utils.symlink_exists_ne(existing_dir)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )


def test_ensure_parent_dir_exists(
    existing_dir: str,
    existing_text_file: str
    # , existing_text_file_symlink: str
) -> None:

    # Ok(None) when parent directory already exists
    assert file_utils.ensure_parent_dir_exists(existing_text_file).is_ok()

    # Ok(None) when parent directory does not exist but was successfully created
    dummy_file = join(existing_dir, "dummy", "path", "dummy_file.txt")
    assert file_utils.ensure_parent_dir_exists(dummy_file).is_ok()
    assert file_utils.write_file_ne(dummy_file, "test").is_ok()

    # negative path

    # FileNotFoundError if path is not valid
    assert (
        file_utils.ensure_parent_dir_exists(INVALID_PATH)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )

    # TypeError if parent directory exists but is not a directory
    invalid_parent_path = join(dummy_file, "another_file.txt")
    assert (
        file_utils.ensure_parent_dir_exists(invalid_parent_path)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )


def test_ensure_parent_dir_exists_with_bad_permissions() -> None:
    # PermissionError when trying to create parent dir without proper permissions
    file = "/root/dummy/not_allowed.txt"
    assert (
        file_utils.ensure_parent_dir_exists(file)
        .unwrap_err()
        .kind_is(ErrorKind.PermissionError)
    )


def test_dir_empty_ne(existing_dir: str, existing_text_file: str) -> None:
    empty_test_dir = join(existing_dir, "empty_test_dir")
    assert file_utils.create_path_ne(empty_test_dir).is_ok()
    assert file_utils.dir_empty_ne(empty_test_dir).unwrap()
    assert file_utils.write_file_ne(
        join(empty_test_dir, ".hidden_text_file"), "hidden_text_file"
    ).is_ok()

    # Ok(False) if directory contains hidden file
    assert not file_utils.dir_empty_ne(empty_test_dir).unwrap()

    # `TypeError` if not a directory
    assert (
        file_utils.dir_empty_ne(existing_text_file)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # `FileNotFoundError` if path not valid
    assert (
        file_utils.dir_empty_ne(INVALID_PATH)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )


def _create_directory_with_contents(path: str, existing_text_file: str) -> None:
    """Create a directory with dummy contents for test purposes."""
    # Create few subdirs  with a `dummy.txt` file inside
    subdirs = ["subdir2", "subdir3", "subdir4"]
    for s in subdirs:
        s_path = join(path, s)
        assert file_utils.create_path_ne(s_path).is_ok()
        f_path = join(s_path, "dummy.txt")
        assert file_utils.write_file_ne(f_path, "dummy").is_ok()

    subsubdir = join(path, "subdir", "sub-subdir")
    assert file_utils.create_path_ne(subsubdir).is_ok()

    assert file_utils.write_file_ne(
        join(path, "dummy_text_file.txt"), "dummy_text_file"
    ).is_ok()

    # Create few hidden text files
    hidden_text_file = join(path, ".hidden_text_file")
    assert file_utils.write_file_ne(hidden_text_file, "hidden_text_file").is_ok()

    assert file_utils.write_file_ne(
        join(subsubdir, ".hidden_text_file2"), "hidden_text_file2"
    ).is_ok()

    # Create a symlink
    symlink1 = join(subsubdir, ".hidden_text_file")
    assert file_utils.create_symlink_ne(existing_text_file, symlink1).is_ok()


def _validate_directory_with_contents(
    path: str, symlinks_replaced_with_files: bool = False
) -> bool:
    """Check that the contents of a directory\
    created with `_create_directory_with_contents()` is OK."""
    assert file_utils.dir_exists_ne(path).unwrap()
    subdirs = ["subdir2", "subdir3", "subdir4"]
    for s in subdirs:
        s_path = join(path, s)
        assert file_utils.dir_exists_ne(s_path).unwrap()
        f_path = join(s_path, "dummy.txt")
        assert file_utils.file_exists_ne(f_path).unwrap()

    subsubdir = join(path, "subdir", "sub-subdir")
    assert file_utils.dir_exists_ne(subsubdir).unwrap()

    assert file_utils.file_exists_ne(join(path, "dummy_text_file.txt")).unwrap()

    hidden_text_file = join(path, ".hidden_text_file")
    assert file_utils.file_exists_ne(hidden_text_file).unwrap()

    assert file_utils.file_exists_ne(join(subsubdir, ".hidden_text_file2")).unwrap()

    symlink1 = join(subsubdir, ".hidden_text_file")
    if not symlinks_replaced_with_files:
        assert file_utils.symlink_exists_ne(symlink1).unwrap()
    else:
        assert file_utils.file_exists_ne(symlink1).unwrap()
    return True


def test_remove_dir_contents_ne(existing_dir: str, existing_text_file: str) -> None:
    root_dir = join(existing_dir, "root_for_remove_dir_contents")
    _create_directory_with_contents(root_dir, existing_text_file)

    assert not file_utils.dir_empty_ne(root_dir).unwrap()
    assert file_utils.remove_dir_contents_ne(root_dir).is_ok()
    assert file_utils.dir_exists_ne(root_dir).unwrap()
    assert file_utils.dir_empty_ne(root_dir).unwrap()

    # negative tests

    # `FileNotFoundError` if path not valid
    assert (
        file_utils.remove_dir_contents_ne(INVALID_PATH)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )


def test_copy_file_ne(existing_dir: str, existing_text_file: str) -> None:
    dest = join(existing_dir, "file_copy.txt")
    # Ok(None) when copy existing file
    assert file_utils.copy_file_ne(existing_text_file, dest).is_ok()
    assert file_utils.file_exists_ne(dest).unwrap()

    # FileExistsError when dest already exists
    assert (
        file_utils.copy_file_ne(existing_text_file, dest)
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )

    # FileNotFoundError when src does not exist
    assert (
        file_utils.copy_file_ne(NOT_EXISTING_FILE, dest)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )

    # FileExistsError when dest exists and overwrite=False
    assert (
        file_utils.copy_file_ne(existing_text_file, dest)
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )

    # Ok(None) when dest exists and overwrite=True
    assert file_utils.copy_file_ne(existing_text_file, dest, overwrite=True).is_ok()

    # FileNotFoundError when src is invalid path
    file_utils.remove_file_ne(dest)
    assert (
        file_utils.copy_file_ne(INVALID_PATH, dest)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )

    # FileNotFoundError when dest is invalid path
    assert (
        file_utils.copy_file_ne(existing_text_file, INVALID_PATH)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )

    # TypeError when dest is a directory
    assert (
        file_utils.copy_file_ne(existing_text_file, existing_dir)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # TypeError when src is a directory
    assert (
        file_utils.copy_file_ne(existing_dir, dest)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )


def test_move_file_ne(existing_dir: str, existing_text_file: str) -> None:
    src = join(existing_dir, "src_file.txt")
    assert file_utils.copy_file_ne(existing_text_file, src).is_ok()
    dest = join(existing_dir, "moved_file.txt")

    # Ok(None) when move existing file
    assert file_utils.move_file_ne(src, dest).is_ok()
    assert file_utils.file_exists_ne(dest).unwrap()
    assert file_utils.copy_file_ne(existing_text_file, src).is_ok()

    # FileExistsError when dest already exists
    assert (
        file_utils.move_file_ne(src, dest)
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )

    # FileNotFoundError when src does not exist
    assert (
        file_utils.move_file_ne(NOT_EXISTING_FILE, dest)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )

    # FileExistsError when dest exists and overwrite=False
    assert (
        file_utils.move_file_ne(src, dest)
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )

    # Ok(None) when dest exists and overwrite=True
    assert file_utils.move_file_ne(src, dest, overwrite=True).is_ok()

    # FileNotFoundError when src is invalid path
    file_utils.remove_file_ne(dest)
    assert (
        file_utils.move_file_ne(INVALID_PATH, dest)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )

    # FileNotFoundError when dest is invalid path
    assert (
        file_utils.move_file_ne(src, INVALID_PATH)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )

    # TypeError when dest is a directory
    assert file_utils.copy_file_ne(existing_text_file, src).is_ok()
    assert (
        file_utils.move_file_ne(src, existing_dir)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # TypeError when src is a directory
    assert (
        file_utils.move_file_ne(existing_dir, dest)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )


def test_copy_tree_ne(existing_dir: str, existing_text_file: str) -> None:
    root_dir = join(existing_dir, "root_for_copy_tree")
    _create_directory_with_contents(root_dir, existing_text_file)
    copy = join(existing_dir, "copied_tree")
    assert file_utils.copy_tree_ne(root_dir, copy).is_ok()
    # assert file_utils.dir_exists_ne(copy)
    assert _validate_directory_with_contents(root_dir)
    assert _validate_directory_with_contents(copy)

    # test copy_tree_ne when symlinks are replaced by files
    copy_symlinks_replaced = join(existing_dir, "root_for_copy_symlinks_replaced")
    assert file_utils.copy_tree_ne(
        root_dir, copy_symlinks_replaced, symlinks=False
    ).is_ok()
    assert _validate_directory_with_contents(
        copy_symlinks_replaced, symlinks_replaced_with_files=True
    )

    # Ok(None) when destination directory already exists
    # and overwrite=True
    assert file_utils.copy_tree_ne(root_dir, copy, overwrite=True).is_ok()

    # negative path
    # FileNotFoundError when src does not exist
    assert (
        file_utils.copy_tree_ne(NOT_EXISTING_DIR, join(existing_dir, "copied_tree_2"))
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )

    # FileExistsError when destination directory already exists
    # and overwrite=False
    assert (
        file_utils.copy_tree_ne(root_dir, copy)
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )

    # FileExistsError when destination directory already exists
    # and overwrite=False
    assert (
        file_utils.copy_tree_ne(root_dir, copy)
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )

    # TypeError when src is not a directory
    assert (
        file_utils.copy_tree_ne(existing_text_file, join(existing_dir, "copied_tree_3"))
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # TypeError when dest is not a directory
    assert (
        file_utils.copy_tree_ne(root_dir, existing_text_file)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )


def test_move_tree_ne(existing_dir: str, existing_text_file: str) -> None:
    root_dir = join(existing_dir, "root_for_move_tree")
    _create_directory_with_contents(root_dir, existing_text_file)
    moved_dir = join(existing_dir, "moved_tree")

    # Ok(None) when moving existing dir to not-existing dest
    assert file_utils.move_tree_ne(root_dir, moved_dir).is_ok()

    assert not file_utils.dir_exists_ne(root_dir).unwrap()
    assert _validate_directory_with_contents(moved_dir)

    # Ok(None) when destination directory already exists
    # and overwrite=True
    assert file_utils.copy_tree_ne(moved_dir, root_dir).is_ok()
    assert file_utils.move_tree_ne(root_dir, moved_dir, overwrite=True).is_ok()

    # negative path
    # FileNotFoundError when src does not exist
    assert (
        file_utils.move_tree_ne(NOT_EXISTING_DIR, join(existing_dir, "moved_tree_2"))
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )

    # FileExistsError when destination directory already exists
    # and overwrite=False
    assert file_utils.copy_tree_ne(moved_dir, root_dir).is_ok()
    assert (
        file_utils.move_tree_ne(root_dir, moved_dir)
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )

    # FileExistsError when destination directory already exists
    # and overwrite=False
    assert (
        file_utils.move_tree_ne(root_dir, moved_dir)
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )

    # TypeError when src is not a directory
    assert (
        file_utils.move_tree_ne(existing_text_file, join(existing_dir, "moved_tree_3"))
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # TypeError when dest is not a directory
    assert (
        file_utils.move_tree_ne(root_dir, existing_text_file)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )


def test_get_subdir_list_ne(existing_dir: str, existing_text_file: str) -> None:
    root_dir = join(existing_dir, "root_for_get_subdir_list_ne")
    _create_directory_with_contents(root_dir, existing_text_file)
    assert file_utils.dir_exists_ne(root_dir).unwrap()

    # Ok(List[str]) when getting sorted list of subdirs
    first_level_subdirs = file_utils.get_subdir_list_ne(root_dir).unwrap()
    assert first_level_subdirs == ["subdir", "subdir2", "subdir3", "subdir4"]

    # Ok(List[str]) when getting unsorted list of subdirs
    first_level_subdirs = file_utils.get_subdir_list_ne(root_dir, sort=False).unwrap()
    assert len(first_level_subdirs) == 4

    # negative path

    # TypeError when path is not a directory
    assert (
        file_utils.get_subdir_list_ne(existing_text_file)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # FileNotFoundError when path not exists
    assert (
        file_utils.get_subdir_list_ne(NOT_EXISTING_DIR)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )


def test_get_subdir_list_recursively_ne(
    existing_dir: str, existing_text_file: str
) -> None:
    root_dir = join(existing_dir, "root_for_get_subdir_list_recursively_ne")
    _create_directory_with_contents(root_dir, existing_text_file)
    assert file_utils.dir_exists_ne(root_dir).unwrap()

    # Ok(List[str]) when getting sorted list of subdirs
    subdirs = file_utils.get_subdir_list_recursively_ne(root_dir).unwrap()
    assert subdirs == sorted(
        ["subdir", "subdir2", "subdir3", "subdir4", join("subdir", "sub-subdir")]
    )

    # Ok(List[str]) when getting unsorted list of subdirs
    subdirs = file_utils.get_subdir_list_recursively_ne(root_dir, sort=False).unwrap()
    assert len(subdirs) == 5

    # Ignored sub-directories are excluded from the result
    ignore = ["subdir3", join("subdir", "sub-subdir"), ""]
    subdirs = file_utils.get_subdir_list_recursively_ne(
        root_dir, ignore_list=ignore
    ).unwrap()
    assert subdirs == sorted(["subdir", "subdir2", "subdir4"])

    # negative path

    # TypeError when path is not a directory
    assert (
        file_utils.get_subdir_list_recursively_ne(existing_text_file)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # FileNotFoundError when path not exists
    assert (
        file_utils.get_subdir_list_recursively_ne(NOT_EXISTING_DIR)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )


def test_get_file_list_ne(existing_dir: str, existing_text_file: str) -> None:
    root_dir = join(existing_dir, "root_for_get_file_list_ne")
    _create_directory_with_contents(root_dir, existing_text_file)
    assert file_utils.dir_exists_ne(root_dir).unwrap()
    # Ok(List[str]) when getting sorted list of files
    first_level_files = file_utils.get_file_list_ne(root_dir).unwrap()
    assert first_level_files == [".hidden_text_file", "dummy_text_file.txt"]

    # Ok(List[str]) when getting unsorted list of files
    first_level_files = file_utils.get_file_list_ne(root_dir, sort=False).unwrap()
    assert len(first_level_files) == 2


def test_get_file_list_recursively_ne(
    existing_dir: str, existing_text_file: str
) -> None:
    root_dir = join(existing_dir, "root_for_get_file_list_recursively_ne")
    _create_directory_with_contents(root_dir, existing_text_file)
    assert file_utils.dir_exists_ne(root_dir).unwrap()

    # Ok(List[str]) when getting sorted list of subdirs
    files = file_utils.get_file_list_recursively_ne(root_dir).unwrap()
    assert files == sorted(
        [
            "dummy_text_file.txt",
            ".hidden_text_file",
            join("subdir2", "dummy.txt"),
            join("subdir3", "dummy.txt"),
            join("subdir4", "dummy.txt"),
            join("subdir", "sub-subdir", ".hidden_text_file"),
            join("subdir", "sub-subdir", ".hidden_text_file2"),
        ]
    )

    # Ok(List[str]) when getting unsorted list of subdirs
    files = file_utils.get_file_list_recursively_ne(root_dir, sort=False).unwrap()
    assert len(files) == 7

    # Ignored files and sub-directories are excluded from the result
    ignore = ["dummy_text_file.txt", "subdir3", join("subdir", "sub-subdir")]
    files = file_utils.get_file_list_recursively_ne(
        root_dir, ignore_list=ignore
    ).unwrap()
    assert files == sorted(
        [
            ".hidden_text_file",
            join("subdir2", "dummy.txt"),
            join("subdir4", "dummy.txt"),
        ]
    )

    # # negative path

    # TypeError when path is not a directory
    assert (
        file_utils.get_file_list_recursively_ne(existing_text_file)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # FileNotFoundError when path not exists
    assert (
        file_utils.get_file_list_recursively_ne(NOT_EXISTING_DIR)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )


def test_get_aggregated_file_list_ne(
    existing_dir: str, existing_text_file: str
) -> None:
    root_dir = join(existing_dir, "root_for_get_aggregated_file_list_ne")
    _create_directory_with_contents(root_dir, existing_text_file)
    assert file_utils.dir_exists_ne(root_dir).unwrap()

    subdirs = file_utils.get_subdir_list_recursively_ne(root_dir).unwrap()

    # Ok(List[str]) when getting sorted list of subdirs
    files = file_utils.get_aggregated_file_list_ne(root_dir, subdirs).unwrap()
    assert files == sorted(
        [
            "dummy_text_file.txt",
            ".hidden_text_file",
            join("subdir2", "dummy.txt"),
            join("subdir3", "dummy.txt"),
            join("subdir4", "dummy.txt"),
            join("subdir", "sub-subdir", ".hidden_text_file"),
            join("subdir", "sub-subdir", ".hidden_text_file2"),
        ]
    )

    # Ok(List[str]) when getting unsorted list of subdirs
    files = file_utils.get_aggregated_file_list_ne(
        root_dir, subdirs, sort=False
    ).unwrap()
    assert len(files) == 7

    # Ignored files and sub-directories are excluded from the result
    ignore = ["dummy_text_file.txt", join("subdir", "sub-subdir", ".hidden_text_file")]
    files = file_utils.get_aggregated_file_list_ne(
        root_dir, subdirs, ignore_list=ignore
    ).unwrap()
    assert files == sorted(
        [
            ".hidden_text_file",
            join("subdir2", "dummy.txt"),
            join("subdir3", "dummy.txt"),
            join("subdir4", "dummy.txt"),
            join("subdir", "sub-subdir", ".hidden_text_file2"),
        ]
    )

    # negative path

    # TypeError when path is not a directory
    assert (
        file_utils.get_aggregated_file_list_ne(existing_text_file, subdirs)
        .unwrap_err()
        .kind_is(ErrorKind.TypeError)
    )

    # FileNotFoundError when path not exists
    assert (
        file_utils.get_aggregated_file_list_ne(NOT_EXISTING_DIR, subdirs)
        .unwrap_err()
        .kind_is(ErrorKind.FileNotFoundError)
    )


def test_get_item_count_ne(existing_dir: str, existing_text_file: str) -> None:
    root_dir = join(existing_dir, "root_for_test_get_item_count_ne")
    _create_directory_with_contents(root_dir, existing_text_file)
    assert file_utils.dir_exists_ne(root_dir).unwrap()

    # Ok(int) when getting item count of an existing directory
    count = file_utils.get_item_count_ne(root_dir).unwrap()
    assert count == 6  # 4 directories and 2 files


def test_get_file_size_ne(existing_text_file: str) -> None:
    result = file_utils.get_file_size_ne(existing_text_file)
    assert result.unwrap() == 4


def test_get_file_crc32_ne(existing_text_file: str) -> None:
    # https://crccalc.com
    result = file_utils.get_file_crc32_hex_ne(existing_text_file)
    assert result.unwrap() == "D87F7E0C"

    result = file_utils.get_file_crc32_hex_ne(existing_text_file, read_buf_size=1)
    assert result.unwrap() == "D87F7E0C"


def test_get_file_hash_ne(existing_text_file: str) -> None:
    # The contents of the text file is 'test'
    result = file_utils.get_file_hash_ne(existing_text_file, algorithm="sha1")
    assert result.unwrap().hex() == "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"

    result = file_utils.get_file_hash_ne(
        existing_text_file, algorithm="sha1", read_buf_size=1
    )
    assert result.unwrap().hex() == "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"

    result = file_utils.get_file_hash_ne(existing_text_file, algorithm="sha256")
    assert (
        result.unwrap().hex()
        == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    )

    result = file_utils.get_file_hash_ne(existing_text_file, algorithm="sha512")
    assert result.unwrap().hex() == (
        "ee26b0dd4af7e749aa1a8ee3c10ae9923f618980772e473f8819a5d4940"
        "e0db27ac185f8a0e1d5f84f88bc887fd67b143732c304cc5fa9ad8e6f57f50028a8ff"
    )

    # negative path
    assert (
        file_utils.get_file_hash_ne(existing_text_file, algorithm="dummy")
        .unwrap_err()
        .kind_is(ErrorKind.ValueError)
    )


def test_gzip_file_ne(existing_dir: str, existing_text_file: str) -> None:
    text_file_copy = join(existing_dir, "text_file_copy.txt")
    file_utils.copy_file_ne(existing_text_file, text_file_copy)
    dest_gz = join(existing_dir, "archived_text_file.tar.gz")
    dest_bz2 = join(existing_dir, "archived_text_file.tar.bz2")
    assert file_utils.gzip_file_ne(text_file_copy, dest=dest_gz, arch_type="gz").is_ok()
    assert file_utils.gzip_file_ne(
        text_file_copy, dest=dest_bz2, arch_type="bz2", remove_src=True
    ).is_ok()

    # Ok(None) when extracting existing archive into not-existing directory
    gzip_extract_root = join(existing_dir, "gzip_extract_root")
    assert file_utils.extract_gzip_archive_ne(dest_gz, dest=gzip_extract_root).is_ok()

    # FileExistsError when extracting existing archive into existing directory
    # and overwrite=False
    assert (
        file_utils.extract_gzip_archive_ne(dest_gz, dest=gzip_extract_root)
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )

    # Ok(None) when extracting existing archive into existing directory
    # and overwrite=True
    assert file_utils.extract_gzip_archive_ne(
        dest_gz, dest=gzip_extract_root, overwrite=True
    ).is_ok()

    # ReadError when src has wrong format
    assert (
        file_utils.extract_gzip_archive_ne(
            existing_text_file, dest=gzip_extract_root, overwrite=True
        )
        .unwrap_err()
        .kind_is("ReadError")
    )


def test_gzip_tree_ne(existing_dir: str, existing_text_file: str) -> None:

    dummy_dir = join(existing_dir, "root_for_test_gzip_tree_ne")
    _create_directory_with_contents(dummy_dir, existing_text_file)
    assert file_utils.dir_exists_ne(dummy_dir).unwrap()

    dummy_dir_gz = join(existing_dir, "dummy_dir.tar.gz")
    dummy_dir_bz2 = join(existing_dir, "dummy_dir.tar.bz2")
    assert file_utils.gzip_tree_ne(dummy_dir, dest=dummy_dir_gz, arch_type="gz").is_ok()

    assert file_utils.gzip_tree_ne(
        dummy_dir, dest=dummy_dir_bz2, arch_type="bz2", remove_src=True
    ).is_ok()

    assert not file_utils.dir_exists_ne(dummy_dir).unwrap()

    # Ok(None) when extracting existing archive into not-existing directory
    gz_dir_extract_root = join(existing_dir, "gz_dir_extract_root")
    assert file_utils.extract_gzip_archive_ne(
        dummy_dir_gz, dest=gz_dir_extract_root
    ).is_ok()

    # FileExistsError when extracting existing archive into existing directory
    # and overwrite=False
    assert (
        file_utils.extract_gzip_archive_ne(dummy_dir_gz, dest=gz_dir_extract_root)
        .unwrap_err()
        .kind_is(ErrorKind.FileExistsError)
    )

    # Ok(None) when extracting existing archive into existing directory
    # and overwrite=True
    assert file_utils.extract_gzip_archive_ne(
        dummy_dir_gz, dest=gz_dir_extract_root, overwrite=True, remove_src=True
    ).is_ok()

    # ReadError when src has wrong format
    assert (
        file_utils.extract_gzip_archive_ne(
            existing_text_file, dest=gz_dir_extract_root, overwrite=True
        )
        .unwrap_err()
        .kind_is("ReadError")
    )
