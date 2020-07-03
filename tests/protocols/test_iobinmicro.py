"""
Tests for IoBinMicroCodec.py
Author: iotanbo
"""

# import pytest
from iotanbo_py_utils.protocols.iobinmicro import IoBinMicroCodec, GARBAGE_WARNING
from iotanbo_py_utils.error import WebSvcError


def usage_example():
    pass
    # TODO


def test_encode_small_data():

    start_key = IoBinMicroCodec.START_KEY
    stop_key = IoBinMicroCodec.STOP_KEY

    pl_size = 8
    codec = IoBinMicroCodec(max_payload_len=pl_size)
    assert codec.buf.size == pl_size + IoBinMicroCodec.SVC_PROTOCOL_DATA_LEN
    assert codec.max_payload_len == pl_size

    # Happy path
    small_payload = b"TEST"
    _, err = codec.encode(small_payload)
    assert not err

    assert codec.buf.get_unread_size() == len(small_payload) + IoBinMicroCodec.SVC_PROTOCOL_DATA_LEN
    assert codec.buf.buf[:12] == start_key + b"\x04\x00\x00\x00TEST" + stop_key

    full_length_payload = b"TESTTEST"
    _, err = codec.encode(full_length_payload)
    assert not err
    assert codec.buf.buf[:16] == start_key + b"\x08\x00\x00\x00TESTTEST" + stop_key

    # Sad path: too big data
    too_big_data = b"TEST_DATA_TOO_LONG"
    _, err = codec.encode(too_big_data)
    assert err == "LENGTH_ERROR"


def test_decode_small_data():
    pl_size = 8
    c = IoBinMicroCodec(max_payload_len=pl_size)
    start_key = IoBinMicroCodec.START_KEY
    stop_key = IoBinMicroCodec.STOP_KEY

    # Happy path: valid small cmd decoded at once
    small_cmd = start_key + b"\x04\x00\x00\x00TEST" + stop_key
    result, err = c.decode(small_cmd)
    assert not err
    assert result
    payload, err = c.get_payload_view()
    assert payload.tobytes() == b"TEST"
    c.mark_read()

    # Happy path: valid full-length cmd decoded at once
    small_cmd = start_key + b"\x08\x00\x00\x00TESTTEST" + stop_key
    result, err = c.decode(small_cmd)
    assert not err
    assert result
    payload, err = c.get_payload_view()
    assert payload.tobytes() == b"TESTTEST"
    c.mark_read()

    # Sad path: try to decode empty buffer
    # Expected codec behaviour: WebSvcError.EMPTY_ERROR
    result, err = c.decode()
    assert err == WebSvcError.EMPTY_ERROR
    assert c.buf.is_empty()


def test_decode_small_data_by_parts():
    pl_size = 8
    c = IoBinMicroCodec(max_payload_len=pl_size)
    start_key = IoBinMicroCodec.START_KEY
    stop_key = IoBinMicroCodec.STOP_KEY

    # Happy path: valid full-length cmd decoded by three parts
    small_cmd = start_key + b"\x08\x00\x00\x00TESTTEST" + stop_key
    # First data portion: return False because more data is needed to decode full cmd
    result, err = c.decode(small_cmd[:8])
    print(f"Buffer after first portion decode: {c.buf}")
    assert not err
    assert not result

    # Second data portion: return False because more data is needed to decode full cmd
    result, err = c.decode(small_cmd[8:15])
    print(f"Buffer after second portion decode: {c.buf}")
    assert not err
    assert not result

    # Third data portion
    result, err = c.decode(small_cmd[15:16])
    print(f"Buffer after third portion decode: {c.buf}")
    assert not err
    assert result

    payload, err = c.get_payload_view()
    assert payload.tobytes() == b"TESTTEST"
    c.mark_read()
    assert c.buf.is_empty()


def test_decode_small_data_byte_by_byte():
    pl_size = 8
    c = IoBinMicroCodec(max_payload_len=pl_size)
    start_key = IoBinMicroCodec.START_KEY
    stop_key = IoBinMicroCodec.STOP_KEY

    # Happy path: valid full-length cmd decoded byte by byte
    small_cmd = start_key + b"\x08\x00\x00\x00TESTTEST" + stop_key
    result = False
    err = "ERROR"
    for byte in small_cmd:
        result, err = c.decode(byte.to_bytes(1, byteorder="little"))
    assert result
    assert not err
    c.mark_read()


# *** SAD PATH TESTS ***

def test_decode_data_with_wrong_start_key():
    pl_size = 8
    c = IoBinMicroCodec(max_payload_len=pl_size)
    start_key = IoBinMicroCodec.START_KEY
    stop_key = IoBinMicroCodec.STOP_KEY

    wrong_start_key = b"\xB9\xA6"

    # Command with wrong START_KEY
    wrong_start_key_cmd = wrong_start_key + b"\x08\x00\x00\x00TESTTEST" + stop_key
    result, err = c.decode(wrong_start_key_cmd)

    # Expected codec behaviour: return WebSvcError.CMD_FMT_ERROR and discard all data
    assert err == WebSvcError.CMD_FMT_ERROR
    assert not result
    assert c.buf.is_empty()


def test_decode_data_with_wrong_stop_key():
    pl_size = 8
    c = IoBinMicroCodec(max_payload_len=pl_size)
    start_key = IoBinMicroCodec.START_KEY
    stop_key = IoBinMicroCodec.STOP_KEY

    wrong_stop_key = b"\x11\x12"

    # Command with wrong STOP_KEY
    wrong_stop_key_cmd = start_key + b"\x08\x00\x00\x00TESTTEST" + wrong_stop_key
    result, err = c.decode(wrong_stop_key_cmd)

    # Expected codec behaviour: return WebSvcError.CMD_FMT_ERROR and discard all data
    assert err == WebSvcError.CMD_FMT_ERROR
    assert not result
    # Buffer must be empty because no more potential commands detected
    assert c.buf.is_empty()


