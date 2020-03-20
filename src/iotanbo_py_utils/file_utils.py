import ntpath
import os
import shutil
import subprocess  # for execute_shell_cmd
import tarfile
import urllib.request
from pathlib import Path
from urllib import error

# import symlink


def file_exists(path_to_file) -> bool:
    """
    True if file exists, false otherwise (or if it is a directory).
    """
    if os.path.isdir(path_to_file):
        return False
    return os.path.exists(path_to_file)


def dir_exists(path_to_dir) -> bool:
    """
    True if directory exists, false otherwise (or if it is a file).
    """
    return os.path.isdir(path_to_dir)


def create_symlink_noexcept(src, dest) -> dict:
    """
    Create a symlink to src called `dest`
    :param src: file, directory or symlink
    :param dest: name of symlink to be created
    :return: Dict:
            ["error"]: str - empty string if success, error message otherwise
    """
    result = {"error": ""}

    if not get_item_type(src)["exists"]:
        result["error"] = "source file or directory does not exist"
        return result
    try:
        os.symlink(src, dest)
    except OSError as e:
        result["error"] = str(e)
        return result
    return result


def symlink_exists(path) -> bool:
    return os.path.islink(path)


def remove_symlink_noexcept(path) -> dict:
    """
    Remove symlink from the file system (do not raise exceptions).
    :param path: string
    :return: Dict:
            ['error']: empty string if the link was removed or not exists,
                    or error message otherwise;
    """
    result = {'error': ''}
    if symlink_exists(path):
        try:
            os.unlink(path)
        except OSError as e:
            result['error'] = str(e)
    return result


def path_base_and_leaf(path) -> tuple:
    """
    Splits path to a base part and a file or directory name, as in the following example:
    path: '/a/b'; base: '/a'; leaf: 'b'
    """
    head, tail = ntpath.split(path)
    if not tail:  # in case there is trailing slash at the end of path
        return ntpath.split(head)[0], ntpath.basename(head)
    return head, tail


def write_text_file_noexcept(filename, contents='') -> dict:
    """
    Create a new text file and write contents into it (do not raise exceptions).
    If file with specified name already exists, it will be overwritten.
    :return: Dict:
            ["error"]: empty string if success, or error message otherwise.
    """
    result = {"error": ""}
    try:
        f = open(filename, 'w')
        f.write(contents)
        f.close()
        return result
    except Exception as e:
        result["error"] = str(e)
        return result


def read_text_file_noexcept(filename) -> dict:
    """
    Read a text file (do not raise exceptions).
    :param filename: path to file
    :return: Dict:
            ["error"]: empty string if success, or error message otherwise;
            ["contents"]: file contents if success;
    """
    result = {'contents': '', 'error': ''}
    if not file_exists(filename):
        result['error'] = 'file_not_exists'
        return result
    try:
        file = open(filename, 'r')
        result['contents'] = file.read()
        file.close()
    except Exception as e:
        result['contents'] = ''
        result['error'] = str(e)
    return result


def create_path_noexcept(path, overwrite=False) -> dict:
    """
    Create path in the filesystem (do not raise exceptions).
    :param path: path to be created
    :param overwrite: if true, existing old directory will be overwritten
    :return: Dict:
            ["error"]: empty string if success, or error message otherwise.
    """
    result = {'error': ''}
    try:
        if dir_exists(path):
            if not overwrite:
                return result
            # remove_dir_noexcept(path)
            shutil.rmtree(path)
        os.makedirs(path)
    except Exception as e:
        result['error'] = str(e)
        return result
    return result


def remove_file(path) -> None:
    os.remove(path)


def remove_file_noexcept(filename) -> dict:
    """
    Remove the file from the file system (do not raise exceptions).
    :param filename:
    :return: Dict:
            ['error']: empty string if the file successfully removed and/or not exists,
                       or error message otherwise;
    """
    result = {'error': ''}
    if file_exists(filename):
        try:
            os.remove(filename)
        except OSError as e:
            result['error'] = str(e)
    return result


def remove_dir_noexcept(path) -> dict:
    """
    Remove directory and all its contents (a tree) from the file system (do not raise exceptions).
    :param path:
    :return: Dict:
            ['error']: empty string if the directory was removed or not exists,
                       or error message otherwise;
    """
    result = {'error': ''}
    if dir_exists(path):
        try:
            shutil.rmtree(path)
        except OSError as e:
            result['error'] = str(e)
    return result


