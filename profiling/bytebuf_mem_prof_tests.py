
from iotanbo_py_utils.bytebuf import Bytebuf

from memory_profiler import profile


"""
VERIFIED BEST PRACTICE WITH BYTEARRAY:

# Convert part of bytearray into str
result = buf[:34].decode()  # OK (no unnecessary copies created)

# Assign bytearray to another bytearray part
dest[start:end] = src  #  OK (no unnecessary copies created)

"""


@profile
def memory_profiler_test():
    buf = Bytebuf(16 * 1024 ** 2)
    buf.write_int64(-12345678901234)
    buf.write_uint64(12345678901234)
    assert buf.read_int64() == -12345678901234


def test_str_multiplication():
    buf = Bytebuf(2 * 1024 ** 2)
    buf.write_str("Hello " * 5)
    result = buf.buf[4:34].decode()

    print(f"'{result}'")
    assert result == "Hello Hello Hello Hello Hello "


@profile
def to_string_test():
    buf = Bytebuf(2 * 1024 ** 2)
    buf.write_str("Hello " * 1024)
    result = buf.buf[4:1024 * 6 + 4].decode()
    assert len(result) == 1024 * 6


EIGHT_MB_ARRAY = bytearray(b"\x77" * 8 * 1024 ** 2)


@profile
def direct_bytes_write_test():
    buf = Bytebuf(16 * 1024 ** 2)
    buf_src = Bytebuf(16 * 1024 ** 2)

    # OK (no extra memory allocation done)
    buf_src.buf[:16 * 1024 ** 2] = b'\x70' * 16 * 1024 ** 2

    # OK (no extra memory allocation done)
    buf.buf[:8 * 1024 ** 2] = EIGHT_MB_ARRAY

    assert buf.buf[8 * (1024**2) - 1] == 0x77
    assert buf.buf[8 * (1024**2)] == 0


# python3 ./bytebuf_mem_prof_tests.py
if __name__ == '__main__':
    memory_profiler_test()
    to_string_test()
    direct_bytes_write_test()
