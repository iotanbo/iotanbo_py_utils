"""
Tests for config_utils.py
Author: iotanbo
"""

import os

from iotanbo_py_utils import config_utils
from iotanbo_py_utils import file_utils


def test_read_config_into_dict_ne():
    cfg_str = """
    [default]
    key1 = val1
    empty_key =
    """
    result, err = config_utils.read_config_into_dict_ne(cfg_file="", cfg_string=cfg_str)
    assert not err
    assert 'default' in result
    assert 'key1' in result['default']
    assert result['default']['key1'] == 'val1'
    assert 'empty_key' in result['default']
    assert result['default']['empty_key'] == ''


def test_read_config_into_dict_nosect_ne():
    cfg_str = """
    [DEFAULT]
    key1 = val1
    empty_key =
    """
    result, err = config_utils.read_config_into_dict_nosect_ne(cfg_file="", cfg_string=cfg_str)
    assert not err
    assert 'key1' in result
    assert result['key1'] == 'val1'
    assert 'empty_key' in result
    assert result['empty_key'] == ''


def test_write_config(tmpdir_factory):
    conf0 = {
        'GENERAL': {
            'key1': 'val1',
            'Empty_key': ''
        }
    }
    tmp0 = tmpdir_factory.mktemp("tmp0")
    cfg_file0 = os.path.join(tmp0, "cfg_file0.cfg")
    _, err = config_utils.write_config(config=conf0, cfg_file=cfg_file0, preserve_case=True)
    assert not err
    assert file_utils.file_exists_ne(cfg_file0)
    contents, err = file_utils.read_text_file_ne(cfg_file0)
    assert not err

    # read the config file
    cfg0, err = config_utils.read_config_into_dict_ne(cfg_file=cfg_file0, cfg_string=None,
                                                      preserve_case=True)
    assert "GENERAL" in cfg0
    assert 'key1' in cfg0["GENERAL"]
    assert 'Empty_key' in cfg0["GENERAL"]
    assert cfg0["GENERAL"]['Empty_key'] == ""


def test_write_config_from_dict_nosect_ne(tmpdir_factory):
    conf0 = {'key1': 'val1',
             'Empty_key': ''
             }

    tmp0 = tmpdir_factory.mktemp("tmp0")
    cfg_file0 = os.path.join(tmp0, "cfg_file0.cfg")
    _, err = config_utils.write_config_from_dict_nosect_ne(config=conf0,
                                                           cfg_file=cfg_file0,
                                                           preserve_case=True)
    assert not err
    assert file_utils.file_exists_ne(cfg_file0)
    contents, err = file_utils.read_text_file_ne(cfg_file0)
    assert not err

    # read the config file
    cfg0, err = config_utils.read_config_into_dict_nosect_ne(cfg_file=cfg_file0, cfg_string=None,
                                                             preserve_case=True)
    assert 'key1' in cfg0
    assert 'Empty_key' in cfg0
    assert cfg0['Empty_key'] == ""