def copy_file_noexcept(origin, dest) -> dict:
    """
    Copy a file (do not raise exception).
    :param origin:
    :param dest:
    :return: Dict:
            ['error']: empty string if existing file was copied, or error message otherwise;
    """
    result = {'error': ''}
    if not file_exists(origin):
        result['error'] = 'origin does not exist'
        return result
    if remove_file_noexcept(dest)['error']:
        result['error'] = "old file can't be removed"
        return result
    try:
        shutil.copy(origin, dest)
    except OSError as e:
        result['error'] = str(e)
    return result


def move_file_noexcept(origin, dest) -> dict:
    """
    Move a file (do not raise exception).
    :param origin:
    :param dest:
    :return: Dict:
            ['error']: empty string if existing file was moved, or error message otherwise;
    """
    result = {'error': ''}
    if not file_exists(origin):
        result['error'] = 'origin does not exist'
        return result
    if remove_file_noexcept(dest)['error']:
        result['error'] = "old file can't be removed"
        return result
    try:
        shutil.move(origin, dest)
    except OSError as e:
        result['error'] = str(e)
    return result


def copy_dir_noexcept(origin, dest) -> dict:
    """
    Copy a directory and its contents (a tree) to a dest (do not raise exception).
    If old 'dest' exists, it will be removed first.
    :param origin:
    :param dest:
    :return: Dict:
            ['error']: empty string if directory was copied and exists or error message otherwise;
    """
    result = {'error': ''}
    if not dir_exists(origin):
        result['error'] = 'origin does not exist'
        return result
    if remove_dir_noexcept(dest)['error']:
        result['error'] = "old directory can't be removed"
        return result
    try:
        shutil.copytree(origin, dest)
    except OSError as e:
        result['error'] = str(e)
    return result


def move_dir_noexcept(origin, dest) -> dict:
    """
    Move a directory and its contents (a tree) into a dest (do not raise exception).
    If old 'dest' exists, it will be removed first.
    This function is equivalent to 'rename'.
    :param origin:
    :param dest:
    :return: Dict:
            ['error']: empty string if success or error message otherwise;
    """
    result = {'error': ''}
    if not dir_exists(origin):
        result['error'] = 'origin does not exist'
        return result
    if remove_dir_noexcept(dest)['error']:
        result['error'] = "old directory can't be removed"
        return result
    try:
        shutil.move(origin, dest)
    except OSError as e:
        result['error'] = str(e)
    return result


def get_subdirs(path) -> dict:
    """
    List of all first child subdirectories that the directory contains.
    :param path:
    :return: Dict:
            ['subdirs']: list of subdirectory names
            ['error']: empty string if success or error message otherwise;
    """
    result = {'subdirs': [], 'error': ''}
    if not dir_exists(path):
        result['error'] = 'path not exists'
        return result
    # https://stackoverflow.com/questions/973473/getting-a-list-of-all-subdirectories-in-the-current-directory
    result['subdirs'] = [subdir.name for subdir in os.scandir(path) if subdir.is_dir()]
    return result


def get_file_list(path) -> dict:
    """
    List of files located in the directory. The list includes symlinks,
    but does not include directories.
    :param path:
    :return: Dict:
            ['file_list']: list of files located in the directory;
            ['error']: empty string if success or error message otherwise;
    """
    result = {'file_list': [], 'error': ''}
    if not dir_exists(path):
        result['error'] = 'path not exists'
        return result
    result['file_list'] = [file.name for file in os.scandir(path) if file.is_file()]
    return result


def get_total_items(path) -> dict:
    """
    Total number of child elements in the directory.
    :param path:
    :return: Dict:
            ['total_items']: number of child items in the directory;
            ['error']: empty string if success or error message otherwise;
    """
    result = {'total_items': 0, 'error': ''}
    if not dir_exists(path):
        result['error'] = 'path not exists'
        return result
    result['total_items'] = len([item.name for item in os.scandir(path)])
    return result


def dir_empty(path) -> bool:
    """
    Check if directory is empty.
    :param path:
    :return: True if dir is empty or does not exist, False if dir exists and not empty
    """
    if os.path.exists(path) and os.path.isdir(path):
        if not os.listdir(path):
            return True
        else:
            return False
    return True


def get_item_type(path) -> dict:
    """
    Type of the file system item.
    Supported type names: 'file', 'dir, 'symlink'
    :param path:
    :return: Dict:
            ['item_type']: string that describes the type; empty string is returned if type is unknown or item
                            does not exist;
            ['exists']: boolean - True if item exists or false otherwise.
    """
    result = {'exists': False, 'item_type': ''}
    if symlink_exists(path):  # symlink must be first because symlink is also a file
        result['exists'] = True
        result['item_type'] = 'symlink'
    elif file_exists(path):
        result['exists'] = True
        result['item_type'] = 'file'
    elif dir_exists(path):
        result['exists'] = True
        result['item_type'] = 'dir'

    return result


