import ntpath
import os
import shutil
import subprocess  # for execute_shell_cmd
import tarfile
import urllib.request
from pathlib import Path
from urllib import error

from iotanbo_py_utils.error import IotanboError
from iotanbo_py_utils.error import ResultTuple


def file_exists_ne(path_to_file: str) -> bool:
    """
    Check if file exists.
    :return: True if file exists, false if not exists or is a directory.
    :except: None
    """
    try:
        result = os.path.isdir(path_to_file)
        if result:
            return False
        result = os.path.exists(path_to_file)
        return result
    except Exception:
        return False


# def file_exists(path_to_file: str) -> bool:
#     """
#     Check if file exists.
#     :param path_to_file: string
#     :return: True if file exists, false if not exists or is a directory.
#     :except: IotanboError if any kind of exception occurred during check
#     """
#     try:
#         result = os.path.isdir(path_to_file)
#         if result:
#             return False
#         result = os.path.exists(path_to_file)
#         return result
#     except Exception as e:
#         raise IotanboError(str(e)) from e


def dir_exists_ne(path_to_dir: str) -> bool:
    """
    Check if dir exists.
    :param path_to_dir:
    :return: True if dir exists, false if not exists or is a file.
    :except: None
    """
    try:
        return os.path.isdir(path_to_dir)
    except Exception:
        pass
    return False


# def dir_exists(path_to_dir: str) -> bool:
#     """
#     Check if dir exists.
#     :param path_to_dir:
#     :return: True if dir exists, false if not exists or is a file.
#     :except: IotanboError if any kind of exception occurred during check
#     """
#     try:
#         return os.path.isdir(path_to_dir)
#     except Exception as e:
#         raise IotanboError(str(e)) from e


def create_symlink_ne(src: str, dest: str) -> ResultTuple:
    """
    Create a symlink to src with name `dest`;
    In case of error, error message is returned as second element of ResultTuple.
    :param src: path to file, directory or symlink
    :param dest: path to symlink to be created
    :return: ResultTuple: (None, ErrorMsg)
            ErrorMsg: str - empty string if success, error message otherwise
    """
    _, err = get_item_type_ne(src)
    if err:
        return None, err
    try:
        os.symlink(src, dest)
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return None, msg
    return None, ""


def symlink_exists_ne(path: str) -> bool:
    """
    Check if symlink exists;
    No exceptions.
    """
    try:
        return os.path.islink(path)
    except Exception:
        return False


def remove_symlink_ne(path: str) -> ResultTuple:
    """
    Remove symlink from the file system (do not raise exceptions).
    :param path: string
    :return: ResultTuple: (None, ErrorMsg):
                         ErrorMsg: str - empty string if the link
                                   was removed or not exists,
                                   or error message otherwise;
    """
    if symlink_exists_ne(path):
        try:
            os.unlink(path)
        except Exception as e:
            msg = str(e)
            if not msg:
                msg = str(e.__class__.__name__)
            return None, msg
    return None, ""


def path_base_and_leaf(path: str) -> tuple:
    """
    Split path to a base part and a file or directory name, like in the following example:
    path: '/a/b'; base: '/a'; leaf: 'b'
    :except: IotanboError
    """
    try:
        head, tail = ntpath.split(path)
        if not tail:  # in case there is trailing slash at the end of path
            return ntpath.split(head)[0], ntpath.basename(head)
        return head, tail
    except Exception as e:
        raise IotanboError(str(e)) from e


def write_text_file_ne(filename: str, contents: str = '') -> ResultTuple:
    """
    Create a new text file and write contents into it (do not raise exceptions).
    If file with specified name already exists, it will be overwritten.
    :return: ResultTuple: (None, ErrorMsg):
                         ErrorMsg: empty string if success, or error message otherwise.
    """
    try:
        with open(filename, 'w') as f:
            f.write(contents)
        return None, ""
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return None, msg


