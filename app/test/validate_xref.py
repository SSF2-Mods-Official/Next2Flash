#!/usr/bin/env python3
"""
SWF Cross-Reference Integrity Validator

Parses a compiled SWF and checks that every charID reference
(PlaceObject, bitmap fills, font refs) points to a valid define tag.
Catches "red box" and missing-asset bugs that structural tag-count tests miss.

Usage:
    python test/validate_xref.py path/to/file.swf
    python test/validate_xref.py --dir path/to/dir   # validate all .swf/.ssf
"""
import os
import struct
import sys
import zlib

# ── Tag type sets ────────────────────────────────────────────────────────

DEFINE_TAGS = {2, 22, 32, 83, 6, 21, 35, 90, 20, 36, 39, 46, 84,
               11, 33, 48, 75, 10, 14, 37, 87}

BITMAP_TAGS = {6, 21, 35, 90, 20, 36}   # all bitmap define tags
FONT_TAGS   = {10, 48, 75}               # DefineFont, DefineFont2, DefineFont3
SHAPE_TAGS  = {2, 22, 32, 83}            # DefineShape 1-4

TAG_NAMES = {
    0: 'End', 1: 'ShowFrame', 2: 'DefineShape', 5: 'RemoveObject',
    6: 'DefineBits', 9: 'SetBgColor', 10: 'DefineFont', 11: 'DefineText',
    14: 'DefineSound', 20: 'DefineBitsLossless', 21: 'DefineBitsJPEG2',
    22: 'DefineShape2', 26: 'PlaceObject2', 32: 'DefineShape3',
    33: 'DefineText2', 35: 'DefineBitsJPEG3', 36: 'DefineBitsLossless2',
    37: 'DefineEditText', 39: 'DefineSprite', 46: 'DefineMorphShape',
    48: 'DefineFont2', 69: 'FileAttributes', 70: 'PlaceObject3',
    75: 'DefineFont3', 76: 'SymbolClass', 82: 'DoABC2',
    83: 'DefineShape4', 84: 'DefineMorphShape2', 87: 'DefineBinaryData',
    90: 'DefineBitsJPEG4',
}


def tag_name(tt):
    return TAG_NAMES.get(tt, f'tag{tt}')


# ── SWF Parsing ──────────────────────────────────────────────────────────

