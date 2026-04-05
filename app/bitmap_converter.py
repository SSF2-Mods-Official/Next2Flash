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
    # Convert RGBA → premultiplied ARGB using numpy if available (100x faster)
    try:
        import numpy as np
        px = np.frombuffer(pixel_data, dtype=np.uint8).reshape(-1, 4).copy()
        r, g, b, a = px[:, 0], px[:, 1], px[:, 2], px[:, 3]
        # Premultiply: channel = channel * alpha / 255
        mask_zero = a == 0
        mask_full = a == 255
        mask_partial = ~mask_zero & ~mask_full
        # Zero alpha → all zero
        px[mask_zero] = 0
        # Full alpha → just reorder to ARGB
        # Partial alpha → premultiply
        if mask_partial.any():
            af = a[mask_partial].astype(np.uint16)
            px[mask_partial, 1] = ((r[mask_partial].astype(np.uint16) * af + 127) // 255).astype(np.uint8)
            px[mask_partial, 2] = ((g[mask_partial].astype(np.uint16) * af + 127) // 255).astype(np.uint8)
            px[mask_partial, 3] = ((b[mask_partial].astype(np.uint16) * af + 127) // 255).astype(np.uint8)
            px[mask_partial, 0] = a[mask_partial]
        # Reorder RGBA → ARGB: [R,G,B,A] → [A,R,G,B]
        argb = np.empty_like(px)
        argb[:, 0] = a
        argb[mask_full, 1] = r[mask_full]
        argb[mask_full, 2] = g[mask_full]
        argb[mask_full, 3] = b[mask_full]
        if mask_partial.any():
            argb[mask_partial, 1] = px[mask_partial, 1]
            argb[mask_partial, 2] = px[mask_partial, 2]
            argb[mask_partial, 3] = px[mask_partial, 3]
        argb[mask_zero] = 0
        argb_bytes = argb.tobytes()
    except ImportError:
        # Fallback: pure Python
        argb_buf = bytearray(len(pixel_data))
        for i in range(0, len(pixel_data), 4):
            r = pixel_data[i] if i < len(pixel_data) else 0
            g = pixel_data[i + 1] if i + 1 < len(pixel_data) else 0
            b = pixel_data[i + 2] if i + 2 < len(pixel_data) else 0
            a = pixel_data[i + 3] if i + 3 < len(pixel_data) else 255
            if a == 0:
                argb_buf[i:i+4] = b'\x00\x00\x00\x00'
            elif a == 255:
                argb_buf[i] = a; argb_buf[i+1] = r; argb_buf[i+2] = g; argb_buf[i+3] = b
            else:
                argb_buf[i] = a
                argb_buf[i+1] = (r * a + 127) // 255
                argb_buf[i+2] = (g * a + 127) // 255
                argb_buf[i+3] = (b * a + 127) // 255
        argb_bytes = bytes(argb_buf)

    # zlib level 6 is ~3x faster than 9 with <5% size increase
    compressed = zlib.compress(argb_bytes, 6)

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
