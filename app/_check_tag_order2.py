"""Check tag ordering: position of DoABC, SymbolClass, and LL2 for charID=1001 in RT vs OG."""
import struct, zlib

RT = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
OG = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'

TAG_NAMES = {
    82: 'DoABC', 76: 'SymbolClass', 36: 'DefineBitsLossless2', 35: 'DefineBitsJPEG3',
    21: 'DefineBitsJPEG2', 8: 'DefineJPEGTables', 39: 'DefineSprite',
    32: 'DefineShape3', 83: 'DefineShape4', 2: 'DefineShape',
    65: 'ScriptLimits', 69: 'FileAttributes', 9: 'SetBackgroundColor',
    77: 'Metadata', 1: 'ShowFrame',
}

def analyze_order(path, label):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:3] == b'CWS':
        raw = raw[:8] + zlib.decompress(raw[8:])
    pos = 8
    nb = (raw[pos] >> 3) & 0x1f
    pos += (5 + nb * 4 + 7) // 8 + 4

    events = []
    tag_index = 0
    while pos < len(raw) - 1:
        hdr = struct.unpack_from('<H', raw, pos)[0]
        tt = hdr >> 6
        sl = hdr & 0x3f
        tag_pos = pos
        pos += 2
        if sl == 0x3f:
            l = struct.unpack_from('<I', raw, pos)[0]; pos += 4
        else:
            l = sl
        pay = raw[pos:pos+l]
        if tt == 0:
            break

        tag_name = TAG_NAMES.get(tt, f'Tag{tt}')

        # Record key events
        if tt == 82:  # DoABC
            events.append(f"  #{tag_index:4d} byte={tag_pos:8d} DoABC (len={l})")
        elif tt == 76:  # SymbolClass
            events.append(f"  #{tag_index:4d} byte={tag_pos:8d} SymbolClass (len={l}, {struct.unpack_from('<H', pay)[0] if l >= 2 else '?'} entries)")
        elif tt == 36 and l >= 2:  # LL2
            cid = struct.unpack_from('<H', pay)[0]
            if cid in (1001, 1002, 1003, 1004):
                w = struct.unpack_from('<H', pay, 3)[0] if l >= 5 else '?'
                h = struct.unpack_from('<H', pay, 5)[0] if l >= 7 else '?'
                events.append(f"  #{tag_index:4d} byte={tag_pos:8d} LL2 charID={cid} {w}x{h}")
        elif tt == 39 and l >= 4:
            sid = struct.unpack_from('<H', pay)[0]
            fc = struct.unpack_from('<H', pay, 2)[0]
            if sid == 1471:
                events.append(f"  #{tag_index:4d} byte={tag_pos:8d} DefineSprite charID=1471 (DAir_73) frameCount={fc}")
        elif tt == 8:
            events.append(f"  #{tag_index:4d} byte={tag_pos:8d} DefineJPEGTables (len={l})")

        tag_index += 1
        pos += l

    print(f"\n=== {label}: Key tag ordering ===")
    for e in events:
        print(e)

analyze_order(RT, "RT")
analyze_order(OG, "OG")
