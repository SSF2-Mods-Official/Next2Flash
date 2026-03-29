"""
Bitmap Converter — Converts inline pixel data and image references
to SWF DefineBitsLossless2 tags (ARGB with zlib compression).
"""

from __future__ import annotations

import io
import logging
import struct
import zlib
from typing import Optional

log = logging.getLogger(__name__)

from swf_writer import TAG_DEFINE_BITS_LOSSLESS2, build_tag


def build_define_bits_lossless2(
    char_id: int,
    width: int,
    height: int,
    pixel_data: bytes,
) -> bytes:
    """
    Build a DefineBitsLossless2 tag (tag 36) for 32-bit ARGB images.

    `pixel_data` should be raw RGBA bytes (4 bytes per pixel, row-major).
    We convert to ARGB order as required by SWF.
    """
    log.debug("build_define_bits_lossless2: char_id=%d %dx%d pixel_bytes=%d", char_id, width, height, len(pixel_data))
    # Convert RGBA → premultiplied ARGB (SWF DefineBitsLossless2 requires
    # premultiplied alpha: R' = R*A/255, G' = G*A/255, B' = B*A/255)
    argb = bytearray()
    for i in range(0, len(pixel_data), 4):
        r = pixel_data[i] if i < len(pixel_data) else 0
        g = pixel_data[i + 1] if i + 1 < len(pixel_data) else 0
        b = pixel_data[i + 2] if i + 2 < len(pixel_data) else 0
        a = pixel_data[i + 3] if i + 3 < len(pixel_data) else 255
        if a == 0:
            argb.extend([0, 0, 0, 0])
        elif a == 255:
            argb.extend([a, r, g, b])
        else:
            argb.extend([a, (r * a + 127) // 255, (g * a + 127) // 255, (b * a + 127) // 255])

    # Pad each row to 4-byte boundary (already aligned for 32-bit)
    compressed = zlib.compress(bytes(argb), 9)

    body = io.BytesIO()
    body.write(struct.pack("<H", char_id))
    body.write(struct.pack("<B", 5))  # BitmapFormat = 5 (32-bit ARGB)
    body.write(struct.pack("<H", width))
    body.write(struct.pack("<H", height))
    body.write(compressed)

    return build_tag(TAG_DEFINE_BITS_LOSSLESS2, body.getvalue())


def build_define_bits_lossless2_from_raw(
    char_id: int,
    width: int,
    height: int,
    raw_argb: bytes,
) -> bytes:
    """
    Build DefineBitsLossless2 from already-ARGB-ordered pixel data.
    """
    log.debug("build_define_bits_lossless2_from_raw: char_id=%d %dx%d argb_bytes=%d", char_id, width, height, len(raw_argb))
    compressed = zlib.compress(raw_argb, 9)
    body = io.BytesIO()
    body.write(struct.pack("<H", char_id))
    body.write(struct.pack("<B", 5))
    body.write(struct.pack("<H", width))
    body.write(struct.pack("<H", height))
    body.write(compressed)
    return build_tag(TAG_DEFINE_BITS_LOSSLESS2, body.getvalue())
