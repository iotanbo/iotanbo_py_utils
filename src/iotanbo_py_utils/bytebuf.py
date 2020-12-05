import struct


class Bytebuf:
    """
    Bytebuf is a binary data storage class with simplified API inspired by Java.nio.Bytebuffer
    """

    def __init__(self, size,
                 byteorder: str = "little",
                 **kwargs):
        """
        Create byte buffer of specified size.

        :param byteorder: Byte order for integer and float values, "little" or "big" - endian.
        :param size: Size in bytes.
        :param kwargs: reserved
        """
        super().__init__(**kwargs)

        self.buf = bytearray(size)
        self.byteorder = byteorder
        self.reader_i = 0
        self.writer_i = 0
        self.size = size

    def __str__(self) -> str:
        return f"Bytebuf<size: {self.size}, reader: {self.reader_i}, writer: {self.writer_i}, " \
               f"data: {self.get_unread_view().tobytes()}>"

    def __repr__(self):
        return self.__str__()

    def get_unread_size(self) -> int:
        """
        Get unread data size.
        """
        return self.writer_i - self.reader_i

    def get_view(self, start_index: int, end_index: int) -> memoryview:
        """
        Get memory view of the underlying bytearray (zero-copy).

        :param start_index:
        :param end_index:
        """
        return memoryview(self.buf)[start_index:end_index]

    def get_unread_view(self) -> memoryview:
        """
        Get memory view of the underlying bytearray (zero-copy) from reader index to writer index.
        """
        return memoryview(self.buf)[self.reader_i:self.writer_i]

    def get_view_chunk(self, size: int) -> memoryview:
        """
        Get memory view of the underlying byte array (zero-copy) from reader index to (reader index + size).

        :param size: size of chunk in bytes.
        """
        return memoryview(self.buf)[self.reader_i:self.reader_i + size]

    def reset(self) -> None:
        """
        Reset indexes.
        :return: None
        """
        self.reader_i = 0
        self.writer_i = 0

    def is_empty(self) -> bool:
        """
        Return True if there is no unread data in the buffer.
        """
        return self.reader_i == self.writer_i

    def get_free_space(self) -> int:
        """
        Get number of bytes that can be written.
        """
        return self.size - self.writer_i

    def compact(self) -> None:
        """
        Move unread data to the beginning of the buffer.
        Set reader index to 0 and writer index to the end of unread data.
        :return: None
        """

        # Correct the error if reader index is greater then writer index
        if self.reader_i > self.writer_i:
            self.reader_i = self.writer_i

        if not self.reader_i:
            return

        if self.reader_i == self.writer_i:
            self.reader_i = 0
            self.writer_i = 0
            return

        unread_size = self.writer_i - self.reader_i
        memoryview(self.buf)[0:unread_size] = self.buf[self.reader_i:self.writer_i]
        self.reader_i = 0
        self.writer_i = unread_size

    def read_uint32(self) -> int:
        result = int.from_bytes(self.buf[self.reader_i:self.reader_i + 4],
                                byteorder=self.byteorder, signed=False)
        self.reader_i += 4
        return result

    def write_uint32(self, uint32: int) -> None:
        memoryview(self.buf)[self.writer_i:self.writer_i+4] = int.to_bytes(uint32, length=4,
                                                                           byteorder=self.byteorder, signed=False)
        self.writer_i += 4

    def read_int32(self) -> int:
        result = int.from_bytes(self.buf[self.reader_i:self.reader_i + 4],
                                byteorder=self.byteorder, signed=True)
        self.reader_i += 4
        return result

    def write_int32(self, uint32: int) -> None:
        memoryview(self.buf)[self.writer_i:self.writer_i+4] = int.to_bytes(uint32, length=4,
                                                                           byteorder=self.byteorder, signed=True)
        self.writer_i += 4

    # 64-bit integers

    def read_uint64(self) -> int:
        result = int.from_bytes(self.buf[self.reader_i:self.reader_i + 8],
                                byteorder=self.byteorder, signed=False)
        self.reader_i += 8
        return result

    def write_uint64(self, uint64: int) -> None:
        memoryview(self.buf)[self.writer_i:self.writer_i+8] = int.to_bytes(uint64, length=8,
                                                                           byteorder=self.byteorder, signed=False)
        self.writer_i += 8

    def read_int64(self) -> int:
        result = int.from_bytes(self.buf[self.reader_i:self.reader_i + 8],
                                byteorder=self.byteorder, signed=True)
        self.reader_i += 8
        return result

    def write_int64(self, uint64: int) -> None:
        memoryview(self.buf)[self.writer_i:self.writer_i+8] = int.to_bytes(uint64, length=8,
                                                                           byteorder=self.byteorder, signed=True)
        self.writer_i += 8

    # ** FLOATING POINT VALUES **

    def read_float32(self) -> float:
        if self.byteorder == "big":
            result = struct.unpack('>f', self.buf[self.reader_i:self.reader_i + 4])
        else:
            result = struct.unpack('<f', self.buf[self.reader_i:self.reader_i + 4])
        self.reader_i += 4
        return result[0]

    def write_float32(self, float32: float) -> None:
        if self.byteorder == "big":
            memoryview(self.buf)[self.writer_i:self.writer_i+4] = struct.pack('>f', float32)
        else:
            memoryview(self.buf)[self.writer_i:self.writer_i+4] = struct.pack('<f', float32)
        self.writer_i += 4

    def read_double(self) -> float:
        """
        Read 64-bit double precision floating point value from buffer.

        :return: float
        """
        if self.byteorder == "big":
            result = struct.unpack('>d', self.buf[self.reader_i:self.reader_i + 8])
        else:
            result = struct.unpack('<d', self.buf[self.reader_i:self.reader_i + 8])
        self.reader_i += 8
        return result[0]

    def write_double(self, double: float) -> None:
        """
        Write 64-bit double precision floating point value into the buffer.
        """

        if self.byteorder == "big":
            memoryview(self.buf)[self.writer_i:self.writer_i+8] = struct.pack('>d', double)
        else:
            memoryview(self.buf)[self.writer_i:self.writer_i+8] = struct.pack('<d', double)
        self.writer_i += 8

    # ** BYTES **
    def read_bytes(self, size: int) -> memoryview:
        """
        Get memory view of buffer of specified size starting from reader index.
        Increment reader index accordingly.

        :param size: in bytes
        :return: memory view of the buffer
        """
        result = self.get_view_chunk(size)
        self.reader_i += size
        return result

    def write_bytes(self, data: bytes) -> None:
        """
        Append bytes at current writer index;
        Increment writer index accordingly.

        :param data:
        """
        data_size = len(data)
        wi = self.writer_i
        if data_size > self.get_free_space():
            raise ValueError("Bytebuf overflow (too small buffer size or forgot to compact?)")
        memoryview(self.buf)[wi:wi + data_size] = data
        self.writer_i += data_size

    # ** STRINGS **

    def read_str(self, encoding="utf-8") -> str:
        """
        Read a string from the byte buffer at current reader index.
        First write 4 bytes indicating length, then actual string data.

        :param encoding: "utf-8" default
        """
        str_len = self.read_uint32()
        result = self.buf[self.reader_i:self.reader_i+str_len].decode(encoding=encoding)
        self.reader_i += str_len
        return result

    def write_str(self, string: str, encoding="utf-8") -> None:
        """
        Write a string into the byte buffer at current reader index.
        First write 4 bytes indicating length, then actual string data.

        :param string:
        :param encoding: "utf-8" default
        """
        str_len = len(string)
        self.write_uint32(str_len)
        self.write_bytes(string.encode(encoding=encoding))
