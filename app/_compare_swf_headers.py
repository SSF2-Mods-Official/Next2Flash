"""Compare SWF headers and tag-level structure between OG and RT."""
import struct, zlib

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
RT = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\fox_fresh.swf"

def read_bits(data, bit_offset, count):
    val = 0
    for i in range(count):
        byte_idx = (bit_offset + i) // 8
        bit_idx = 7 - ((bit_offset + i) % 8)
        if byte_idx < len(data):
            val = (val << 1) | ((data[byte_idx] >> bit_idx) & 1)
    return val

def read_sbits(data, bit_offset, count):
    val = read_bits(data, bit_offset, count)
    if val >= (1 << (count - 1)):
        val -= (1 << count)
    return val

def parse_swf_header(path):
    with open(path, 'rb') as f:
        raw = f.read()
    sig = raw[:3].decode('ascii')
    ver = raw[3]
    file_length = struct.unpack_from('<I', raw, 4)[0]
    
    if sig == 'CWS':
        rest = zlib.decompress(raw[8:])
    elif sig == 'ZWS':
        import lzma
        rest = lzma.decompress(raw[8:])
    elif sig == 'FWS':
        rest = raw[8:]
    else:
        raise ValueError(f"Unknown sig: {sig}")
    
    # Parse RECT
    nbits = (rest[0] >> 3) & 0x1F
    bit_off = 5
    xmin = read_sbits(rest, bit_off, nbits); bit_off += nbits
    xmax = read_sbits(rest, bit_off, nbits); bit_off += nbits
    ymin = read_sbits(rest, bit_off, nbits); bit_off += nbits
    ymax = read_sbits(rest, bit_off, nbits); bit_off += nbits
    rect_bytes = (bit_off + 7) // 8
    
    # Frame rate and frame count
    fr_fixed = struct.unpack_from('<H', rest, rect_bytes)[0]
    frame_rate = fr_fixed / 256.0  # 8.8 fixed point
    frame_count = struct.unpack_from('<H', rest, rect_bytes + 2)[0]
    
    data_start = rect_bytes + 4
    
    return {
        'sig': sig,
        'version': ver,
        'file_length': file_length,
        'actual_file_size': len(raw),
        'decompressed_size': len(rest) + 8,
        'rect': {'xmin': xmin/20.0, 'xmax': xmax/20.0, 'ymin': ymin/20.0, 'ymax': ymax/20.0},
        'rect_nbits': nbits,
        'frame_rate': frame_rate,
        'frame_rate_raw': fr_fixed,
        'frame_count': frame_count,
        'data': rest[data_start:],
    }

def iter_tags(data):
    pos = 0
    while pos < len(data):
        if pos + 2 > len(data):
            break
        h = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        tt = h >> 6
        length = h & 0x3F
        if length == 0x3F:
            if pos + 4 > len(data):
                break
            length = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        td = data[pos:pos+length]
        yield tt, td
        pos += length
        if tt == 0:
            break

TAG_NAMES = {
    0: 'End', 1: 'ShowFrame', 2: 'DefineShape', 4: 'PlaceObject',
    5: 'RemoveObject', 6: 'DefineBits', 8: 'JPEGTables', 9: 'SetBackgroundColor',
    11: 'DefineText', 12: 'DoAction', 13: 'DefineFontInfo', 14: 'DefineSound',
    20: 'DefineBitsLossless', 21: 'DefineBitsJPEG2', 22: 'DefineShape2',
    24: 'Protect', 26: 'PlaceObject2', 28: 'RemoveObject2',
    32: 'DefineShape3', 35: 'DefineBitsJPEG3', 36: 'DefineBitsLossless2',
    37: 'DefineEditText', 39: 'DefineSprite', 43: 'FrameLabel',
    45: 'SoundStreamHead2', 46: 'DefineMorphShape',
    48: 'DefineFont2', 56: 'ExportAssets', 65: 'ScriptLimits',
    69: 'FileAttributes', 70: 'PlaceObject3', 73: 'DefineFontAlignZones',
    75: 'DefineFont3', 76: 'SymbolClass', 77: 'Metadata',
    78: 'DefineScalingGrid', 82: 'DoABC2', 83: 'DefineShape4',
    86: 'DefineSceneAndFrameData', 87: 'DefineBinaryData',
    91: 'DefineMorphShape2',
}

for label, path in [("OG", OG), ("RT", RT)]:
    info = parse_swf_header(path)
    print(f"\n{'='*60}")
    print(f"  {label}: {path}")
    print(f"{'='*60}")
    print(f"  Signature:    {info['sig']}")
    print(f"  SWF Version:  {info['version']}")
    print(f"  File Length:  {info['file_length']} (actual: {info['actual_file_size']})")
    print(f"  Rect:         {info['rect']} (nbits={info['rect_nbits']})")
    print(f"  Frame Rate:   {info['frame_rate']} (raw=0x{info['frame_rate_raw']:04X})")
    print(f"  Frame Count:  {info['frame_count']}")
    
    # Count all tag types
    tag_counts = {}
    total_tags = 0
    for tt, td in iter_tags(info['data']):
        tname = TAG_NAMES.get(tt, f'Unknown_{tt}')
        tag_counts[tname] = tag_counts.get(tname, 0) + 1
        total_tags += 1
    
    print(f"\n  Total tags: {total_tags}")
    print(f"  Tag breakdown:")
    for tname in sorted(tag_counts.keys()):
        print(f"    {tname:30s}: {tag_counts[tname]}")
    
    # Check FileAttributes
    for tt, td in iter_tags(info['data']):
        if tt == 69:  # FileAttributes
            flags = struct.unpack_from('<I', td, 0)[0]
            print(f"\n  FileAttributes flags: 0x{flags:08X}")
            print(f"    HasMetadata:    {bool(flags & 0x10)}")
            print(f"    ActionScript3:  {bool(flags & 0x08)}")
            print(f"    UseNetwork:     {bool(flags & 0x01)}")
            print(f"    UseDirectBlit:  {bool(flags & 0x40)}")
            print(f"    UseGPU:         {bool(flags & 0x20)}")
        if tt == 65:  # ScriptLimits
            max_recursion = struct.unpack_from('<H', td, 0)[0]
            timeout = struct.unpack_from('<H', td, 2)[0]
            print(f"\n  ScriptLimits: max_recursion={max_recursion}, timeout={timeout}s")
        if tt == 9:  # SetBackgroundColor
            r, g, b = td[0], td[1], td[2]
            print(f"\n  Background: RGB({r},{g},{b})")
        if tt == 86:  # DefineSceneAndFrameData
            print(f"\n  DefineSceneAndFrameData: {len(td)} bytes")
