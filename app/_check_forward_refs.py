"""Check for bitmap forward references — sprites placing bitmap characters
that haven't been defined yet in the tag stream."""
import struct, zlib, sys, os

RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"
OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"

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

def check_forward_refs(tags, label):
    defined = set()
    bitmap_defined = set()
    forward_refs = []
    
    for tag_idx, (t, d) in enumerate(tags):
        if t in (2, 4, 11, 14, 20, 22, 24, 32, 35, 36, 37, 39, 46, 75, 83, 84, 87):
            if len(d) >= 2:
                cid = struct.unpack_from('<H', d, 0)[0]
                defined.add(cid)
                if t in (20, 35, 36):
                    bitmap_defined.add(cid)
        
        if t == 39 and len(d) >= 4:
            sprite_cid = struct.unpack_from('<H', d, 0)[0]
            inner = parse_tags(d, 4)
            for it, id_ in inner:
                if it == 70 and len(id_) >= 6:
                    flags1 = id_[0]
                    flags2 = id_[1]
                    has_char = flags1 & 0x02
                    has_image = flags2 & 0x10
                    
                    if has_char and has_image:
                        off = 4
                        if flags2 & 0x08:
                            end = id_.index(0, off)
                            off = end + 1
                        placed_cid = struct.unpack_from('<H', id_, off)[0]
                        if placed_cid not in defined:
                            forward_refs.append((sprite_cid, placed_cid, tag_idx))
                
                # Also check PO2 placements referencing bitmap chars  
                elif it == 26 and len(id_) >= 5:
                    flags = id_[0]
                    has_char = flags & 0x02
                    if has_char:
                        placed_cid = struct.unpack_from('<H', id_, 3)[0]
                        if placed_cid not in defined and placed_cid in bitmap_defined:
                            forward_refs.append((sprite_cid, placed_cid, tag_idx))
    
    print(f"\n{label}: {len(defined)} definitions, {len(bitmap_defined)} bitmap defs")
    print(f"{label}: {len(forward_refs)} forward references (placing undefined chars)")
    if forward_refs:
        by_char = {}
        for sprite_cid, placed_cid, idx in forward_refs:
            if placed_cid not in by_char:
                by_char[placed_cid] = []
            by_char[placed_cid].append(sprite_cid)
        print(f"  Unique undefined chars: {len(by_char)}")
        for placed_cid, sprites in sorted(by_char.items())[:30]:
            is_bmp = placed_cid in bitmap_defined
            print(f"  char {placed_cid} (bitmap_later={is_bmp}): in {len(sprites)} sprites, e.g. {sprites[:3]}")

def main():
    og_data = read_swf(OG)
    rt_data = read_swf(RT)
    og_tags = parse_tags(og_data, skip_header(og_data))
    rt_tags = parse_tags(rt_data, skip_header(rt_data))
    
    check_forward_refs(og_tags, "OG")
    check_forward_refs(rt_tags, "RT")

if __name__ == '__main__':
    main()
