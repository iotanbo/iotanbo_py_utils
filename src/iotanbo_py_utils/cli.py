"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -miotanbo_py_utils` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``iotanbo_py_utils.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``iotanbo_py_utils.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import sys

import iotanbo_py_utils
from iotanbo_py_utils import console_man_test


def main(*_, **__):
    """
    Report version
    """
    args = sys.argv

    if 'contest' in args:
        print("Starting console manual test:")
        console_man_test.input_ex_test()
    else:
        print(f"iotanbo_py_utils version {iotanbo_py_utils.__version__}")

    return 0