def read_text_file_ne(filename: str) -> ResultTuple:
    """
    Read a text file (do not raise exceptions).
    :param filename: path to file

    :return: ResultTuple: (Result, ErrorMsg):
                         Result: str - file contents if success;
                         ErrorMsg: str - empty string if success, or error message otherwise.
    """
    if not file_exists_ne(filename):
        return "", "file_not_exists"
    try:
        with open(filename, 'r') as f:
            return f.read(), ""
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return "", msg


def create_path_ne(path: str, overwrite=False) -> ResultTuple:
    """
    Create path in the filesystem (do not raise exceptions).
    :param path: path to be created
    :param overwrite: if true, existing old directory will be overwritten
    :return: ResultTuple: (None, ErrorMsg):
                         ErrorMsg: str - empty string if success, or error message otherwise.
    """
    try:
        if dir_exists_ne(path):
            if not overwrite:
                return None, ""
            shutil.rmtree(path)
        os.makedirs(path)
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return None, msg
    return None, ""


def remove_file(path: str) -> None:
    os.remove(path)


def remove_file_ne(path: str) -> ResultTuple:
    """
    Remove the file from the file system (do not raise exceptions).
    :param path:
    :return: ResultTuple: (None, ErrorMsg):
                         ErrorMsg: empty string if the file successfully removed
                                   and/or not exists, or error message otherwise;
    """
    if file_exists_ne(path):
        try:
            os.remove(path)
        except Exception as e:
            msg = str(e)
            if not msg:
                msg = str(e.__class__.__name__)
            return None, msg
    return None, ""


