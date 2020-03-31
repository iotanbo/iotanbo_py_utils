import pytest

from iotanbo_py_utils import file_utils

# from iotanbo_py_utils.error import IotanboError


@pytest.fixture(scope="session")
def existing_dir(tmpdir_factory):
    ed = tmpdir_factory.mktemp("existing_dir")
    print("\n*** Created temporary dir for current session: ", ed)
    return ed


@pytest.fixture(scope="session")
def existing_text_file(existing_dir):
    ef = existing_dir.join("existing_file.txt")
    _, err = file_utils.write_text_file_ne(ef, "test")
    assert not err
    print("\n*** Created temporary text file for current session: ", ef)
    return ef


@pytest.fixture(scope="session")
def existing_text_file_symlink(existing_dir, existing_text_file):
    es = existing_dir + "/existing_text_file_symlink.txt"
    _, err = file_utils.create_symlink_ne(existing_text_file, es)
    assert not err
    print("\n*** Created temporary symlink for current session: ", es)
    return es


@pytest.fixture(scope="session")
def not_existing_dir():
    return "/tmp/this_dir_does_not_exist"


@pytest.fixture(scope="session")
def not_existing_file():
    return "/tmp/this_file_does_not_exist"


def test_file_exists_ne(existing_text_file, not_existing_file):
    assert file_utils.file_exists_ne(existing_text_file)
    assert not file_utils.file_exists_ne(not_existing_file)
    # Sad path:
    # Bad parameter test
    assert not file_utils.file_exists_ne(None)
    assert not file_utils.file_exists_ne({"Dummy": "dict"})


# def test_file_exists(existing_text_file, not_existing_file):
#     assert file_utils.file_exists(existing_text_file)
#     assert not file_utils.file_exists(not_existing_file)
#     # Sad path:
#     # Bad parameter test
#     with pytest.raises(IotanboError):
#         file_utils.file_exists(None)
#     with pytest.raises(IotanboError):
#         file_utils.file_exists({"Dummy": "dict"})


def test_dir_exists_ne(existing_dir, not_existing_dir, existing_text_file):
    assert file_utils.dir_exists_ne(existing_dir)
    assert not file_utils.dir_exists_ne(not_existing_dir)
    # Sad path:
    # File instead of dir
    assert not file_utils.dir_exists_ne(existing_text_file)
    # Bad parameter test
    assert not file_utils.dir_exists_ne(None)
    assert not file_utils.dir_exists_ne({"Dummy": "dict"})


# def test_dir_exists(existing_dir, not_existing_dir, existing_text_file):
#     assert file_utils.dir_exists(existing_dir)
#     assert not file_utils.dir_exists(not_existing_dir)
#     # Sad path:
#     # File instead of dir
#     assert not file_utils.dir_exists(existing_text_file)
#     # with pytest.raises(IotanboError):
#     #     file_utils.dir_exists(existing_text_file)
#     # Bad parameter test
#     with pytest.raises(IotanboError):
#         file_utils.dir_exists(None)
#     with pytest.raises(IotanboError):
#         file_utils.dir_exists({"Dummy": "dict"})


def test_symlink_exists_ne(existing_text_file_symlink):
    assert file_utils.symlink_exists_ne(existing_text_file_symlink)


def test_create_remove_symlink_ne(existing_text_file, existing_dir):
    # Create and remove symlink to file
    text_file_symlink = existing_dir + "/file_symlink.txt"
    _, err = file_utils.create_symlink_ne(existing_text_file, text_file_symlink)
    assert not err
    assert file_utils.symlink_exists_ne(text_file_symlink)
    assert file_utils.remove_symlink_ne(text_file_symlink)
    assert not file_utils.symlink_exists_ne(text_file_symlink)

    # Create and remove symlink to dir
    dir_symlink = existing_dir + "/symlink_to_parent_dir"
    _, err = file_utils.create_symlink_ne(existing_dir, dir_symlink)
    assert not err
    assert file_utils.symlink_exists_ne(dir_symlink)
    assert file_utils.remove_symlink_ne(dir_symlink)
    assert not file_utils.symlink_exists_ne(dir_symlink)


def test_path_base_and_leaf():
    path = "/tmp/base/leaf"
    base, leaf = file_utils.path_base_and_leaf(path)
    assert base == "/tmp/base"
    assert leaf == "leaf"
    # Test with forward slash at the end
    path = "/tmp/base/leaf/"
    base, leaf = file_utils.path_base_and_leaf(path)
    assert base == "/tmp/base"
    assert leaf == "leaf"