def get_user_home_dir() -> str:
    return str(Path.home())

# ---------------------------------------------------------------------------------------------------------------------
# Environment variables


def set_env_var(name, value) -> None:
    os.environ[name] = value


def get_env_var(name) -> str:
    if name not in os.environ:
        return ''
    return os.environ[name]


def unset_env_var(name) -> None:
    if name in os.environ:
        del os.environ[name]


def env_var_exists(name) -> bool:
    return name in os.environ


# ---------------------------------------------------------------------------------------------------------------------
# Execute shell commands

# 'cmd_and_args' must be a list, each argument must be a separate list element
def execute_shell_cmd(cmd_and_args):
    subprocess.check_call(cmd_and_args, env=dict(os.environ))


# ---------------------------------------------------------------------------------------------------------------------
# Zip, tar, gzip archives

def unzip_tar_gz(file, dest_dir, remove_after_extract=False) -> dict:
    """
    Unzip .tar.gz archive into the `dest_dir`
    :param file: source .tar.gz archive
    :param dest_dir: destination dir
    :param remove_after_extract:
    :return: Dict:
            ["error"]: str - empty string if success or error message otherwise
    """
    result = {"error": ""}
    if file_exists(dest_dir):
        result["error"] = "destination is not directory: " + str(dest_dir)
        return result

    if not file_exists(file):
        result["error"] = "source file not exists"
        return result

    if not dir_exists(dest_dir):
        if create_path_noexcept(dest_dir)["error"]:
            result["error"] = "can't create destination directory: " + str(dest_dir)
            return result
    try:
        with tarfile.open(file, 'r:*') as t:
            t.extractall(dest_dir)
            t.close()
        if remove_after_extract:
            remove_file_noexcept(file)
    except OSError as e:
        result["error"] = str(e) + str(dest_dir)
        return result
    return result


def zip_file_tar_gz(file, dest_file, remove_after=False) -> dict:
    """
    Create .tar.zip archive from file.
    :param file: source file
    :param dest_file: destination file to be written
    :param remove_after: if True, source file will be removed after archive created
    :return: Dict:
            ["error"]: str - empty string if success or error message otherwise
    """
    result = {"error": ""}
    if not file_exists(file):
        result["error"] = "source file not exists: " + str(file)
        return result
    try:
        with tarfile.open(dest_file, "w:gz") as tar:
            tar.add(file, arcname=os.path.basename(file))
        if remove_after:
            remove_file(file)
    except OSError as e:
        result["error"] = str(e) + " when creating file " + str(dest_file)
        return result
    return result


def zip_dir_tar_gz(source_dir: str, dest_file: str, remove_after=False) -> dict:
    """
    Create .tar.zip archive from directory tree.
    :param source_dir:
    :param dest_file:
    :param remove_after: if True, source dir will be removed after archive created
    :return: Dict:
            ["error"]: str - empty string if success or error message otherwise
    """
    result = {"error": ""}
    if not dir_exists(source_dir):
        print(f"** TRACING source_dir: {source_dir}")
        result["error"] = "source directory not exists: " + str(source_dir)
        return result
    try:
        with tarfile.open(dest_file, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
        if remove_after:
            remove_dir_noexcept(source_dir)
    except OSError as e:
        result["error"] = str(e) + " when creating file " + str(dest_file)
        return result
    return result


# ---------------------------------------------------------------------------------------------------------------------
# File download

def download_into_file(url, dest_file) -> dict:
    """
    Download url synchronously and save result into file.
    :param url:
    :param dest_file: file to write url contents
    :return: Dict:
            ["response_header"]: str - http response header if success
            ["error"]: str - empty string if success or error message otherwise
    """

    result = {"error": "", "response_header": ""}
    try:
        result["response_header"] = urllib.request.urlretrieve(url, dest_file)[1]
    except error.URLError as e:
        result["error"] = str(e)
    return result


# ---------------------------------------------------------------------------------------------------------------------
# Git operations (simplified)

def git_clone(git_url, path):
    if dir_exists(path):
        remove_dir_noexcept(path)
    cmd = ['git', 'clone', git_url, path]
    execute_shell_cmd(cmd)


def git_pull(path):
    if not dir_exists(path):
        return
    old_path = os.getcwd()
    os.chdir(path)
    cmd = ['git', 'pull']
    execute_shell_cmd(cmd)
    os.chdir(old_path)
