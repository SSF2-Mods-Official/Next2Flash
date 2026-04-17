"""Check what CID 355 (OG) and CID 1759 (RT) are - collision box shapes"""
import struct, zlib

def parse_swf(path):
    with open(path, 'rb') as f:
        sig = f.read(3)
        ver = struct.unpack('<B', f.read(1))[0]
        length = struct.unpack_from('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS': rest = zlib.decompress(rest)
    data = rest
    nbits = (data[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    data = data[rect_bytes:]
    data = data[4:]
    return data

def iter_tags(data):
    pos = 0
    while pos < len(data):
        if pos + 2 > len(data): break
        h = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        tt = h >> 6
        length = h & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        td = data[pos:pos+length]
        yield tt, td
        pos += length
        if tt == 0: break

TAG_NAMES = {
    2: 'DefineShape', 22: 'DefineShape2', 32: 'DefineShape3', 83: 'DefineShape4',
    46: 'DefineMorphShape', 91: 'DefineMorphShape2',
    39: 'DefineSprite', 20: 'DefineBitsLossless', 36: 'DefineBitsLossless2',
    21: 'DefineBitsJPEG2', 6: 'DefineBits',
}

for label, path, check_cids in [
    ('OG', r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf", [355, 364]),
    ('RT', "fox_fresh.swf", [1759, 1756]),
]:
    print(f"\n=== {label} ===")
    data = parse_swf(path)
    for tt, td in iter_tags(data):
        if tt in TAG_NAMES:
            cid = struct.unpack_from('<H', td, 0)[0]
            if cid in check_cids:
                tname = TAG_NAMES[tt]
                print(f"  CID {cid}: {tname} (tag type {tt}), data length={len(td)}")
                if tt == 39:  # DefineSprite
                    fc = struct.unpack_from('<H', td, 2)[0]
                    print(f"    DefineSprite: {fc} frames")
                    # Dump inner tags briefly
                    inner = td[4:]
                    frame = 0
                    for itt, itd in iter_tags(inner):
                        itname = TAG_NAMES.get(itt, f'Tag{itt}')
                        if itt == 1:
                            frame += 1
                        elif itt in (26, 70):
                            flags = itd[0] if itt == 26 else struct.unpack_from('<H', itd, 0)[0]
                            off = 1 if itt == 26 else 2
                            depth = struct.unpack_from('<H', itd, off)[0]
                            print(f"    F{frame} PlaceObj depth={depth} flags=0x{flags:02x}")
                        else:
                            print(f"    F{frame} {itname}({itt}) len={len(itd)}")