def test_decode_data_with_wrong_payload_size():
    pl_size = 8
    c = IoBinMicroCodec(max_payload_len=pl_size)
    start_key = IoBinMicroCodec.START_KEY
    stop_key = IoBinMicroCodec.STOP_KEY

    # Command with too small PAYLOAD_SIZE
    wrong_payload_size_cmd = start_key + b"\x07\x00\x00\x00TESTTEST" + stop_key
    result, err = c.decode(wrong_payload_size_cmd)

    # Expected codec behaviour: return WebSvcError.CMD_FMT_ERROR and discard all data
    assert err == WebSvcError.CMD_FMT_ERROR
    assert not result
    # Buffer must be empty because no more potential commands detected
    assert c.buf.is_empty()

    # Command with too big PAYLOAD_SIZE
    wrong_payload_size_cmd = start_key + b"\xff\x00\x00\x00TESTTEST" + stop_key
    result, err = c.decode(wrong_payload_size_cmd)

    # Expected codec behaviour: return WebSvcError.LENGTH_ERROR and discard all data
    assert err == WebSvcError.LENGTH_ERROR
    assert not result
    # Buffer must be empty because no more potential commands detected
    assert c.buf.is_empty()


def test_decode_with_garbage_before_and_after_cmd():
    # Garbage data that does not resemble START_KEY or STOP_KEY
    garbage = b"\x22\44\17\10"
    pl_size = 8
    c = IoBinMicroCodec(max_payload_len=pl_size + len(garbage))
    start_key = IoBinMicroCodec.START_KEY
    stop_key = IoBinMicroCodec.STOP_KEY

    # Garbage data before cmd
    cmd_with_garbage = garbage + start_key + b"\x08\x00\x00\x00TESTTEST" + stop_key
    result, err = c.decode(cmd_with_garbage)

    # Expected codec behaviour:
    assert err  == GARBAGE_WARNING
    assert result
    c.mark_read()
    # Buffer must be empty because no more potential commands detected
    assert c.buf.is_empty()

    # Garbage data goes after cmd
    cmd_with_garbage = start_key + b"\x08\x00\x00\x00TESTTEST" + stop_key + garbage
    result, err = c.decode(cmd_with_garbage)

    # Expected codec behaviour:
    # First, successful decoding
    assert not err
    assert result
    c.mark_read()

    # Second, WebSvcError.CMD_FMT_ERROR
    result, err = c.decode()
    assert err == WebSvcError.CMD_FMT_ERROR
    assert c.buf.is_empty()


def test_garbage_resistance_start_key():
    start_key = IoBinMicroCodec.START_KEY
    stop_key = IoBinMicroCodec.STOP_KEY

    # Garbage data containing START_KEY and STOP_KEY
    garbage = start_key + b"\x22\44\17\10"
    pl_size = 8
    c = IoBinMicroCodec(max_payload_len=pl_size + len(garbage))

    # Garbage data before cmd
    cmd_with_garbage = garbage + start_key + b"\x08\x00\x00\x00TESTTEST" + stop_key
    result, err = c.decode(cmd_with_garbage)

    # Expected codec behaviour:
    assert err == WebSvcError.LENGTH_ERROR
    assert result
    c.mark_read()
    assert c.buf.is_empty()

    # Garbage data goes after cmd
    cmd_with_garbage = start_key + b"\x08\x00\x00\x00TESTTEST" + stop_key + garbage
    result, err = c.decode(cmd_with_garbage)

    # Expected codec behaviour:
    # First, successful decoding
    assert not err
    assert result
    c.mark_read()

    # Second, WebSvcError.LENGTH_ERROR
    result, err = c.decode()
    assert err == WebSvcError.LENGTH_ERROR
    assert c.buf.is_empty()


def _complex_garbage_resistance_check(garbage: bytes):
    start_key = IoBinMicroCodec.START_KEY
    stop_key = IoBinMicroCodec.STOP_KEY

    pl_size = 8
    c = IoBinMicroCodec(max_payload_len=pl_size + len(garbage))

    # Garbage data before cmd
    cmd_with_garbage = garbage + start_key + b"\x08\x00\x00\x00TESTTEST" + stop_key
    success = False
    c.buf.write_bytes(cmd_with_garbage)

    max_iters = 10
    for i in range(max_iters):
        result, err = c.decode()
        if result:
            if c.get_payload_view()[0].tobytes() == b"TESTTEST":
                success = True
                c.mark_read()
            break
        if not err or err == WebSvcError.EMPTY_ERROR:
            break
    assert success


def test_complex_garbage_resistance():
    """
    Test if a valid iobinmicro command is detected correctly despite of complex garbage data.
    """
    start_key = IoBinMicroCodec.START_KEY
    stop_key = IoBinMicroCodec.STOP_KEY

    # Garbage with multiple start_key and stop_key
    garbage = start_key + start_key + stop_key + b"\x08\x00\x00\x00DUMMY123" + start_key + stop_key
    _complex_garbage_resistance_check(garbage)

    # Garbage with multiple start_key and stop_key
    garbage = stop_key + start_key + start_key + stop_key + b"\xff\xff\x00\x00DUMMY123" + start_key + \
        b"\xff\xff\x00\x00asdfOi ;oasidhf h';oih;hbnoihweg h''ih oho09800"
    _complex_garbage_resistance_check(garbage)

    garbage = start_key[:1] * 200 + start_key * 30 + stop_key
    _complex_garbage_resistance_check(garbage)
