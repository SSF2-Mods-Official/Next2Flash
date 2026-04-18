"""Compare structural tags between OG and RT SWF."""
import struct

og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
rt_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'

TAG_NAMES = {
    0: 'End', 1: 'ShowFrame', 2: 'DefineShape', 4: 'PlaceObject',
    5: 'RemoveObject', 6: 'DefineBits', 7: 'DefineButton', 8: 'JPEGTables',
    9: 'SetBackgroundColor', 10: 'DefineFont', 11: 'DefineText',
    12: 'DoAction', 14: 'DefineSound', 15: 'StartSound', 18: 'SoundStreamHead',
    19: 'SoundStreamBlock', 20: 'DefineBitsLossless', 21: 'DefineBitsJPEG2',
    22: 'DefineShape2', 24: 'Protect', 26: 'PlaceObject2', 28: 'RemoveObject2',
    32: 'DefineShape3', 33: 'DefineText2', 34: 'DefineButton2',
    35: 'DefineBitsJPEG3', 36: 'DefineBitsLossless2', 37: 'DefineEditText',
    39: 'DefineSprite', 43: 'FrameLabel', 45: 'SoundStreamHead2',
    46: 'DefineMorphShape', 48: 'DefineFont2', 56: 'ExportAssets',
    57: 'ImportAssets', 58: 'EnableDebugger', 59: 'DoInitAction',
    60: 'DefineVideoStream', 63: 'DebugID', 64: 'EnableDebugger2',
    65: 'ScriptLimits', 66: 'SetTabIndex', 69: 'FileAttributes',
    70: 'PlaceObject3', 71: 'ImportAssets2', 73: 'DefineFontAlignZones',
    74: 'CSMTextSettings', 75: 'DefineFont3', 76: 'SymbolClass',
    77: 'Metadata', 78: 'DefineScalingGrid', 82: 'DoABC',
    83: 'DefineShape4', 84: 'DefineMorphShape2', 86: 'DefineSceneAndFrameLabelData',
    87: 'DefineBinaryData', 88: 'DefineFontName', 91: 'DefineFont4',
    93: 'EnableTelemetry'
}