def parse_swf(data):
    """Parse SWF bytes → list of (tag_type, body_bytes)."""
    magic = data[:3]
    if magic == b'CWS':
        data = data[:8] + zlib.decompress(data[8:])
    elif magic == b'ZWS':
        import lzma
        data = data[:8] + lzma.decompress(data[12:])
    elif magic != b'FWS':
        raise ValueError(f"Bad SWF magic: {magic!r}")

    nbits = (data[8] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_end = 8 + (total_bits + 7) // 8
    pos = rect_end + 4
    tags = []
    while pos < len(data):
        if pos + 2 > len(data):
            break
        h = struct.unpack_from('<H', data, pos)[0]
        tt = h >> 6
        ln = h & 0x3F
        hdr = 2
        if ln == 0x3F:
            if pos + 6 > len(data):
                break
            ln = struct.unpack_from('<I', data, pos + 2)[0]
            hdr = 6
        body = data[pos + hdr: pos + hdr + ln]
        tags.append((tt, body))
        pos += hdr + ln
        if tt == 0:
            break
    return tags


def parse_sprite_tags(body):
    """Parse sub-tags inside a DefineSprite body (after charID+frameCount)."""
    data = body[4:]  # skip charID(2) + frameCount(2) — but body already lacks charID
    # Actually body here is the full tag body which starts with charID
    # We skip charID(2) + frameCount(2) = 4 bytes
    tags = []
    pos = 0
    while pos < len(data):
        if pos + 2 > len(data):
            break
        h = struct.unpack_from('<H', data, pos)[0]
        tt = h >> 6
        ln = h & 0x3F
        hdr = 2
        if ln == 0x3F:
            if pos + 6 > len(data):
                break
            ln = struct.unpack_from('<I', data, pos + 2)[0]
            hdr = 6
        sub_body = data[pos + hdr: pos + hdr + ln]
        tags.append((tt, sub_body))
        pos += hdr + ln
        if tt == 0:
            break
    return tags


# ── Bit reader helper ────────────────────────────────────────────────────

class BitReader:
    """Read bits from a byte buffer."""
    def __init__(self, buf, byte_offset=0):
        self.buf = buf
        self.byte_off = byte_offset
        self.bit_pos = 0

    def read(self, n):
        result = 0
        for _ in range(n):
            if self.byte_off >= len(self.buf):
                raise IndexError("BitReader overrun")
            result = (result << 1) | ((self.buf[self.byte_off] >> (7 - self.bit_pos)) & 1)
            self.bit_pos += 1
            if self.bit_pos >= 8:
                self.bit_pos = 0
                self.byte_off += 1
        return result

    def read_signed(self, n):
        val = self.read(n)
        if n > 0 and val >= (1 << (n - 1)):
            val -= (1 << n)
        return val

    def align(self):
        if self.bit_pos > 0:
            self.bit_pos = 0
            self.byte_off += 1

    @property
    def pos(self):
        return self.byte_off


def skip_rect(buf, off):
    """Skip a RECT record, return offset after it."""
    br = BitReader(buf, off)
    nbits = br.read(5)
    br.read_signed(nbits)  # Xmin
    br.read_signed(nbits)  # Xmax
    br.read_signed(nbits)  # Ymin
    br.read_signed(nbits)  # Ymax
    br.align()
    return br.pos


def skip_matrix(buf, off):
    """Skip a MATRIX record, return offset after it."""
    br = BitReader(buf, off)
    has_scale = br.read(1)
    if has_scale:
        nb = br.read(5)
        br.read(nb)  # scaleX
        br.read(nb)  # scaleY
    has_rotate = br.read(1)
    if has_rotate:
        nb = br.read(5)
        br.read(nb)  # rotateSkew0
        br.read(nb)  # rotateSkew1
    nb = br.read(5)
    br.read(nb)  # translateX
    br.read(nb)  # translateY
    br.align()
    return br.pos


# ── Reference extractors ─────────────────────────────────────────────────

def extract_place_object_ref(tag_type, body):
    """Extract charID from PlaceObject2 (26) or PlaceObject3 (70).
    Returns charID or None if no character reference."""
    if tag_type == 26 and len(body) >= 5:
        flags = body[0]
        if flags & 0x02:  # HasCharacter
            return struct.unpack_from('<H', body, 3)[0]
    elif tag_type == 70 and len(body) >= 6:
        flags = body[0]
        if flags & 0x02:  # HasCharacter
            return struct.unpack_from('<H', body, 4)[0]
    return None


def extract_shape_bitmap_refs(body_after_cid, tag_type):
    """Extract all bitmap charIDs referenced in shape fill styles.
    body_after_cid = tag body with charID already stripped (first 2 bytes removed).
    Returns list of (bitmap_char_id, description)."""
    refs = []
    buf = body_after_cid
    if len(buf) < 4:
        return refs

    try:
        # Skip shape bounds RECT
        off = skip_rect(buf, 0)

        # DefineShape4 (tag 83): extra edge-bounds RECT + 1 byte flags
        if tag_type == 83:
            off = skip_rect(buf, off)
            off += 1  # flags byte

        # Parse fill style array
        count = buf[off]; off += 1
        if tag_type not in (2,) and count == 0xFF:
            count = buf[off] | (buf[off + 1] << 8); off += 2

        color_size = 4 if tag_type in (32, 83) else 3

        for i in range(count):
            if off >= len(buf):
                break
            ft = buf[off]; off += 1

            if ft == 0x00:
                # Solid fill: RGB or RGBA
                off += color_size
            elif ft in (0x10, 0x12):
                # Gradient fill: MATRIX + GRADIENT
                off = skip_matrix(buf, off)
                off = _skip_gradient_data(buf, off, color_size)
            elif ft == 0x13:
                # Focal gradient: MATRIX + FOCALGRADIENT
                off = skip_matrix(buf, off)
                off = _skip_gradient_data(buf, off, color_size)
                off += 2  # FIXED8 focalPoint
            elif ft in (0x40, 0x41, 0x42, 0x43):
                # Bitmap fill: UI16 bitmapId + MATRIX
                bmp_id = buf[off] | (buf[off + 1] << 8)
                off += 2
                off = skip_matrix(buf, off)
                if bmp_id != 0xFFFF:  # 0xFFFF = placeholder
                    refs.append((bmp_id, f"fillStyle[{i}] type=0x{ft:02X}"))
            else:
                # Unknown fill type — stop parsing to avoid errors
                break
    except (IndexError, KeyError):
        pass  # partial parse is fine, we report what we found

    return refs


def _skip_gradient_data(buf, off, color_size):
    """Skip gradient record data (after MATRIX)."""
    br = BitReader(buf, off)
    _spread = br.read(2)
    _interp = br.read(2)
    num_grads = br.read(4)
    br.align()
    off = br.pos
    # Each gradient record: UI8 ratio + color
    off += num_grads * (1 + color_size)
    return off


def extract_morph_shape_bitmap_refs(body_after_cid, tag_type):
    """Extract bitmap charIDs from DefineMorphShape/DefineMorphShape2 fill styles."""
    refs = []
    buf = body_after_cid
    if len(buf) < 10:
        return refs

    try:
        off = 0
        # StartBounds + EndBounds
        off = skip_rect(buf, off)
        off = skip_rect(buf, off)

        # MorphShape2: extra edge bounds + flags
        if tag_type == 84:
            off = skip_rect(buf, off)
            off = skip_rect(buf, off)
            off += 1  # flags

        off += 4  # Offset UI32

        # MorphFillStyleCount
        count = buf[off]; off += 1
        if count == 0xFF:
            count = buf[off] | (buf[off + 1] << 8); off += 2

        for i in range(count):
            if off >= len(buf):
                break
            ft = buf[off]; off += 1
            if ft == 0x00:
                off += 8  # Start RGBA + End RGBA
            elif ft in (0x10, 0x12):
                off = skip_matrix(buf, off)  # start matrix
                off = skip_matrix(buf, off)  # end matrix
                off = _skip_morph_gradient(buf, off)
            elif ft == 0x13:
                off = skip_matrix(buf, off)
                off = skip_matrix(buf, off)
                off = _skip_morph_gradient(buf, off)
            elif ft in (0x40, 0x41, 0x42, 0x43):
                bmp_id = buf[off] | (buf[off + 1] << 8)
                off += 2
                off = skip_matrix(buf, off)  # start
                off = skip_matrix(buf, off)  # end
                if bmp_id != 0xFFFF:
                    refs.append((bmp_id, f"morphFill[{i}] type=0x{ft:02X}"))
            else:
                break
    except (IndexError, KeyError):
        pass
    return refs


def _skip_morph_gradient(buf, off):
    """Skip morph gradient data."""
    br = BitReader(buf, off)
    _spread = br.read(2)
    _interp = br.read(2)
    num_grads = br.read(4)
    br.align()
    off = br.pos
    # Each morph grad: ratio(1) + startRGBA(4) + ratio(1) + endRGBA(4) = 10
    off += num_grads * 10
    return off


def extract_text_font_refs(body_after_cid, tag_type):
    """Extract font charIDs from DefineText (11) / DefineText2 (33) body.
    body_after_cid = body with charID stripped."""
    refs = []
    buf = body_after_cid
    if len(buf) < 6:
        return refs

    try:
        off = skip_rect(buf, 0)     # bounds RECT
        off = skip_matrix(buf, off)  # text matrix

        glyph_bits = buf[off]; off += 1
        advance_bits = buf[off]; off += 1

        rec_idx = 0
        while off < len(buf):
            flags = buf[off]; off += 1
            if flags == 0:
                break  # end of text records

            has_font = bool(flags & 0x08)
            has_color = bool(flags & 0x04)
            has_y_off = bool(flags & 0x02)
            has_x_off = bool(flags & 0x01)

            if has_font:
                fid = buf[off] | (buf[off + 1] << 8)
                off += 2
                refs.append((fid, f"textRecord[{rec_idx}]"))
            if has_color:
                off += 4 if tag_type == 33 else 3  # RGBA vs RGB
            if has_y_off:
                off += 2
            if has_x_off:
                off += 2
            if has_font:
                off += 2  # textHeight

            glyph_count = buf[off]; off += 1
            total_bits = glyph_count * (glyph_bits + advance_bits)
            off += (total_bits + 7) // 8
            rec_idx += 1
    except (IndexError, KeyError):
        pass
    return refs


def extract_edit_text_font_ref(body_after_cid):
    """Extract font charID from DefineEditText (37) body.
    body_after_cid = body with charID stripped."""
    buf = body_after_cid
    if len(buf) < 4:
        return None
    try:
        off = skip_rect(buf, 0)  # bounds RECT
        flags1 = buf[off]; off += 1
        _flags2 = buf[off]; off += 1
        if flags1 & 0x01:  # HasFont
            fid = buf[off] | (buf[off + 1] << 8)
            return fid
    except (IndexError, KeyError):
        pass
    return None


# ── Main Validator ────────────────────────────────────────────────────────

class XRefIssue:
    """A single cross-reference integrity issue."""
    __slots__ = ('severity', 'context', 'message')

    ERROR = 'ERROR'
    WARN = 'WARN'

    def __init__(self, severity, context, message):
        self.severity = severity
        self.context = context
        self.message = message

    def __str__(self):
        return f"[{self.severity}] {self.context}: {self.message}"

    def __repr__(self):
        return self.__str__()


def validate_swf_xrefs(swf_data):
    """Validate all charID cross-references in a SWF.

    Returns a list of XRefIssue objects. Empty list = clean.
    """
    tags = parse_swf(swf_data)
    issues = []

    # Step 1: Build set of all defined charIDs and their types
    defined = {}  # charID → tag_type
    for tt, body in tags:
        if tt in DEFINE_TAGS and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            defined[cid] = tt

    # Step 2: Check top-level PlaceObject2/3 references
    for idx, (tt, body) in enumerate(tags):
        if tt in (26, 70):
            ref = extract_place_object_ref(tt, body)
            if ref is not None and ref not in defined:
                issues.append(XRefIssue(
                    XRefIssue.ERROR,
                    f"root {tag_name(tt)} #{idx}",
                    f"references charID {ref} which is not defined"))

    # Step 3: Check shape bitmap fill references
    for tt, body in tags:
        if tt in SHAPE_TAGS and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            bitmap_refs = extract_shape_bitmap_refs(body[2:], tt)
            for bmp_id, desc in bitmap_refs:
                if bmp_id not in defined:
                    issues.append(XRefIssue(
                        XRefIssue.ERROR,
                        f"{tag_name(tt)} charID={cid}",
                        f"{desc} references bitmap charID {bmp_id} which is not defined"))
                elif defined[bmp_id] not in BITMAP_TAGS:
                    issues.append(XRefIssue(
                        XRefIssue.WARN,
                        f"{tag_name(tt)} charID={cid}",
                        f"{desc} references charID {bmp_id} as bitmap "
                        f"but it is {tag_name(defined[bmp_id])}"))

    # Step 4: Check morph shape bitmap refs
    for tt, body in tags:
        if tt in (46, 84) and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            bitmap_refs = extract_morph_shape_bitmap_refs(body[2:], tt)
            for bmp_id, desc in bitmap_refs:
                if bmp_id not in defined:
                    issues.append(XRefIssue(
                        XRefIssue.ERROR,
                        f"{tag_name(tt)} charID={cid}",
                        f"{desc} references bitmap charID {bmp_id} which is not defined"))

    # Step 5: Check DefineText/DefineText2 font references
    for tt, body in tags:
        if tt in (11, 33) and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            font_refs = extract_text_font_refs(body[2:], tt)
            for fid, desc in font_refs:
                if fid not in defined:
                    issues.append(XRefIssue(
                        XRefIssue.ERROR,
                        f"{tag_name(tt)} charID={cid}",
                        f"{desc} references font charID {fid} which is not defined"))
                elif defined[fid] not in FONT_TAGS:
                    issues.append(XRefIssue(
                        XRefIssue.WARN,
                        f"{tag_name(tt)} charID={cid}",
                        f"{desc} references charID {fid} as font "
                        f"but it is {tag_name(defined[fid])}"))

    # Step 6: Check DefineEditText font references
    for tt, body in tags:
        if tt == 37 and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            fid = extract_edit_text_font_ref(body[2:])
            if fid is not None and fid not in defined:
                issues.append(XRefIssue(
                    XRefIssue.ERROR,
                    f"DefineEditText charID={cid}",
                    f"references font charID {fid} which is not defined"))
            elif fid is not None and defined.get(fid) not in FONT_TAGS:
                issues.append(XRefIssue(
                    XRefIssue.WARN,
                    f"DefineEditText charID={cid}",
                    f"references charID {fid} as font "
                    f"but it is {tag_name(defined.get(fid, 0))}"))

    # Step 7: Check DefineSprite sub-tag references (recursive)
    for tt, body in tags:
        if tt == 39 and len(body) >= 4:
            sprite_cid = struct.unpack_from('<H', body, 0)[0]
            # frameCount at bytes 2-3, sub-tags start at byte 4
            sub_tags = parse_sprite_tags(body)
            for sub_idx, (sub_tt, sub_body) in enumerate(sub_tags):
                if sub_tt in (26, 70):
                    ref = extract_place_object_ref(sub_tt, sub_body)
                    if ref is not None and ref not in defined:
                        issues.append(XRefIssue(
                            XRefIssue.ERROR,
                            f"DefineSprite charID={sprite_cid}",
                            f"sub-tag {tag_name(sub_tt)} #{sub_idx} "
                            f"references charID {ref} which is not defined"))
                elif sub_tt == 15 and len(sub_body) >= 2:
                    # StartSound: UI16 soundId
                    snd_id = struct.unpack_from('<H', sub_body, 0)[0]
                    if snd_id not in defined:
                        issues.append(XRefIssue(
                            XRefIssue.ERROR,
                            f"DefineSprite charID={sprite_cid}",
                            f"StartSound #{sub_idx} references sound charID "
                            f"{snd_id} which is not defined"))
                elif sub_tt == 89 and len(sub_body) >= 2:
                    # StartSound2 has a name not a charID — skip
                    pass

    # Step 8: Check SymbolClass references
    for tt, body in tags:
        if tt == 76 and len(body) >= 2:
            count = struct.unpack_from('<H', body, 0)[0]
            off = 2
            for _ in range(count):
                if off + 2 > len(body):
                    break
                cid = struct.unpack_from('<H', body, off)[0]
                off += 2
                # Skip null-terminated name
                while off < len(body) and body[off] != 0:
                    off += 1
                off += 1
                # charID 0 = main timeline, valid
                if cid != 0 and cid not in defined:
                    issues.append(XRefIssue(
                        XRefIssue.ERROR,
                        "SymbolClass",
                        f"references charID {cid} which is not defined"))

    return issues


def validate_swf_file(path):
    """Validate a SWF file. Returns list of XRefIssue."""
    with open(path, 'rb') as f:
        data = f.read()
    return validate_swf_xrefs(data)


# ── CLI ───────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate SWF cross-references")
    parser.add_argument('path', help='SWF file or directory')
    parser.add_argument('--dir', action='store_true',
                        help='Treat path as directory, validate all .swf/.ssf')
    args = parser.parse_args()

    if args.dir or os.path.isdir(args.path):
        files = []
        for root, dirs, fnames in os.walk(args.path):
            for fn in sorted(fnames):
                if fn.lower().endswith(('.swf', '.ssf')):
                    files.append(os.path.join(root, fn))
        files.sort()
    else:
        files = [args.path]

    total_errors = 0
    total_warnings = 0
    clean = 0

    for f in files:
        rel = os.path.relpath(f, args.path) if len(files) > 1 else f
        issues = validate_swf_file(f)
        errors = [i for i in issues if i.severity == XRefIssue.ERROR]
        warnings = [i for i in issues if i.severity == XRefIssue.WARN]

        if not issues:
            clean += 1
            if len(files) <= 20:
                print(f"  OK  {rel}")
        else:
            print(f"  {'FAIL' if errors else 'WARN'}  {rel}  "
                  f"({len(errors)} errors, {len(warnings)} warnings)")
            for issue in issues:
                print(f"        {issue}")

        total_errors += len(errors)
        total_warnings += len(warnings)

    print()
    print(f"{'='*60}")
    print(f"Files: {len(files)}  Clean: {clean}  "
          f"Errors: {total_errors}  Warnings: {total_warnings}")

    return 1 if total_errors > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
