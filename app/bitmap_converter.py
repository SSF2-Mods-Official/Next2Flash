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

from swf_writer import TAG_DEFINE_BITS_LOSSLESS2, TAG_DEFINE_BITS_LOSSLESS, build_tag


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
        px = np.frombuffer(pixel_data, dtype=np.uint8).reshape(-1, 4)
        r, g, b, a = px[:, 0], px[:, 1], px[:, 2], px[:, 3]
        # Premultiply: channel = channel * alpha / 255
        mask_zero = a == 0
        mask_full = a == 255
        mask_partial = ~mask_zero & ~mask_full
        # Build ARGB output directly (avoids view-aliasing bugs from mutating px)
        argb = np.empty_like(px)
        # Alpha channel
        argb[:, 0] = a
        # Full alpha → just copy RGB
        argb[mask_full, 1] = r[mask_full]
        argb[mask_full, 2] = g[mask_full]
        argb[mask_full, 3] = b[mask_full]
        # Partial alpha → premultiply RGB
        if mask_partial.any():
            af = a[mask_partial].astype(np.uint16)
            argb[mask_partial, 1] = ((r[mask_partial].astype(np.uint16) * af + 127) // 255).astype(np.uint8)
            argb[mask_partial, 2] = ((g[mask_partial].astype(np.uint16) * af + 127) // 255).astype(np.uint8)
            argb[mask_partial, 3] = ((b[mask_partial].astype(np.uint16) * af + 127) // 255).astype(np.uint8)
        # Zero alpha → all zero
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


def build_define_bits_lossless(
    char_id: int,
    width: int,
    height: int,
    pixel_data: bytes,
) -> bytes:
    """Build a DefineBitsLossless tag (tag 20) for 24-bit RGB images.

    `pixel_data` should be raw RGBA bytes (4 bytes per pixel).
    We strip the alpha channel and pad rows to 4-byte alignment as SWF requires.
    """
    log.debug("build_define_bits_lossless: char_id=%d %dx%d", char_id, width, height)
    # Convert RGBA → RGB, padded to 4-byte row alignment
    # SWF DefineBitsLossless format 5 (24-bit) pads each row to 4-byte boundary
    # Each pixel = 1 byte padding + R + G + B (PIX24 = 0x00, R, G, B)
    row_stride = width * 4  # 4 bytes per pixel in PIX24 format (pad, R, G, B)
    rgb_buf = bytearray(row_stride * height)
    for y in range(height):
        for x in range(width):
            src = (y * width + x) * 4
            dst = y * row_stride + x * 4
            r = pixel_data[src] if src < len(pixel_data) else 0
            g = pixel_data[src + 1] if src + 1 < len(pixel_data) else 0
            b = pixel_data[src + 2] if src + 2 < len(pixel_data) else 0
            rgb_buf[dst] = 0       # reserved/padding byte
            rgb_buf[dst + 1] = r
            rgb_buf[dst + 2] = g
            rgb_buf[dst + 3] = b

    compressed = zlib.compress(bytes(rgb_buf), 6)

    body = io.BytesIO()
    body.write(struct.pack("<H", char_id))
    body.write(struct.pack("<B", 5))    # BitmapFormat = 5 (24-bit RGB)
    body.write(struct.pack("<H", width))
    body.write(struct.pack("<H", height))
    body.write(compressed)
    return build_tag(TAG_DEFINE_BITS_LOSSLESS, body.getvalue())


def build_define_bits_jpeg3(
    char_id: int,
    width: int,
    height: int,
    pixel_data: bytes,
    jpeg_quality: int = 90,
) -> bytes:
    """Build a DefineBitsJPEG3 tag (tag 35): JPEG data + zlib-compressed alpha.

    `pixel_data` should be raw RGBA bytes.  We encode the RGB channels as JPEG
    and the alpha channel as a separate zlib-compressed table.
    """
    log.debug("build_define_bits_jpeg3: char_id=%d %dx%d q=%d", char_id, width, height, jpeg_quality)
    try:
        from PIL import Image as _PilImage
    except ImportError:
        # Fallback to DefineBitsLossless2 if Pillow not available
        log.warning("Pillow not available — falling back to DefineBitsLossless2")
        return build_define_bits_lossless2(char_id, width, height, pixel_data)

    import numpy as np

    # Separate RGBA into RGB and A
    px = np.frombuffer(pixel_data, dtype=np.uint8).reshape(height, width, 4)
    rgb_img = _PilImage.fromarray(px[:, :, :3], 'RGB')
    alpha = px[:, :, 3].tobytes()

    # Encode RGB as JPEG
    jpeg_buf = io.BytesIO()
    rgb_img.save(jpeg_buf, format='JPEG', quality=jpeg_quality)
    jpeg_bytes = jpeg_buf.getvalue()

    # Compress alpha table with zlib
    alpha_compressed = zlib.compress(alpha, 6)

    # DefineBitsJPEG3 body: charId(2) + AlphaDataOffset(4) + JPEG data + zlib alpha
    body = io.BytesIO()
    body.write(struct.pack("<H", char_id))
    body.write(struct.pack("<I", len(jpeg_bytes)))  # AlphaDataOffset
    body.write(jpeg_bytes)
    body.write(alpha_compressed)

    TAG_DEFINE_BITS_JPEG3 = 35
    return build_tag(TAG_DEFINE_BITS_JPEG3, body.getvalue())