def parse_swf_header_and_tags(path):
    with open(path, 'rb') as f:
        raw = f.read()
    
    sig = raw[:3].decode('ascii')
    ver = raw[3]
    file_len = struct.unpack_from('<I', raw, 4)[0]
    
    pos = 8
    nbits = (raw[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    
    # Parse RECT bounds
    import io
    from collections import OrderedDict
    
    rect_start = pos
    bits_data = int.from_bytes(raw[pos:pos+rect_bytes+4], 'big')
    bit_offset = 5  # skip Nbits
    total_available_bits = (rect_bytes + 4) * 8
    
    def read_bits(n):
        nonlocal bit_offset
        shift = total_available_bits - bit_offset - n
        val = (bits_data >> shift) & ((1 << n) - 1)
        if val & (1 << (n-1)):  # sign extend
            val -= (1 << n)
        bit_offset += n
        return val
    
    xmin = read_bits(nbits)
    xmax = read_bits(nbits)
    ymin = read_bits(nbits)
    ymax = read_bits(nbits)
    
    pos += rect_bytes
    frame_rate_raw = struct.unpack_from('<H', raw, pos)[0]
    frame_rate = frame_rate_raw >> 8  # integer part
    pos += 2
    frame_count = struct.unpack_from('<H', raw, pos)[0]
    pos += 2
    
    header = {
        'sig': sig, 'ver': ver, 'file_len': file_len,
        'rect': f'({xmin},{ymin})-({xmax},{ymax})',
        'frame_rate': frame_rate, 'frame_count': frame_count
    }
    
    tags = []
    while pos < len(raw):
        if pos + 2 > len(raw):
            break
        tag_code_and_length = struct.unpack_from('<H', raw, pos)[0]
        tag_type = tag_code_and_length >> 6
        tag_length = tag_code_and_length & 0x3F
        pos += 2
        if tag_length == 0x3F:
            tag_length = struct.unpack_from('<I', raw, pos)[0]
            pos += 4
        tag_start = pos
        
        tag_data = raw[tag_start:tag_start + tag_length]
        tags.append((tag_type, tag_length, tag_data))
        
        if tag_type == 0:
            break
        pos = tag_start + tag_length
    
    return header, tags

og_header, og_tags = parse_swf_header_and_tags(og_path)
rt_header, rt_tags = parse_swf_header_and_tags(rt_path)

print("=== HEADER COMPARISON ===")
for key in og_header:
    og_val = og_header[key]
    rt_val = rt_header[key]
    match = "OK" if og_val == rt_val else "DIFF!"
    print(f"  {key}: OG={og_val} RT={rt_val} [{match}]")

# Compare tag type distribution
from collections import Counter
og_type_counts = Counter(t[0] for t in og_tags)
rt_type_counts = Counter(t[0] for t in rt_tags)

print("\n=== TAG TYPE DISTRIBUTION ===")
all_types = sorted(set(og_type_counts.keys()) | set(rt_type_counts.keys()))
for tt in all_types:
    name = TAG_NAMES.get(tt, f'Unknown({tt})')
    og_c = og_type_counts.get(tt, 0)
    rt_c = rt_type_counts.get(tt, 0)
    match = "OK" if og_c == rt_c else "DIFF!"
    if og_c != rt_c or tt not in (36, 32, 39, 70, 28, 1, 0):
        print(f"  Tag {tt:3d} ({name:30s}): OG={og_c:5d} RT={rt_c:5d} [{match}]")

print("\n=== SPECIAL TAGS COMPARISON ===")

# FileAttributes (tag 69)
for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
    for tt, tl, td in tags:
        if tt == 69:  # FileAttributes
            if tl >= 4:
                flags = struct.unpack_from('<I', td, 0)[0]
                print(f"  {label} FileAttributes: flags=0x{flags:08X}")
                print(f"    UseDirectBlit: {bool(flags & 0x40)}")
                print(f"    UseGPU: {bool(flags & 0x20)}")
                print(f"    HasMetadata: {bool(flags & 0x10)}")
                print(f"    ActionScript3: {bool(flags & 0x08)}")
                print(f"    UseNetwork: {bool(flags & 0x01)}")
            break

# SetBackgroundColor (tag 9)
for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
    for tt, tl, td in tags:
        if tt == 9:
            if tl >= 3:
                r, g, b = td[0], td[1], td[2]
                print(f"  {label} SetBackgroundColor: #{r:02X}{g:02X}{b:02X}")
            break

# ScriptLimits (tag 65)
for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
    found = False
    for tt, tl, td in tags:
        if tt == 65:
            if tl >= 4:
                max_recursion = struct.unpack_from('<H', td, 0)[0]
                timeout = struct.unpack_from('<H', td, 2)[0]
                print(f"  {label} ScriptLimits: maxRecursion={max_recursion} timeout={timeout}")
            found = True
            break
    if not found:
        print(f"  {label} ScriptLimits: NOT PRESENT")

# DoABC (tag 82)
for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
    for tt, tl, td in tags:
        if tt == 82:
            # flags(4) + name(null-terminated) + abc
            flags = struct.unpack_from('<I', td, 0)[0]
            name_end = td.index(0, 4)
            name = td[4:name_end].decode('utf-8', errors='replace')
            abc_len = tl - name_end - 1
            print(f"  {label} DoABC: flags={flags} name='{name}' abc_size={abc_len}")
            break

# SymbolClass (tag 76)
for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
    for tt, tl, td in tags:
        if tt == 76:
            count = struct.unpack_from('<H', td, 0)[0]
            print(f"  {label} SymbolClass: {count} entries")
            pos = 2
            for i in range(min(count, 5)):
                cid = struct.unpack_from('<H', td, pos)[0]
                pos += 2
                name_end = td.index(0, pos)
                name = td[pos:name_end].decode('utf-8', errors='replace')
                pos = name_end + 1
                print(f"    [{i}] charID={cid} -> '{name}'")
            if count > 5:
                print(f"    ... and {count - 5} more")
            break

# ExportAssets (tag 56)
for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
    found = False
    for tt, tl, td in tags:
        if tt == 56:
            count = struct.unpack_from('<H', td, 0)[0]
            print(f"  {label} ExportAssets: {count} entries")
            found = True
            break
    if not found:
        print(f"  {label} ExportAssets: NOT PRESENT")

# Product info / Metadata
for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
    for tt, tl, td in tags:
        if tt == 77:  # Metadata
            print(f"  {label} Metadata: {tl} bytes")
            break

# DefineSceneAndFrameLabelData (tag 86)
for label, tags in [("OG", og_tags), ("RT", rt_tags)]:
    found = False
    for tt, tl, td in tags:
        if tt == 86:
            print(f"  {label} DefineSceneAndFrameLabelData: {tl} bytes")
            found = True
            break
    if not found:
        print(f"  {label} DefineSceneAndFrameLabelData: NOT PRESENT")
