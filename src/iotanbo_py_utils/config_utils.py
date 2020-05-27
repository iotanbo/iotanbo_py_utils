"""
Author: iotanbo
"""

from configparser import ConfigParser

from iotanbo_py_utils.error import ResultTuple
from iotanbo_py_utils import file_utils


def read_config_into_dict_ne(*, cfg_file, cfg_string=None,
                             allow_no_value=True, preserve_case=False) -> ResultTuple:
    """
    Read configuration from specified config file into dict preserving sections.
    dict format is like {'section1': {'key1': 'val1', ... }}
    :param cfg_file: Absolute path to the config file.
    :param cfg_string: Read config from string instead of file.
    :param preserve_case: if True, key and value character case will be preserved
    :param allow_no_value: if True, empty values are not treated as errors.
    :return: ResultTuple (dict, ErrorMsg)
    """

    parser = ConfigParser(allow_no_value=allow_no_value)
    if preserve_case:
        parser.optionxform = str

    try:
        if not cfg_file:
            if cfg_string:
                parser.read_string(cfg_string)
        else:
            parser.read(cfg_file)
    except Exception as e:
        return {}, e.__class__.__name__ + ": " + str(e)

    result = {}

    try:
        # Special treatment for the 'DEFAULT' section
        if 'DEFAULT' in parser:
            result['default'] = dict(parser['DEFAULT'])

        # All other sections
        for section in parser.sections():
            section_entries = {}
            for key, value in parser.items(section):
                section_entries[key] = value
            result[section] = section_entries
    except Exception as e:
        return {}, e.__class__.__name__ + ": " + str(e)
    return result, ""


def read_config_into_dict_nosect_ne(*, cfg_file, cfg_string=None,
                                    allow_no_value=True, preserve_case=False) -> ResultTuple:
    """
    Read configuration from specified config file. Merge all sections into one.
    If same key appears in different sections, the value will be undefined.
    Return dict like { 'key1': 'val1', ... }

    :param cfg_file: Absolute path to the config file.
    :param cfg_string: Read config from string instead of file.
    :param preserve_case: if True, key and value character case will be preserved
    :param allow_no_value: if True, empty values are not treated as errors.
    :return: ResultTuple (dict, ErrorMsg)
    """

    parser = ConfigParser(allow_no_value=allow_no_value)
    if preserve_case:
        parser.optionxform = str

    try:
        if not cfg_file:
            if cfg_string:
                parser.read_string(cfg_string)
        else:
            parser.read(cfg_file)
    except Exception as e:
        return {}, e.__class__.__name__ + ": " + str(e)

    result = {}
    try:
        # Special treatment for the 'DEFAULT' section
        if 'DEFAULT' in parser:
            result = dict(parser['DEFAULT'])

        for section in parser.sections():
            for key, value in parser.items(section):
                result[key] = value
    except Exception as e:
        return {}, e.__class__.__name__ + ": " + str(e)
    return result, ""


def write_config(*, config: dict, cfg_file: str, allow_rewrite: bool = False,
                 allow_no_value: bool = True,
                 preserve_case: bool = False) -> ResultTuple:
    """
    Write config parsed from 'config' dict into file.

    :param config: dict, including sections
    :param cfg_file: absolute path to the config file
    :param allow_rewrite: if True, old file will be silently overwritten
    :param allow_no_value: if True, empty values will be allowed
    :param preserve_case: if True, case will be preserved
    :return: ResultTuple (None, ErrorMsg)
    """
    if not allow_rewrite:
        if file_utils.file_exists_ne(cfg_file):
            return None, "old config file exists"

    parser = ConfigParser(allow_no_value=allow_no_value)
    if preserve_case:
        parser.optionxform = str

    try:
        parser.read_dict(config)
    except Exception as e:
        return None, "can't parse config dict: " + str(e)

    # save to file
    try:
        with open(cfg_file, 'w') as f:
            parser.write(f)
    except Exception as e:
        return None, f"can't create config file '{cfg_file}': " + str(e)

    return None, ""


def write_config_from_dict_nosect_ne(config: dict, cfg_file: str,
                                     allow_rewrite: bool = False,
                                     allow_no_value: bool = True,
                                     preserve_case: bool = False) -> ResultTuple:
    """
    Write config from plain 'config' dict (without sections) into file.
    A default 'GENERAL' section will be created.

    :param config: dict, including sections
    :param cfg_file: absolute path to the config file
    :param allow_rewrite: if True, old file will be silently overwritten
    :param allow_no_value: if True, empty values will be allowed
    :param preserve_case: if True, case will be preserved
    :return: ResultTuple (None, ErrorMsg)
    """
    sectioned_dict = {"GENERAL": config}
    return write_config(config=sectioned_dict, cfg_file=cfg_file,
                        allow_rewrite=allow_rewrite,
                        allow_no_value=allow_no_value,
                        preserve_case=preserve_case)