def remove_dir_ne(path) -> ResultTuple:
    """
    Remove directory and all its contents (a tree) from the file system (do not raise exceptions).
    :param path:
    :return: ResultTuple: (None, ErrorMsg):
                         ErrorMsg: empty string if the directory was removed or not exists,
                       or error message otherwise;
    """
    if dir_exists_ne(path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            msg = str(e)
            if not msg:
                msg = str(e.__class__.__name__)
            return None, msg
    return None, ""


def copy_file_ne(origin, dest) -> ResultTuple:
    """
    Copy a file (do not raise exception).
    :param origin:
    :param dest:
    :return: ResultTuple: (None, ErrorMsg):
                         ErrorMsg: empty string if existing file was copied,
                         or error message otherwise;
    """
    if not file_exists_ne(origin):
        return None, 'origin does not exist'
    if remove_file_ne(dest)[1]:
        return None, "old file can't be removed"
    try:
        shutil.copy(origin, dest)
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return None, msg
    return None, ""


def move_file_ne(origin: str, dest: str) -> ResultTuple:
    """
    Move a file (do not raise exception).
    :param origin:
    :param dest:
    :return: ResultTuple: (None, ErrorMsg):
                         ErrorMsg: empty string if existing file was moved,
                         or error message otherwise;
    """
    if not file_exists_ne(origin):
        return None, 'origin does not exist'
    if remove_file_ne(dest)[1]:
        return None, "old file can't be removed"
    try:
        shutil.move(origin, dest)
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return None, msg
    return None, ""


def copy_dir_ne(origin: str, dest: str) -> ResultTuple:
    """
    Copy a directory and its contents (tree) to the dest, do not raise exception.
    If old 'dest' exists, it will be removed first.
    :param origin:
    :param dest:
    :return: ResultTuple: (None, ErrorMsg):
                         ErrorMsg: empty string if directory was copied
                         and exists or error message otherwise;
    """
    if not dir_exists_ne(origin):
        return None, 'origin does not exist'
    if remove_dir_ne(dest)[1]:
        return None, "old directory can't be removed"
    try:
        shutil.copytree(origin, dest)
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return None, msg
    return None, ""


def move_dir_ne(origin: str, dest: str) -> ResultTuple:
    """
    Move a directory and its contents (a tree) into a dest (do not raise exception).
    If old 'dest' exists, it will be removed first.
    This function is equivalent to 'rename'.
    :param origin:
    :param dest:
    :return: ResultTuple: (None, ErrorMsg):
                         ErrorMsg: empty string if success or error message otherwise;
    """
    if not dir_exists_ne(origin):
        return None, 'origin does not exist'
    if remove_dir_ne(dest)[1]:
        return None, "old directory can't be removed"
    try:
        shutil.move(origin, dest)
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return None, msg
    return None, ""


def get_subdirs_ne(path: str) -> ResultTuple:
    """
    Get list of all first child subdirectories that the directory contains.
    Does not raise exceptions.
    :param path:
    :return: ResultTuple: (subdirs, ErrorMsg):
                         subdirs: list of subdirectory names
                         ErrorMsg: empty string if success or error message otherwise;
    """
    if not dir_exists_ne(path):
        return [], 'path not exists'
    # https://stackoverflow.com/questions/973473/getting-a-list-of-all-subdirectories-in-the-current-directory
    try:
        subdirs = [subdir.name for subdir in os.scandir(path) if subdir.is_dir()]
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return [], msg
    return subdirs, ""


def get_file_list_ne(path: str) -> ResultTuple:
    """
    List of files located in the directory. The list includes symlinks,
    but does not include directories.
    Does not raise exceptions.
    :param path:
    :return: ResultTuple: (file_list, ErrorMsg):
                         file_list: list of files located in the directory;
                         ErrorMsg: empty string if success or error message otherwise;
    """
    if not dir_exists_ne(path):
        return [], 'path not exists'
    try:
        file_list = [file.name for file in os.scandir(path) if file.is_file()]
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return [], msg
    return file_list, ""


def get_total_items_ne(path: str) -> ResultTuple:
    """
    Total number of child elements in the directory.
    :param path:
    :return: ResultTuple: (total_items: int, ErrorMsg):
                         total_items: number of child items in the directory;
                         ErrorMsg: empty string if success or error message otherwise;
    """
    if not dir_exists_ne(path):
        return 0, 'path not exists'
    try:
        total_items = len([item.name for item in os.scandir(path)])
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return 0, msg
    return total_items, ""


def dir_empty_ne(path: str) -> bool:
    """
    Check if directory is empty. Do not raise exceptions.
    :param path:
    :return: True if dir is empty or does not exist, False if dir exists and not empty
    """
    try:
        if os.path.exists(path) and os.path.isdir(path):
            if not os.listdir(path):
                return True
            else:
                return False
    except Exception:
        pass
    return True


def get_item_type_ne(path: str) -> ResultTuple:
    """
    Get type of the file system item ('file', 'dir, 'symlink').
    Does not raise exceptions.
    :param path:
    :return: ResultTuple: (Result: str, ErrorMsg):
             Result:  str - the file system item type ('file', 'dir, 'symlink');
                            empty string is returned if type is unknown or item
                            does not exist;
             ErrorMsg: str - empty string if success, error message otherwise
    """
    try:
        if symlink_exists_ne(path):  # symlink must be first because symlink is also a file
            item_type = 'symlink'
        elif file_exists_ne(path):
            item_type = 'file'
        elif dir_exists_ne(path):
            item_type = 'dir'
        else:
            return "", "not exists"
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return "", msg

    return item_type, ""


def get_user_home_dir() -> str:
    return str(Path.home())


def get_cwd() -> str:
    return os.getcwd()

# ---------------------------------------------------------------------------------------------------------------------
# Environment variables


def set_env_var(name: str, value: str) -> None:
    os.environ[name] = value


def get_env_var(name: str) -> str:
    if name not in os.environ:
        return ''
    return os.environ[name]


def unset_env_var(name: str) -> None:
    if name in os.environ:
        del os.environ[name]


def env_var_exists(name: str) -> bool:
    return name in os.environ


# ---------------------------------------------------------------------------------------------------------------------
# Execute shell commands

# 'cmd_and_args' must be a list, each argument must be a separate list element
def execute_shell_cmd(cmd_and_args: list):
    subprocess.check_call(cmd_and_args, env=dict(os.environ))


# ---------------------------------------------------------------------------------------------------------------------
# Zip, tar, gzip archives

def unzip_tar_gz(file: str, dest_dir: str, remove_after_extract=False) -> ResultTuple:
    """
    Unzip .tar.gz archive into the `dest_dir`
    :param file: source .tar.gz archive
    :param dest_dir: destination dir
    :param remove_after_extract: bool
    :return: ResultTuple: (None, ErrorMsg):
                 ErrorMsg: empty string if success or error message otherwise;
    """
    if file_exists_ne(dest_dir):
        return None, "destination is not directory: " + str(dest_dir)

    if not file_exists_ne(file):
        return None, "source file not exists"

    if not dir_exists_ne(dest_dir):
        if create_path_ne(dest_dir)[1]:
            return None, "can't create destination directory: " + str(dest_dir)
    try:
        with tarfile.open(file, 'r:*') as t:
            t.extractall(dest_dir)
        if remove_after_extract:
            remove_file_ne(file)
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return None, msg + str(dest_dir)
    return None, ""


def zip_file_tar_gz(file, dest_file, remove_after=False) -> ResultTuple:
    """
    Create .tar.zip archive from file.
    :param file: source file
    :param dest_file: destination file to be written
    :param remove_after: if True, source file will be removed after archive created
    :return: ResultTuple: (None, ErrorMsg):
                 ErrorMsg: empty string if success or error message otherwise;
    """
    if not file_exists_ne(file):
        return None, "source file not exists: " + str(file)
    try:
        with tarfile.open(dest_file, "w:gz") as tar:
            tar.add(file, arcname=os.path.basename(file))
        if remove_after:
            remove_file(file)
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return None, msg + " when creating file " + str(dest_file)
    return None, ""


def zip_dir_tar_gz(source_dir: str, dest_file: str, remove_after=False) -> ResultTuple:
    """
    Create .tar.zip archive from directory tree.
    :param source_dir:
    :param dest_file:
    :param remove_after: if True, source dir will be removed after archive created
    :return: ResultTuple: (None, ErrorMsg):
                 ErrorMsg: empty string if success or error message otherwise;
    """
    if not dir_exists_ne(source_dir):
        return None, "source directory not exists: " + str(source_dir)
    try:
        with tarfile.open(dest_file, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        if remove_after:
            remove_dir_ne(source_dir)
    except Exception as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return None, msg + " when creating file " + str(dest_file)
    return None, ""


# ---------------------------------------------------------------------------------------------------------------------
# File download

def download_into_file(url, dest_file) -> ResultTuple:
    """
    Download url synchronously and save result into file.
    :param url:
    :param dest_file: file to write url contents
    :return: Dict:
            ["response_header"]: str - http response header if success
            ["error"]: str - empty string if success or error message otherwise
    :return: ResultTuple: (response_header: str, ErrorMsg):
                 response_header: str - http response header if success
                 ErrorMsg: empty string if success or error message otherwise;
    """
    response_header = ""
    try:
        response_header = urllib.request.urlretrieve(url, dest_file)[1]
    except error.URLError as e:
        msg = str(e)
        if not msg:
            msg = str(e.__class__.__name__)
        return None, msg
    return response_header, ""


# ---------------------------------------------------------------------------------------------------------------------
# Git operations (simplified)

def git_clone(git_url: str, path: str) -> None:
    if dir_exists_ne(path):
        remove_dir_ne(path)
    cmd = ['git', 'clone', git_url, path]
    execute_shell_cmd(cmd)


def git_pull(path) -> None:
    if not dir_exists_ne(path):
        return
    old_path = os.getcwd()
    os.chdir(path)
    cmd = ['git', 'pull']
    execute_shell_cmd(cmd)
    os.chdir(old_path)
