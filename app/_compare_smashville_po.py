"""Byte-level comparison of PlaceObject tags in smashville_bg sprite between OG and RT."""
import struct, zlib, sys, math

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\stage\smashville.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\stage\smashville.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        data = b'FWS' + data[3:8] + zlib.decompress(data[8:])
    return data

def parse_tags(data, offset, end=None):
    if end is None: end = len(data)
    tags = []
    while offset < end:
        if offset + 2 > end: break
        hdr = struct.unpack_from('<H', data, offset)[0]
        tt = hdr >> 6; length = hdr & 0x3F; offset += 2
        if length == 0x3F:
            length = struct.unpack_from('<I', data, offset)[0]; offset += 4
        td = data[offset:offset+length]; tags.append((tt, td)); offset += length
        if tt == 0: break
    return tags

def parse_rect(data, bit_off=0):
    byte_i = bit_off // 8; bit_i = bit_off % 8
    nbits = 0
    for i in range(5):
        nbits = (nbits << 1) | ((data[byte_i + (bit_i+i)//8] >> (7-(bit_i+i)%8)) & 1)
    return (5 + nbits * 4 + 7) // 8

def skip_header(data):
    return 8 + parse_rect(data, 64) + 4

class BitReader:
    def __init__(self, data, byte_offset=0):
        self.data = data
        self.bit_pos = byte_offset * 8
    
    def read_bits(self, n):
        val = 0
        for _ in range(n):
            byte_i = self.bit_pos // 8
            bit_i = 7 - (self.bit_pos % 8)
            if byte_i < len(self.data):
                val = (val << 1) | ((self.data[byte_i] >> bit_i) & 1)
            else:
                val = val << 1
            self.bit_pos += 1
        return val
    
    def read_sbits(self, n):
        val = self.read_bits(n)
        if n > 0 and (val & (1 << (n-1))):
            val -= (1 << n)
        return val
    
    def read_fbits(self, n):
        return self.read_sbits(n) / 65536.0
    
    def align(self):
        if self.bit_pos % 8:
            self.bit_pos = (self.bit_pos // 8 + 1) * 8
    
    @property
    def byte_pos(self):
        return (self.bit_pos + 7) // 8

def decode_matrix(data, offset):
    """Decode a MATRIX structure. Returns (dict, bytes_consumed)."""
    br = BitReader(data, offset)
    result = {}
    
    has_scale = br.read_bits(1)
    if has_scale:
        n = br.read_bits(5)
        result['scaleX'] = br.read_fbits(n)
        result['scaleY'] = br.read_fbits(n)
    
    has_rotate = br.read_bits(1)
    if has_rotate:
        n = br.read_bits(5)
        result['rotateSkew0'] = br.read_fbits(n)
        result['rotateSkew1'] = br.read_fbits(n)
    
    n_translate = br.read_bits(5)
    if n_translate:
        result['translateX'] = br.read_sbits(n_translate)
        result['translateY'] = br.read_sbits(n_translate)
    
    br.align()
    return result, br.byte_pos - offset

def decode_cxform_alpha(data, offset):
    """Decode CXFORMWITHALPHA. Returns (dict, bytes_consumed)."""
    br = BitReader(data, offset)
    result = {}
    
    has_add = br.read_bits(1)
    has_mult = br.read_bits(1)
    nbits = br.read_bits(4)
    
    if has_mult:
        result['multR'] = br.read_sbits(nbits)
        result['multG'] = br.read_sbits(nbits)
        result['multB'] = br.read_sbits(nbits)
        result['multA'] = br.read_sbits(nbits)
    if has_add:
        result['addR'] = br.read_sbits(nbits)
        result['addG'] = br.read_sbits(nbits)
        result['addB'] = br.read_sbits(nbits)
        result['addA'] = br.read_sbits(nbits)
    
    br.align()
    return result, br.byte_pos - offset

def decode_place_object2(tag_data):
    """Fully decode a PlaceObject2 (tag 26) tag."""
    flags = tag_data[0]
    depth = struct.unpack_from('<H', tag_data, 1)[0]
    off = 3
    
    result = {
        'flags': flags,
        'depth': depth,
        'hasMove': bool(flags & 0x01),
        'hasCharacter': bool(flags & 0x02),
        'hasMatrix': bool(flags & 0x04),
        'hasColorTransform': bool(flags & 0x08),
        'hasRatio': bool(flags & 0x10),
        'hasName': bool(flags & 0x20),
        'hasClipDepth': bool(flags & 0x40),
        'hasClipActions': bool(flags & 0x80),
    }
    
    if flags & 0x02:  # HasCharacter
        result['characterId'] = struct.unpack_from('<H', tag_data, off)[0]
        off += 2
    
    if flags & 0x04:  # HasMatrix
        mtx, consumed = decode_matrix(tag_data, off)
        result['matrix'] = mtx
        off += consumed
    
    if flags & 0x08:  # HasColorTransform
        cx, consumed = decode_cxform_alpha(tag_data, off)
        result['colorTransform'] = cx
        off += consumed
    
    if flags & 0x10:  # HasRatio
        result['ratio'] = struct.unpack_from('<H', tag_data, off)[0]
        off += 2
    
    if flags & 0x20:  # HasName
        end = tag_data.index(0, off)
        result['name'] = tag_data[off:end].decode('utf-8', errors='replace')
        off = end + 1
    
    if flags & 0x40:  # HasClipDepth
        result['clipDepth'] = struct.unpack_from('<H', tag_data, off)[0]
        off += 2
    
    return result

def decode_place_object3(tag_data):
    """Fully decode a PlaceObject3 (tag 70) tag."""
    flags2 = tag_data[0]
    flags = tag_data[1]
    depth = struct.unpack_from('<H', tag_data, 2)[0]
    off = 4
    
    result = {
        'flags': flags,
        'flags2': flags2,
        'depth': depth,
        'hasMove': bool(flags & 0x01),
        'hasCharacter': bool(flags & 0x02),
        'hasMatrix': bool(flags & 0x04),
        'hasColorTransform': bool(flags & 0x08),
        'hasRatio': bool(flags & 0x10),
        'hasName': bool(flags & 0x20),
        'hasClipDepth': bool(flags & 0x40),
        'hasClipActions': bool(flags & 0x80),
        # flags2
        'hasFilterList': bool(flags2 & 0x01),
        'hasBlendMode': bool(flags2 & 0x02),
        'hasBitmapCache': bool(flags2 & 0x04),
        'hasVisible': bool(flags2 & 0x08),
    }
    
    if flags & 0x02:
        result['characterId'] = struct.unpack_from('<H', tag_data, off)[0]
        off += 2
    if flags & 0x04:
        mtx, consumed = decode_matrix(tag_data, off)
        result['matrix'] = mtx
        off += consumed
    if flags & 0x08:
        cx, consumed = decode_cxform_alpha(tag_data, off)
        result['colorTransform'] = cx
        off += consumed
    if flags & 0x10:
        result['ratio'] = struct.unpack_from('<H', tag_data, off)[0]
        off += 2
    if flags & 0x20:
        end = tag_data.index(0, off)
        result['name'] = tag_data[off:end].decode('utf-8', errors='replace')
        off = end + 1
    if flags & 0x40:
        result['clipDepth'] = struct.unpack_from('<H', tag_data, off)[0]
        off += 2
    # flags2 extensions
    if flags2 & 0x01:  # HasFilterList
        result['filterList'] = '(present)'
        # Skip filter parsing for now
    if flags2 & 0x02:  # HasBlendMode
        result['blendMode'] = tag_data[off] if off < len(tag_data) else None
        off += 1
    
    return result

def find_sprite(tags, target_cid):
    for t, d in tags:
        if t == 39 and len(d) >= 4:
            cid = struct.unpack_from('<H', d)[0]
            if cid == target_cid:
                return d
    return None

def find_cid_for_symbol(tags, symbol_name):
    for t, d in tags:
        if t == 76:
            count = struct.unpack_from('<H', d)[0]
            off = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', d, off)[0]; off += 2
                end = d.index(0, off)
                name = d[off:end].decode('utf-8', errors='replace')
                off = end + 1
                if name == symbol_name:
                    return cid
    return None

def main():
    og_data = read_swf(OG)
    rt_data = read_swf(RT)
    
    og_tags = parse_tags(og_data, skip_header(og_data))
    rt_tags = parse_tags(rt_data, skip_header(rt_data))
    
    og_cid = find_cid_for_symbol(og_tags, 'smashville_bg')
    rt_cid = find_cid_for_symbol(rt_tags, 'smashville_bg')
    
    og_sprite = find_sprite(og_tags, og_cid)
    rt_sprite = find_sprite(rt_tags, rt_cid)
    
    if not og_sprite or not rt_sprite:
        print("ERROR: sprite not found"); return
    
    og_inner = parse_tags(og_sprite, 4)
    rt_inner = parse_tags(rt_sprite, 4)
    
    print(f"OG smashville_bg: {len(og_inner)} tags")
    print(f"RT smashville_bg: {len(rt_inner)} tags")
    
    # Compare tag by tag
    TAG_NAMES = {0:'End', 1:'ShowFrame', 26:'PlaceObject2', 28:'RemoveObject2', 43:'FrameLabel', 45:'SoundStreamHead2', 70:'PlaceObject3'}
    
    max_tags = max(len(og_inner), len(rt_inner))
    og_frame = 1; rt_frame = 1
    
    print(f"\n{'='*100}")
    print(f"TAG-BY-TAG COMPARISON")
    print(f"{'='*100}")
    
    for i in range(max_tags):
        og_t = og_inner[i] if i < len(og_inner) else None
        rt_t = rt_inner[i] if i < len(rt_inner) else None
        
        if og_t is None or rt_t is None:
            print(f"\n[{i}] MISMATCH: OG={'None' if og_t is None else TAG_NAMES.get(og_t[0], f'Tag{og_t[0]}')} RT={'None' if rt_t is None else TAG_NAMES.get(rt_t[0], f'Tag{rt_t[0]}')}")
            continue
        
        og_tt, og_td = og_t
        rt_tt, rt_td = rt_t
        
        # Track frames
        if og_tt == 1: og_frame += 1
        if rt_tt == 1: rt_frame += 1
        
        same = (og_tt == rt_tt and og_td == rt_td)
        if same:
            continue  # Skip identical tags
        
        og_name = TAG_NAMES.get(og_tt, f'Tag{og_tt}')
        rt_name = TAG_NAMES.get(rt_tt, f'Tag{rt_tt}')
        
        print(f"\n[{i}] Frame OG={og_frame} RT={rt_frame}: {og_name}({len(og_td)}b) vs {rt_name}({len(rt_td)}b)")
        
        if og_tt == rt_tt and og_tt in (26, 70):
            # Decode PlaceObject
            if og_tt == 26:
                og_po = decode_place_object2(og_td)
                rt_po = decode_place_object2(rt_td)
            else:
                og_po = decode_place_object3(og_td)
                rt_po = decode_place_object3(rt_td)
            
            # Print differences
            all_keys = set(list(og_po.keys()) + list(rt_po.keys()))
            for k in sorted(all_keys):
                og_v = og_po.get(k, '(absent)')
                rt_v = rt_po.get(k, '(absent)')
                marker = '  ' if og_v == rt_v else '≠ '
                if og_v != rt_v:
                    print(f"  {marker}{k}: OG={og_v} RT={rt_v}")
        elif og_tt != rt_tt:
            print(f"  TYPE MISMATCH: OG={og_name} RT={rt_name}")
        else:
            print(f"  OG hex: {og_td.hex()}")
            print(f"  RT hex: {rt_td.hex()}")
        
        # Also show raw hex for PlaceObject differences
        if og_tt == rt_tt and og_tt in (26, 70) and og_td != rt_td:
            print(f"  OG raw: {og_td.hex()}")
            print(f"  RT raw: {rt_td.hex()}")

    # Also check the foreground sprite (svforegroundmc_45) for child instance names
    print(f"\n{'='*100}")
    print("FOREGROUND SPRITE INSTANCE NAMES CHECK")
    print(f"{'='*100}")
    
    # Find svforegroundmc_45
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        fg_cid = find_cid_for_symbol(tags, 'svforegroundmc_45')
        if fg_cid is None:
            print(f"{label}: svforegroundmc_45 NOT FOUND in SymbolClass")
            continue
        fg_sprite = find_sprite(tags, fg_cid)
        if not fg_sprite:
            print(f"{label}: svforegroundmc_45 sprite data NOT FOUND (cid={fg_cid})")
            continue
        fg_inner = parse_tags(fg_sprite, 4)
        frame = 1
        print(f"\n{label} svforegroundmc_45 (cid={fg_cid}):")
        for tt, td in fg_inner:
            if tt == 1: frame += 1
            elif tt == 43:
                lbl = td[:td.index(0)].decode() if 0 in td else td.decode()
                print(f"  Frame {frame}: FrameLabel='{lbl}'")
            elif tt in (26, 70):
                po = decode_place_object2(td) if tt == 26 else decode_place_object3(td)
                if po.get('hasName'):
                    print(f"  Frame {frame}: PO depth={po['depth']} char={po.get('characterId','?')} name='{po.get('name','?')}'")

    # Also check SmashvilleLighting_47 (the lighting sprite)
    print(f"\n{'='*100}")
    print("LIGHTING SPRITE INSTANCE NAMES CHECK")
    print(f"{'='*100}")
    
    for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
        lt_cid = find_cid_for_symbol(tags, 'SmashvilleLighting_47')
        if lt_cid is None:
            print(f"{label}: SmashvilleLighting_47 NOT FOUND")
            continue
        lt_sprite = find_sprite(tags, lt_cid)
        if not lt_sprite:
            print(f"{label}: SmashvilleLighting_47 sprite NOT FOUND (cid={lt_cid})")
            continue
        lt_inner = parse_tags(lt_sprite, 4)
        frame = 1
        print(f"\n{label} SmashvilleLighting_47 (cid={lt_cid}):")
        for tt, td in lt_inner:
            if tt == 1: frame += 1
            elif tt == 43:
                lbl = td[:td.index(0)].decode() if 0 in td else td.decode()
                print(f"  Frame {frame}: FrameLabel='{lbl}'")
            elif tt in (26, 70):
                po = decode_place_object2(td) if tt == 26 else decode_place_object3(td)
                if po.get('hasName'):
                    charinfo = f"char={po.get('characterId','?')}" if po.get('hasCharacter') else ""
                    print(f"  Frame {frame}: PO depth={po['depth']} {charinfo} name='{po.get('name','?')}'")

if __name__ == '__main__':
    main()
