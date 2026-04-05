#!/usr/bin/env python3
"""
swf_binary_io.py — Shared Binary I/O Utilities for SWF Parsing and generation.

This module provides low-level bit manipulation primitives for reading
and writing SWF binary format, which uses bit-packed structures.

Extracted from swf_to_n2d.py, swf_writer.py, and swf_shape_to_recodes.py
to eliminate code duplication and provide a single tested implementation.
"""

from __future__ import annotations

import struct
from typing import List


class BitReader:
    """Read individual bits from a byte buffer (MSB-first, per SWF spec).
    
    Supports bit-aligned reads (ub, sb, fb) and byte-aligned reads (ui8, ui16, etc.).
    Used for parsing SWF binary structures like RECT, MATRIX, shape records.
    
    Example:
        >>> reader = BitReader(b'\\xFF\\x80')
        >>> reader.read_ub(4)  # Read 4 bits
        15
        >>> reader.read_ub(4)
        15
        >>> reader.read_ub(4)
        8
    """

    def __init__(self, data: bytes, byte_offset: int = 0):
        """
        Initialize bit reader.
        
        Args:
            data: Byte buffer to read from
            byte_offset: Starting byte position (default: 0)
        """
        self.data = data
        self.byte_pos = byte_offset
        self.bit_pos = 0

    @property
    def pos(self) -> int:
        """Current position in bits from start of buffer."""
        return self.byte_pos * 8 + self.bit_pos

    @property
    def remaining(self) -> int:
        """Number of bytes remaining from current position to end of buffer."""
        return len(self.data) - self.byte_pos

    def align(self) -> None:
        """Align to next byte boundary."""
        if self.bit_pos > 0:
            self.byte_pos += 1
            self.bit_pos = 0

    def read_ub(self, n: int) -> int:
        """
        Read n unsigned bits (MSB-first).
        
        Args:
            n: Number of bits to read (0-32)
            
        Returns:
            Unsigned integer value
            
        Raises:
            IndexError: If reading past end of buffer
        """
        if n == 0:
            return 0
        result = 0
        for _ in range(n):
            if self.byte_pos >= len(self.data):
                raise IndexError(f"BitReader: read past end of buffer at byte {self.byte_pos}")
            byte_val = self.data[self.byte_pos]
            bit = (byte_val >> (7 - self.bit_pos)) & 1
            result = (result << 1) | bit
            self.bit_pos += 1
            if self.bit_pos >= 8:
                self.bit_pos = 0
                self.byte_pos += 1
        return result

    def read_sb(self, n: int) -> int:
        """
        Read n signed bits (two's complement, MSB-first).
        
        Args:
            n: Number of bits to read (1-32)
            
        Returns:
            Signed integer value
        """
        if n == 0:
            return 0
        val = self.read_ub(n)
        if val & (1 << (n - 1)):  # sign bit set
            val -= (1 << n)
        return val

    def read_fb(self, n: int) -> float:
        """
        Read n-bit fixed-point 16.16 value.
        
        Args:
            n: Number of bits to read
            
        Returns:
            Floating-point value
        """
        return self.read_sb(n) / 65536.0

    def read_ui8(self) -> int:
        """Read unsigned 8-bit integer (byte-aligned)."""
        self.align()
        if self.byte_pos >= len(self.data):
            raise IndexError(f"BitReader: read_ui8 past end at byte {self.byte_pos}")
        val = self.data[self.byte_pos]
        self.byte_pos += 1
        return val

    def read_ui16(self) -> int:
        """Read unsigned 16-bit integer, little-endian (byte-aligned)."""
        self.align()
        if self.byte_pos + 2 > len(self.data):
            raise IndexError(f"BitReader: read_ui16 past end at byte {self.byte_pos}")
        val = struct.unpack_from('<H', self.data, self.byte_pos)[0]
        self.byte_pos += 2
        return val

    def read_ui32(self) -> int:
        """Read unsigned 32-bit integer, little-endian (byte-aligned)."""
        self.align()
        if self.byte_pos + 4 > len(self.data):
            raise IndexError(f"BitReader: read_ui32 past end at byte {self.byte_pos}")
        val = struct.unpack_from('<I', self.data, self.byte_pos)[0]
        self.byte_pos += 4
        return val

    def read_si16(self) -> int:
        """Read signed 16-bit integer, little-endian (byte-aligned)."""
        self.align()
        if self.byte_pos + 2 > len(self.data):
            raise IndexError(f"BitReader: read_si16 past end at byte {self.byte_pos}")
        val = struct.unpack_from('<h', self.data, self.byte_pos)[0]
        self.byte_pos += 2
        return val

    def read_string(self) -> str:
        """Read null-terminated UTF-8 string (byte-aligned)."""
        self.align()
        try:
            end = self.data.index(0, self.byte_pos)
        except ValueError:
            raise ValueError(f"BitReader: no null terminator found at byte {self.byte_pos}")
        s = self.data[self.byte_pos:end].decode('utf-8', errors='replace')
        self.byte_pos = end + 1
        return s