def test_read_write_text_file_ne(existing_dir):
    tmpfile = existing_dir + "/tmpfile.txt"
    _, err = file_utils.write_text_file_ne(tmpfile, "test")
    assert not err
    contents, err = file_utils.read_text_file_ne(tmpfile)
    assert not err
    assert contents == "test"
    file_utils.remove_file_ne(tmpfile)


def test_create_path_ne(existing_dir):
    path = existing_dir + "/some/complicated/path"
    _, err = file_utils.create_path_ne(path)
    assert not err
    assert not file_utils.remove_dir_ne(existing_dir + "/some")[1]


def test_copy_file_ne(existing_dir, existing_text_file):
    dest = existing_dir + "/existing_text_file_copy.txt"
    _, err = file_utils.copy_file_ne(existing_text_file, dest)
    assert not err
    # Read created copy to verify its contents
    contents, err = file_utils.read_text_file_ne(dest)
    assert contents == "test"
    # Remove created copy
    assert not file_utils.remove_file_ne(dest)[1]


def test_move_file_ne(existing_dir):
    # Create temp file
    orig_file = existing_dir + "move_file_test.txt"
    dest = existing_dir + "moved_file.txt"
    contents = "move_file_test.txt"
    _, err = file_utils.write_text_file_ne(orig_file, contents)
    assert not err
    # Move it
    _, err = file_utils.move_file_ne(orig_file, dest)
    assert not err
    # Assert original file not exists
    assert not file_utils.file_exists_ne(orig_file)
    # Assert moved file exists and has correct contents
    assert file_utils.file_exists_ne(dest)
    file_contents, err = file_utils.read_text_file_ne(dest)
    assert contents == file_contents
    # Remove temp file
    assert file_utils.remove_file_ne(dest)


def test_copy_dir_ne(existing_dir):
    # Create path
    orig_path = existing_dir + "/copy/dir/test"
    _, err = file_utils.create_path_ne(orig_path)
    assert not err
    src = existing_dir + "/copy"
    dest = existing_dir + "/dest"
    # Copy tree
    assert not file_utils.copy_dir_ne(src, dest)[1]
    # Assert both exist
    assert file_utils.dir_exists_ne(orig_path)
    assert file_utils.dir_exists_ne(dest + "/dir/test")
    # Remove src and dest
    assert not file_utils.remove_dir_ne(src)[1]
    assert not file_utils.remove_dir_ne(dest)[1]


def test_move_dir_ne(existing_dir):
    # Create path
    orig_path = existing_dir + "/move/dir/test"
    _, err = file_utils.create_path_ne(orig_path)
    assert not err
    src = existing_dir + "/move"
    dest = existing_dir + "/dest"
    # Copy tree
    _, err = file_utils.move_dir_ne(src, dest)
    assert not err
    # Assert only dest exists
    assert not file_utils.dir_exists_ne(orig_path)
    assert file_utils.dir_exists_ne(dest + "/dir/test")
    # Remove dest
    _, err = file_utils.remove_dir_ne(dest)
    assert not err


def test_get_subdirs(existing_dir):
    # Create path
    path1 = existing_dir + "/subdirs/test1/test1_1"
    assert not file_utils.create_path_ne(path1)[1]
    path2 = existing_dir + "/subdirs/test2/test1_2"
    assert not file_utils.create_path_ne(path2)[1]
    subdirs_list, err = file_utils.get_subdirs_ne(existing_dir + "/subdirs")
    # There must be no error when getting subdirs
    assert not err
    # There must be 2 subdirs, check their names
    assert len(subdirs_list) == 2
    assert "test1" in subdirs_list
    assert "test2" in subdirs_list
    # Cleanup
    assert not file_utils.remove_dir_ne(existing_dir + "/subdirs")[1]


def test_get_file_list(existing_dir):
    # Create path
    path = existing_dir + "/file_list_test"
    assert not file_utils.create_path_ne(path)[1]
    # Create a file, a dir and a symlink in that dir
    file_utils.create_path_ne(path + "/test_dir")
    file_utils.write_text_file_ne(path + "/test_file.txt", "test_file.txt")
    file_utils.create_symlink_ne(path + "/test_file.txt", path + "/test_file_symlink.txt")
    # Assert that only file is recognized as file
    file_list, err = file_utils.get_file_list_ne(path)
    assert not err
    assert len(file_list) == 2
    assert "test_file.txt" in file_list
    assert "test_file_symlink.txt" in file_list

    # Cleanup
    file_utils.remove_dir_ne(path)


