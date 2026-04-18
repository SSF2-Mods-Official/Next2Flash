"""
Deep parse of shape 635 (RT-only) and shape 604 (OG+RT) to verify whether
the e903 bytes are genuine bitmap fill charID references.

Also: find every sprite that references shape 635, and their placement depth context.
"""
import struct, zlib, io, sys

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

TARGET_CID = 1001

def read_swf(path):
    d = open(path,'rb').read()
    if d[:3]==b'CWS': d = d[:8]+zlib.decompress(d[8:])
    return d

def swf_header_end(d):
    pos = 8
    nb = (d[pos]>>3)&0x1f
    pos += (5+nb*4+7)//8 + 4
    return pos

def iter_tags_toplevel(d):
    pos = swf_header_end(d)
    while pos+1 < len(d):
        hdr = struct.unpack_from('<H',d,pos)[0]; tt=hdr>>6; sl=hdr&0x3f; pos+=2
        if sl==0x3f: l=struct.unpack_from('<I',d,pos)[0]; pos+=4
        else: l=sl
        pay = d[pos:pos+l]
        if tt==0: break
        yield tt, pay, pos
        pos += l


# ─── Bitfield reader for SWF RECT and MATRIX ──────────────────────────────────

class BitReader:
    def __init__(self, data, byte_off=0):
        self._d = data; self._bo = byte_off*8
    def seek_byte(self, byte_off):
        self._bo = byte_off*8
    def read_bits(self, n):
        v = 0
        for _ in range(n):
            byte = self._bo//8; bit = 7-(self._bo%8)
            v = (v<<1)|((self._d[byte]>>bit)&1)
            self._bo += 1
        return v
    def read_sign(self, n):
        v = self.read_bits(n)
        if v >= (1<<(n-1)): v -= (1<<n)
        return v
    def byte_align(self):
        if self._bo%8: self._bo += 8-(self._bo%8)
    def byte_pos(self): return (self._bo+7)//8

def skip_rect(data, pos):
    br = BitReader(data, pos)
    nb = br.read_bits(5)
    br.read_bits(nb*4)
    br.byte_align()
    return br.byte_pos()

def skip_matrix(data, pos):
    br = BitReader(data, pos)
    has_scale = br.read_bits(1)
    if has_scale:
        nb = br.read_bits(5); br.read_bits(nb*2)
    has_rotate = br.read_bits(1)
    if has_rotate:
        nb = br.read_bits(5); br.read_bits(nb*2)
    nb = br.read_bits(5); br.read_bits(nb*2)  # translate always present
    br.byte_align()
    return br.byte_pos()

def skip_cxform(data, pos, with_alpha):
    br = BitReader(data, pos)
    has_add = br.read_bits(1); has_mult = br.read_bits(1)
    nb = br.read_bits(4)
    if has_mult: br.read_bits(nb * (4 if with_alpha else 3))
    if has_add:  br.read_bits(nb * (4 if with_alpha else 3))
    br.byte_align()
    return br.byte_pos()

# ─── FILLSTYLEARRAY parser ─────────────────────────────────────────────────────

def parse_fillstyle(data, pos, with_alpha):
    """
    Parse one FillStyle. Returns (fill_type, bitmap_cid, new_pos).
    bitmap_cid is None for non-bitmap fills.
    May raise if data runs out.
    """
    ft = data[pos]; pos += 1
    if ft == 0x00:           # solid
        if with_alpha: pos += 4  # RGBA
        else:           pos += 3  # RGB
        return ft, None, pos
    elif ft in (0x10, 0x12, 0x13):  # gradient
        pos = skip_matrix(data, pos)
        # GradientFill body: SpreadMode(2)+InterpolationMode(2)+NumGradients(4) + N*(Ratio+Color)
        # BUT for DS3/with_alpha gradient has extra byte
        if pos >= len(data): return ft, None, pos
        num_grads = data[pos] & 0x0F; pos += 1
        for _ in range(num_grads):
            pos += 1  # ratio
            if with_alpha: pos += 4  # RGBA
            else:           pos += 3  # RGB
        if ft == 0x13:  # FocalGradient — extra FocalPoint FIXED8
            pos += 2
        return ft, None, pos
    elif ft in (0x40, 0x41, 0x42, 0x43):  # bitmap
        cid = struct.unpack_from('<H', data, pos)[0]; pos += 2
        pos = skip_matrix(data, pos)
        return ft, cid, pos
    else:
        raise ValueError(f"Unknown fill type 0x{ft:02x} at payload offset {pos-1}")


