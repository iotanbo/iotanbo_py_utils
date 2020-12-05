"""
Author: iotanbo
"""

# import aiofile
import os
import zlib

from aiofile import AIOFile
from iotanbo_py_utils.error import ResultTuple


async def file_crc32_ne(filename: str, buf_size: int = 1024*100) -> ResultTuple:
    """
    Calculate file crc32 asynchronously without exceptions.

    :param filename: path to file
    :param buf_size: memory buffer size
    :return: ResultTuple(crc: int, ErrorMsg: str):
                         crc: file crc32 as int
    """
    try:
        file_size = os.path.getsize(filename)

        if file_size < buf_size:
            remainder_size = file_size
            iterations = 0
        else:
            iterations = file_size // buf_size
            remainder_size = file_size % buf_size

        crc32 = 0
        offset = 0
        async with AIOFile(filename, 'rb') as f:
            for _ in range(iterations):
                data = await f.read(size=buf_size, offset=offset)
                crc32 = zlib.crc32(data, crc32)
                offset += buf_size

            # Read the remainder
            data = await f.read(remainder_size, offset=offset)
            crc32 = zlib.crc32(data, crc32)

    except Exception as e:
        msg = f"{e.__class__.__name__}: {str(e)}"
        return 0, msg
    return crc32, ""