def test_get_total_items(existing_dir):
    """
    Tests:
    get_total_items,
    dir_empty,
    get_item_type
    """
    # Create path
    path = existing_dir + "/get_total_items_test"
    assert not file_utils.create_path_ne(path)[1]
    # Create a file, a dir and a symlink in that dir
    file_utils.create_path_ne(path + "/test_dir")
    file_utils.write_text_file_ne(path + "/test_file.txt", "test_file.txt")
    file_utils.create_symlink_ne(path + "/test_file.txt", path + "/test_file_symlink.txt")
    # Assert there are 3 items
    total_items, err = file_utils.get_total_items_ne(path)
    assert not err
    assert total_items == 3
    # test_dir_empty test
    assert not file_utils.dir_empty_ne(path)
    assert file_utils.dir_empty_ne(path + "/not_exists")
    assert file_utils.dir_empty_ne(path + "/test_dir")
    # get_item_type test
    assert file_utils.get_item_type_ne(path)[0] == "dir"
    assert file_utils.get_item_type_ne(path + "/test_file.txt")[0] == "file"
    assert file_utils.get_item_type_ne(path + "/test_file_symlink.txt")[0] == "symlink"
    assert not file_utils.get_item_type_ne(path + "/not_exists")[0]
    # Cleanup
    file_utils.remove_dir_ne(path)


def test_env_variables():
    """
    set_env_var,
    get_env_var,
    unset_env_var,
    env_var_exists
    """
    env_var = "dummy_env_var"
    assert not file_utils.env_var_exists(env_var)
    file_utils.set_env_var(env_var, "exists")
    assert file_utils.env_var_exists(env_var)
    assert file_utils.get_env_var(env_var) == "exists"
    file_utils.unset_env_var(env_var)
    assert not file_utils.env_var_exists(env_var)


def test_tar_gz(existing_dir):
    """
    unzip_tar_gz,
    zip_file_tar_gz,
    zip_dir_tar_gz
    """

    # Create a directory with a text file
    path = existing_dir + "/tar_gz_test"
    assert not file_utils.create_path_ne(path)[1]
    # Create a dir and a file
    src_dir = path + "/test_dir"
    file_utils.create_path_ne(src_dir + "/inner_dir")
    src_file = src_dir + "/test_file.txt"
    src_file_contents = "test_file.txt"
    file_utils.write_text_file_ne(src_file, src_file_contents)

    # Create .tar.gz archive from file
    assert not file_utils.zip_file_tar_gz(src_file, path + "/result_file.tar.gz")[1]

    # Create .tar.gz archive from directory
    assert not file_utils.zip_dir_tar_gz(src_dir, path + "/result_dir.tar.gz")[1]

    # Unzip .tar.gz and verify contents
    assert not file_utils.unzip_tar_gz(path + "/result_file.tar.gz",
                                       path + "/unzipped")[1]
    assert file_utils.file_exists_ne(path + "/unzipped/test_file.txt")

    file_contents, err = file_utils.read_text_file_ne(path + "/unzipped/test_file.txt")
    assert file_contents == src_file_contents

    # Unzip .tar.gz dir and verify contents
    assert not file_utils.unzip_tar_gz(path + "/result_dir.tar.gz",
                                       path + "/unzipped")[1]
    assert file_utils.dir_exists_ne(path + "/unzipped/test_dir")
    assert file_utils.file_exists_ne(path + "/unzipped/test_dir/test_file.txt")
    file_contents, err = file_utils.read_text_file_ne(path + "/unzipped/test_dir/test_file.txt")
    assert file_contents == src_file_contents

    # Cleanup
    assert not file_utils.remove_dir_ne(existing_dir + "/tar_gz_test")[1]


def test_get_user_home_dir():
    user_home_dir = file_utils.get_user_home_dir()
    # print(f"\nUser home dir: {user_home_dir}\n")
    assert file_utils.dir_exists_ne(user_home_dir)


# # This test requires internet access, so it is normally disabled
# def test_download_into_file(existing_dir):
#     dest_file = existing_dir + '/tmp.md'
#     header, err = file_utils.download_into_file("https://github.com/iotanbo/cpplibhub/blob/master/docs/GET_STARTED.md",
#                                                 dest_file)
#     assert not err
#     # Cleanup
#     file_utils.remove_file_ne(dest_file)
