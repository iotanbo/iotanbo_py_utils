========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - | |travis| |appveyor|
        | |codecov|
    * - package
      - | |commits-since|

.. |travis| image:: https://api.travis-ci.org/iotanbo/iotanbo_py_utils.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/iotanbo/iotanbo_py_utils

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/iotanbo/iotanbo_py_utils?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/iotanbo/iotanbo_py_utils

.. |codecov| image:: https://codecov.io/github/iotanbo/iotanbo_py_utils/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/iotanbo/iotanbo_py_utils

.. |commits-since| image:: https://img.shields.io/github/commits-since/iotanbo/iotanbo_py_utils/v0.0.4.svg
    :alt: Commits since latest release
    :target: https://github.com/iotanbo/iotanbo_py_utils/compare/v0.0.4...master



.. end-badges

Python utility collection by iotanbo

* Free software: MIT license

Installation
============

::

    pip install iotanbo_py_utils

You can also install the in-development version with::

    pip install https://github.com/iotanbo/iotanbo_py_utils/archive/master.zip


Documentation
=============


To use the project:

.. code-block:: python

    import iotanbo_py_utils
    iotanbo_py_utils.longest()


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