def parse_fillstyle_array(data, start, with_alpha):
    """Returns (list of (ft, cid), new_pos)"""
    pos = start
    count = data[pos]; pos += 1
    if count == 0xFF:
        count = struct.unpack_from('<H', data, pos)[0]; pos += 2
    results = []
    for i in range(count):
        ft, cid, pos = parse_fillstyle(data, pos, with_alpha)
        results.append((ft, cid))
    return results, pos


def parse_linestyle(data, pos, with_alpha):
    """Skip one line style. Returns new_pos."""
    pos += 2  # width
    if with_alpha: pos += 4  # RGBA
    else:           pos += 3  # RGB
    return pos


def parse_linestyle_array(data, start, with_alpha):
    """Returns (count, new_pos), skipping all line styles."""
    pos = start
    count = data[pos]; pos += 1
    if count == 0xFF:
        count = struct.unpack_from('<H', data, pos)[0]; pos += 2
    for _ in range(count):
        pos = parse_linestyle(data, pos, with_alpha)
    return count, pos


def parse_defineshape(tag_type, payload):
    """
    Return (charID, list of (fill_type, bitmap_cid)).
    tag_type: 2=DS1, 22=DS2, 32=DS3, 83=DS4
    """
    with_alpha = (tag_type >= 32)
    cid = struct.unpack_from('<H', payload)[0]
    # skip bounds rect
    pos = skip_rect(payload, 2)
    if tag_type == 83:       # DS4 has extra UsesFillWindingRule + HasNonScalingStrokes etc.
        pos = skip_rect(payload, pos)    # EdgeBounds
        pos += 1                         # flags byte
    fills, pos = parse_fillstyle_array(payload, pos, with_alpha)
    return cid, fills


# ─── Sprite inner-tag parser ───────────────────────────────────────────────────

def iter_sprite_inner(payload):
    pos = 4
    while pos+1 < len(payload):
        hdr = struct.unpack_from('<H',payload,pos)[0]; tt=hdr>>6; sl=hdr&0x3f; pos+=2
        if sl==0x3f: l=struct.unpack_from('<I',payload,pos)[0]; pos+=4
        else: l=sl
        sp = payload[pos:pos+l]
        if tt==0: break
        yield tt, sp
        pos += l


# ─── Main analysis ─────────────────────────────────────────────────────────────

