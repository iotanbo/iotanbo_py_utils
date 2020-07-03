"""
Author: iotanbo
"""
from iotanbo_py_utils.bytebuf import Bytebuf
from iotanbo_py_utils.error import ErrorMsg, WebSvcError


GARBAGE_WARNING = 'GARBAGE_WARNING'
"""
A return value meaning that operation was successful,
but garbage data was detected along with a valid command.
This is not considered as an error.
"""


class IoBinMicroCodec:
    """
    IoBinMicro is a very basic binary protocol targeting first of all
    MCUs or MCUs connected to web servers.
    Except MCUs, it also can be used for efficient data exchange between (almost) any kind of
    clients and servers.
    This protocol does NOT check data authenticity and
    gives a very limited data integrity guarantee.


    ** PROTOCOL DESCRIPTION **

      2 bytes    4 bytes       any number of bytes        2 bytes
    START_KEY  PAYLOAD_len  PAYLOAD_OF_VARIABLE_LENGTH  STOP_KEY
     'B9A7'      uint32_t      any kink of payload        'B801'

    * START_KEY ('B9A7') and STOP_KEY ('B801') are intended to alleviate command decoding
      (reduce computing power) in an environment where data loss may happen.

    * PAYLOAD_len is a little-endian encoded 32-bit integer representing
                   payload size (STOP_KEY size NOT included).

    * PAYLOAD_OF_VARIABLE_LENGTH is an arbitrary set of binary data.
                                 Its integrity and authenticity must be further
                                 verified by the receiver.

    """

    SVC_PROTOCOL_DATA_LEN = 8
    """
    Cumulative size of all service protocol data (START_KEY size + STOP_KEY size + uint32_t size)
    """

    START_KEY = b"\xB9\xA7"
    """
    Start key constant.
    """

    STOP_KEY = b"\xB8\x01"
    """
    Stop key constant.
    """

    def __init__(self, *,
                 max_payload_len: int,
                 **kwargs):
        """
        Create a new IoBinMicroCodec object that can encode and decode payloads of specified size.
        This protocol is presumed to be used in a half-duplex communications,
        so the only buffer is used for both decoding (receiving) and encoding data.
        If there is a need for a full-duplex mode, two IoBinMicroCodec objects can be created.

        :param buf_len: internal buffer size; also defines maximum payload size.
        :param kwargs: reserved
        """
        super().__init__(**kwargs)
        self.max_payload_len = max_payload_len
        self.buf = Bytebuf(size=max_payload_len + IoBinMicroCodec.SVC_PROTOCOL_DATA_LEN,
                           byteorder="little")

        self._decoded_payload_len = 0
        """
        Length of the decoded payload.
        """

    def reset(self) -> None:
        """
        Reset codec internal state, delete all data from the buffer.
        """
        self.buf.reset()
        self._decoded_payload_len = 0

    def mark_read(self) -> None:
        """
        Discard already decoded cmd and compact internal buffer.
        """
        self.buf.reader_i = self._decoded_payload_len + IoBinMicroCodec.SVC_PROTOCOL_DATA_LEN
        self.buf.compact()
        self._decoded_payload_len = 0

    def encode(self, payload: bytes) -> (None, ErrorMsg):
        """
        Encode a IoBinMicro message with specified payload and put it into the
        internal buffer. Old data in the buffer will be lost.

        :param payload: arbitrary binary data
        :return: (None, ErrorMsg):
        """

        payload_len = len(payload)
        if payload_len > self.max_payload_len:
            return None, WebSvcError.LENGTH_ERROR

        self.reset()
        self.buf.write_bytes(IoBinMicroCodec.START_KEY)
        self.buf.write_uint32(payload_len)
        self.buf.write_bytes(payload)
        self.buf.write_bytes(IoBinMicroCodec.STOP_KEY)
        return None, ""

    def decode(self, data: bytes = None) -> (bool, ErrorMsg):
        """
        Append data to the internal buffer and try to decode it.
        If data is None, the data from the internal buffer will be decoded.

        :param data: binary data in 'iobinmicro' format, e.g. encoded with 'IoBinMicroCodec.encode()'.
        :return: True if command was successfully decoded and can be retrieved with 'get_payload_view()' method.
                 False if there is not enough data to decode the entire command or error occurred.
                 Error messages:
                    * 'GARBAGE_WARNING' if the command was successfully decoded but garbage data was
                        detected along with cmd data;
                    * 'WebSvcError.EMPTY_ERROR' if there is no data to decode;
                    * 'WebSvcError.LENGTH_ERROR' if cmd is too long or has incorrect PAYLOAD_SIZE;
                    * 'WebSvcError.CMD_FMT_ERROR' if start or end keys are not on their places;


        """
        if data:
            data_len = len(data)
            free_space = self.buf.get_free_space()
            if data_len > free_space:
                return False, WebSvcError.LENGTH_ERROR

            self.buf.write_bytes(data)

        if self.buf.is_empty():
            return False, WebSvcError.EMPTY_ERROR

        last_error = ""

        # Reset reader index because a command is always located in the beginning of the buffer
        self.buf.reader_i = 0

        start_key_b1 = IoBinMicroCodec.START_KEY[0]

        # Alias for internal Bytebuf's bytearray
        buf = self.buf.buf

        while True:

            # Update unread data size
            total_data_len = self.buf.get_unread_size()

            if total_data_len < 2:  # more data is required to continue
                return False, last_error

            # Check if START_KEY is present
            if buf[:2] != IoBinMicroCodec.START_KEY:
                # Data is corrupted.
                last_error = WebSvcError.CMD_FMT_ERROR
                # Search for potential START_KEY and discard all data before it
                start_key_b1_found = False
                for i in range(1, total_data_len):
                    if buf[i] == start_key_b1:
                        self.buf.reader_i = i
                        start_key_b1_found = True
                        break
                # Restart decoding cycle with invalid data discarded
                if not start_key_b1_found:
                    self.buf.reader_i = total_data_len
                self.buf.compact()
                continue

            # START_KEY is OK
            if total_data_len < 6:  # more data is required to continue
                return False, last_error

            # Read PAYLOAD_SIZE
            self.buf.reader_i = 2
            decoded_payload_len = self.buf.read_uint32()

            if decoded_payload_len > self.max_payload_len:
                # Message is too long or data is corrupted.
                # Search for potential START_KEY and discard all data before it
                last_error = WebSvcError.LENGTH_ERROR  # store error message for future return
                start_key_b1_found = False
                for i in range(2, total_data_len):
                    if buf[i] == start_key_b1:
                        self.buf.reader_i = i
                        start_key_b1_found = True
                        break
                # Restart decoding cycle with invalid data discarded
                if not start_key_b1_found:
                    self.buf.reader_i = total_data_len
                self.buf.compact()
                continue

            # PAYLOAD_SIZE is OK
            # Check if there is enough data in the buffer
            if total_data_len < decoded_payload_len + IoBinMicroCodec.SVC_PROTOCOL_DATA_LEN:
                return False, last_error

            # Check STOP_KEY
            stop_key_index = decoded_payload_len + 6
            if buf[stop_key_index:stop_key_index+2] != IoBinMicroCodec.STOP_KEY:
                # Data is corrupted.
                last_error = WebSvcError.CMD_FMT_ERROR
                # Search for potential START_KEY and discard all data before it
                start_key_b1_found = False
                for i in range(2, total_data_len):
                    if buf[i] == start_key_b1:
                        self.buf.reader_i = i
                        start_key_b1_found = True
                        break
                # Restart decoding cycle with invalid data discarded
                if not start_key_b1_found:
                    self.buf.reader_i = total_data_len
                self.buf.compact()
                continue

            # STOP_KEY is OK
            # The command is successfully decoded
            self.buf.reader_i = 6  # payload start
            self._decoded_payload_len = decoded_payload_len
            if last_error == WebSvcError.CMD_FMT_ERROR:
                last_error = GARBAGE_WARNING
            return True, last_error

    def get_payload_view(self) -> (memoryview, ErrorMsg):
        """
        Get zero-copy view of the decoded payload in the internal buffer.
        It is required to call either 'mark_read()' or 'reset()' method
        in order to discard already decoded command.

        :return: 'memoryview' - memory view of the payload;
                 'ErrorMsg' - 'WebSvcError.EMPTY_ERROR' if no payload decoded.
        """
        if not self._decoded_payload_len:
            return None, WebSvcError.EMPTY_ERROR
        return self.buf.read_bytes(self._decoded_payload_len), ""
