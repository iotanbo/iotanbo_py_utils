"""
Tests for bytebuf.py
Author: iotanbo
"""

# import pytest
import math

from iotanbo_py_utils.bytebuf import Bytebuf
from memory_profiler import profile


def test_init():
    buf = Bytebuf(16)
    assert buf.size == 16
    assert buf.buf[0] == 0
    assert buf.buf[15] == 0


def test_read_write_int():
    buf = Bytebuf(16)
    buf.write_int32(-12345678)
    buf.write_uint32(12345678)
    assert buf.writer_i == 8
    assert buf.read_int32() == -12345678
    assert buf.read_uint32() == 12345678
    assert buf.reader_i == 8

    buf.reset()
    buf.write_int64(-12345678901234)
    buf.write_uint64(12345678901234)
    assert buf.writer_i == 16
    assert not buf.get_free_space()
    assert buf.read_int64() == -12345678901234
    assert buf.read_uint64() == 12345678901234
    assert buf.reader_i == 16
    assert buf.is_empty()


def test_read_write_float():
    buf = Bytebuf(16)
    buf.write_float32(1.0)
    buf.write_float32(-33.44)
    assert buf.writer_i == 8
    assert buf.read_float32() == 1.0
    assert math.isclose(buf.read_float32(), -33.44, abs_tol=.0001)
    assert buf.reader_i == 8

    buf.reset()
    buf.write_double(-12345678901234.777)
    buf.write_double(12345678901234.777)
    assert buf.writer_i == 16
    assert not buf.get_free_space()
    assert math.isclose(buf.read_double(), -12345678901234.777, abs_tol=.0001)
    assert math.isclose(buf.read_double(), 12345678901234.777, abs_tol=.0001)
    assert buf.reader_i == 16
    assert buf.is_empty()


def test_read_write_bytes():
    buf = Bytebuf(16)
    buf.write_bytes(b"\x00\x01\x02\x03")
    assert buf.writer_i == 4
    assert buf.read_bytes(4) == b"\x00\x01\x02\x03"
    assert buf.reader_i == 4

    buf.write_bytes(b"\x11\x22\x33\x44")
    assert buf.writer_i == 8
    assert buf.read_bytes(4) == b"\x11\x22\x33\x44"
    assert buf.reader_i == 8


def test_read_write_strings():
    buf = Bytebuf(20)
    buf.write_str("Hello, ")
    assert buf.writer_i == 11
    buf.write_str("world")
    assert buf.writer_i == 20
    # print(f"DEBUG buffer: '{buf.buf}'")
    assert buf.read_str() == "Hello, "
    assert buf.reader_i == 11
    assert buf.read_str() == "world"
    assert buf.reader_i == 20


def test_multi_read_write():
    buf = Bytebuf(128)
    buf.write_str("Hello")
    buf.write_int32(-22)
    buf.write_bytes(b"\x11\x22\x33\x44")
    buf.write_float32(0.3377)
    buf.write_double(77.12345678e5)

    # Read back
    assert buf.read_str() == "Hello"
    assert buf.read_int32() == -22
    assert buf.read_bytes(4) ==  b"\x11\x22\x33\x44"
    assert math.isclose(buf.read_float32(), .3377, abs_tol=.00001)
    assert math.isclose(buf.read_double(), 77.12345678e5, rel_tol=.00001)


def test_compact():
    buf = Bytebuf(16)
    buf.write_int64(-12345678901234)
    buf.write_uint64(12345678901234)
    assert buf.read_int64() == -12345678901234
    assert buf.get_free_space() == 0

    buf.compact()
    assert buf.reader_i == 0
    assert buf.get_free_space() == 8
    assert buf.read_uint64() == 12345678901234
    buf.compact()
    assert buf.reader_i == 0
    assert buf.get_free_space() == 16


@profile
def memory_profiler_test():
    buf = Bytebuf(16 * 1024 ** 2)
    buf.write_int64(-12345678901234)
    buf.write_uint64(12345678901234)
    assert buf.read_int64() == -12345678901234


# python3 -m memory_profiler ./test_bytebuf.py
if __name__ == '__main__':
    memory_profiler_test()