def analyze(path, label):
    data = read_swf(path)
    tags = list(iter_tags_toplevel(data))

    # Collect all shapes
    shapes = {}   # charID -> (tag_type, fills)
    for tt, pay, _ in tags:
        if tt in (2, 22, 32, 83) and len(pay) >= 2:
            try:
                cid, fills = parse_defineshape(tt, pay)
                shapes[cid] = (tt, fills)
            except Exception as ex:
                cid2 = struct.unpack_from('<H', pay)[0] if len(pay)>=2 else '?'
                print(f"  [{label}] WARNING: shape cid={cid2} parse error: {ex}")

    # Collect all sprites: charID -> payload
    sprites = {}
    for tt, pay, _ in tags:
        if tt == 39 and len(pay) >= 2:
            cid = struct.unpack_from('<H', pay)[0]
            sprites[cid] = pay

    # ── Inspect shape 604 and 635 ──
    for shape_cid in (604, 635):
        if shape_cid not in shapes:
            print(f"\n  [{label}] Shape {shape_cid}: NOT PRESENT")
            continue
        tt, fills = shapes[shape_cid]
        tn = {2:'DS1',22:'DS2',32:'DS3',83:'DS4'}.get(tt,f'tag{tt}')
        bmp_fills = [(i,ft,cid) for i,(ft,cid) in enumerate(fills) if cid is not None]
        print(f"\n  [{label}] Shape {shape_cid} ({tn}): {len(fills)} fill style(s), {len(bmp_fills)} bitmap fill(s)")
        for idx, ft, cid in bmp_fills:
            marker = " *** TARGET ***" if cid == TARGET_CID else ""
            print(f"    Fill[{idx}] type=0x{ft:02x}, bitmapCID={cid}{marker}")

    # ── Which sprites place shape 635? ──
    shape_of_interest = 635
    sprites_using_635 = {}  # sp_cid -> [(frame, depth, po_type, has_image)]
    for sp_cid, sp_pay in sprites.items():
        frames_info = []
        frame = 1
        for stt, sp in iter_sprite_inner(sp_pay):
            if stt == 1:  # ShowFrame
                frame += 1
            elif stt == 70 and len(sp) >= 6:  # PO3
                flags1 = sp[0]; flags2 = sp[1]
                depth = struct.unpack_from('<H', sp, 2)[0]
                has_char = (flags1>>1)&1
                has_image = (flags2>>4)&1
                if has_char:
                    cid = struct.unpack_from('<H', sp, 4)[0]
                    if cid == shape_of_interest:
                        frames_info.append((frame, depth, 'PO3', has_image))
            elif stt == 26 and len(sp) >= 5:  # PO2
                flags = sp[0]; has_char = (flags>>1)&1
                if has_char:
                    depth = struct.unpack_from('<H', sp, 1)[0]
                    cid = struct.unpack_from('<H', sp, 3)[0]
                    if cid == shape_of_interest:
                        frames_info.append((frame, depth, 'PO2', 0))
        if frames_info:
            sprites_using_635[sp_cid] = frames_info

    print(f"\n  [{label}] Sprites referencing shape 635:")
    if not sprites_using_635:
        print("    (none)")
    else:
        for sp_cid, placements in sorted(sprites_using_635.items()):
            # Show first placement + total count
            print(f"    Sprite {sp_cid}: {len(placements)} placement(s)")
            for fr, dep, po, hi in placements[:3]:
                print(f"      Frame {fr}, depth={dep}, {po}, has_image={hi}")
            if len(placements) > 3:
                print(f"      ... +{len(placements)-3} more")

    # ── Also confirm: which sprites reference charID=1001 directly ──
    print(f"\n  [{label}] Full chain: sprites placing charID={TARGET_CID}:")
    for sp_cid, sp_pay in sprites.items():
        frame = 1
        for stt, sp in iter_sprite_inner(sp_pay):
            if stt == 1: frame += 1
            elif stt == 70 and len(sp) >= 6:
                flags2 = sp[1]; flags1 = sp[0]
                has_char = (flags1>>1)&1; has_image=(flags2>>4)&1
                if has_char:
                    cid = struct.unpack_from('<H',sp,4)[0]
                    if cid == TARGET_CID:
                        print(f"    Sprite {sp_cid} frame {frame} depth={struct.unpack_from('<H',sp,2)[0]} PO3(has_image={has_image})")

    # ── Find what shape in OG corresponds to 635-region (by content search) ──
    # Check if shape 635 exists in OG at all (as different charID perhaps via raw byte)
    if label == 'RT':
        print(f"\n  [RT] Shape 635 raw bytes in SWF (first 50 bytes of payload):")
        for tt, pay, _ in tags:
            if tt in (2,22,32,83) and len(pay)>=2:
                cid2 = struct.unpack_from('<H',pay)[0]
                if cid2 == 635:
                    print(f"    {pay[:50].hex()}")
                    # Also check which bytes surround offset 1006
                    if len(pay) > 1010:
                        ctx_start = max(0, 1004)
                        ctx_bytes = pay[ctx_start:ctx_start+8]
                        print(f"    Bytes at payload[1004:1012]: {ctx_bytes.hex()}")
                        print(f"    Byte at [1005] = 0x{pay[1005]:02x}  (should be 0x40-0x43 if bitmap fill type)")
                    break


print("=" * 70)
print("ANALYZING OG")
print("=" * 70)
analyze(OG, 'OG')

print()
print("=" * 70)
print("ANALYZING RT")
print("=" * 70)
analyze(RT, 'RT')

print("\nDone.")
