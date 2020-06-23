"""
Tests for async_file_utils.py
Author: iotanbo
"""

"""
NOTE:
    * Async file_crc32_ne() runs 2 times slower than synchronous variant.
      Is there a benefit of using it?
"""

import pytest
import os
from iotanbo_py_utils import async_file_utils
from iotanbo_py_utils import file_utils
import time


@pytest.mark.asyncio
async def test_file_crc32_ne(tmpdir):

    # Small data test
    small_file = os.path.join(tmpdir, "small_file.test")
    small_file_contents = b"TEST"

    _, err = file_utils.write_bin_file_ne(small_file, contents=small_file_contents)
    assert not err

    crc, err = await async_file_utils.file_crc32_ne(small_file)
    assert not err
    print(f"FILE CRC: {crc}, hex: {hex(crc)}")
    assert crc == int("EEEA93B8", base=16)

    # Big data test
    big_file = os.path.join(tmpdir, "big_file.test")
    big_file_contents = b"TEST" * 1024 ** 2 * 10

    _, err = file_utils.write_bin_file_ne(big_file, contents=big_file_contents)
    assert not err

    start = time.perf_counter()
    crc_async, err = await async_file_utils.file_crc32_ne(big_file)
    elapsed = time.perf_counter() - start

    assert not err
    print(f"ASYNC BIG_FILE CRC: {crc_async}, hex: {hex(crc_async)}, size: {len(big_file_contents) / 1024**2} Mb, time: {elapsed * 1000} millis")

    # Compare with sync variant
    start = time.perf_counter()
    crc_sync, err = file_utils.file_crc32_ne(big_file)
    elapsed = time.perf_counter() - start

    assert not err
    print(
        f"SYNC BIG_FILE CRC: {crc_sync}, hex: {hex(crc_sync)}, size: {len(big_file_contents) / 1024 ** 2} Mb, time: {elapsed * 1000} millis")

    assert crc_sync == crc_async