class BitWriter:
    """Write individual bits to a byte buffer (MSB-first, per SWF spec).
    
    Supports bit-aligned writes (ub, sb) and byte-aligned writes via output buffer.
    Used for generating SWF binary structures.
    
    Example:
        >>> import io
        >>> output = io.BytesIO()
        >>> writer = BitWriter(output)
        >>> writer.write_ub(4, 15)  # Write 4 bits, value 15
        >>> writer.write_ub(4, 15)
        >>> writer.align()
        >>> output.getvalue()
        b'\\xff'
    """

    __slots__ = ('_buf', '_output', '_acc', '_acc_bits')

    def __init__(self, output=None):
        if output is None:
            import io
            output = io.BytesIO()
        self._output = output
        self._buf = bytearray()
        self._acc = 0       # accumulator for partial byte
        self._acc_bits = 0  # bits currently in accumulator (0-7)

    @property
    def output(self):
        return self._output

    def get_bytes(self) -> bytes:
        """Flush any pending bits and return all written bytes."""
        self.align()
        if self._buf:
            self._output.write(self._buf)
            self._buf = bytearray()
        return self._output.getvalue()

    def write_ub(self, nbits: int, value: int) -> None:
        """Write unsigned integer as n bits (MSB-first)."""
        if nbits <= 0:
            return
        value = value & ((1 << nbits) - 1)
        acc = self._acc
        acc_bits = self._acc_bits
        buf = self._buf

        # Merge bits into accumulator; flush complete bytes
        total = acc_bits + nbits
        acc = (acc << nbits) | value
        while total >= 8:
            total -= 8
            buf.append((acc >> total) & 0xFF)
            acc &= (1 << total) - 1 if total else 0
        self._acc = acc
        self._acc_bits = total

    def write_sb(self, nbits: int, value: int) -> None:
        """Write signed integer as n bits (two's complement, MSB-first)."""
        if nbits <= 0:
            return
        if value < 0:
            value = (1 << nbits) + value
        self.write_ub(nbits, value)

    def write_fb(self, nbits: int, value: float) -> None:
        """Write fixed-point 16.16 number as n bits (signed)."""
        fixed = int(round(value * 65536))
        self.write_sb(nbits, fixed)

    def align(self) -> None:
        """Flush current byte and align to next byte boundary."""
        if self._acc_bits > 0:
            self._buf.append((self._acc << (8 - self._acc_bits)) & 0xFF)
            self._acc = 0
            self._acc_bits = 0

    def flush(self) -> None:
        """Alias for align() for compatibility."""
        self.align()


def _nbits_unsigned(value: int) -> int:
    """
    Calculate minimum bits needed to represent unsigned integer.
    
    Args:
        value: Unsigned integer
        
    Returns:
        Number of bits (0-32)
        
    Example:
        >>> _nbits_unsigned(0)
        0
        >>> _nbits_unsigned(15)
        4
        >>> _nbits_unsigned(255)
        8
    """
    if value == 0:
        return 0
    return value.bit_length()


def _nbits_signed(value: int) -> int:
    """
    Calculate minimum bits needed to represent signed integer.
    
    Args:
        value: Signed integer
        
    Returns:
        Number of bits (1-32)
        
    Example:
        >>> _nbits_signed(0)
        1
        >>> _nbits_signed(15)
        5
        >>> _nbits_signed(-1)
        1
        >>> _nbits_signed(-16)
        5
    """
    if value == 0:
        return 1
    if value > 0:
        return value.bit_length() + 1  # +1 for sign bit
    else:
        # For negative, find bits needed for |value - 1|
        return (abs(value) - 1).bit_length() + 1


def _nbits_unsigned_list(values: List[int]) -> int:
    """
    Calculate minimum bits needed to represent all values in list (unsigned).
    
    Args:
        values: List of unsigned integers
        
    Returns:
        Number of bits (0-32)
    """
    if not values:
        return 0
    return max(_nbits_unsigned(v) for v in values)


def _nbits_signed_list(values: List[int]) -> int:
    """
    Calculate minimum bits needed to represent all values in list (signed).
    
    Args:
        values: List of signed integers
        
    Returns:
        Number of bits (1-32)
    """
    if not values:
        return 1
    return max(_nbits_signed(v) for v in values)
