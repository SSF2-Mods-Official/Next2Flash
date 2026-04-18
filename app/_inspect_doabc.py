"""
Parse the DoABC from the OG SWF and find the bm_dairHand class constructor.
Extract what width/height values it calls super() with.
"""
import struct, zlib

def read_swf_tags(path):
    with open(path, 'rb') as f:
        data = f.read()
    sig = data[:3]
    if sig == b'CWS':
        body = zlib.decompress(data[8:])
        data = data[:8] + body
    off = 8
    nbits = (data[off] >> 3) & 0x1f
    total_bits = 5 + nbits * 4
    off += (total_bits + 7) // 8
    off += 4
    tags = []
    while off < len(data):
        if off + 2 > len(data): break
        tw = struct.unpack_from('<H', data, off)[0]
        tag_type = tw >> 6
        tag_len = tw & 0x3f
        off += 2
        if tag_len == 63:
            tag_len = struct.unpack_from('<i', data, off)[0]
            off += 4
        tags.append((tag_type, off, tag_len))
        off += tag_len
    return tags, data

def read_u30(data, off):
    result = 0
    shift = 0
    while True:
        b = data[off]
        off += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return result, off

og_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
og_tags, og_data = read_swf_tags(og_path)

# Find DoABC tag
for (t, o, l) in og_tags:
    if t == 82:
        abc_data = og_data[o:o+l]
        break

print(f'DoABC length: {len(abc_data)}')

# ABC format: flags(4) + name(string z-terminated) + actual_abc_bytecode
# Actually DoABC tag body: flags(4) + name + abc_data
# Skip flags (4 bytes) + null-terminated name
abc_off = 4
while abc_off < len(abc_data) and abc_data[abc_off] != 0:
    abc_off += 1
abc_off += 1  # skip null terminator
abc_body = abc_data[abc_off:]
print(f'ABC body offset: {abc_off}, body length: {len(abc_body)}')

# Parse ABC minor_version + major_version
minor, major = struct.unpack_from('<HH', abc_body)
print(f'ABC version: {major}.{minor}')
abc_off = 4

# Parse constant pool
def parse_constant_pool(data, off):
    # int_count
    int_count, off = read_u30(data, off)
    ints = [0]  # index 0 = 0
    for _ in range(int_count - 1):
        v, off = read_u30(data, off)
        # Actually int is read as u32 (variable length signed)
        ints.append(v)
    
    # uint_count
    uint_count, off = read_u30(data, off)
    uints = [0]
    for _ in range(uint_count - 1):
        v, off = read_u30(data, off)
        uints.append(v)
    
    # double_count
    double_count, off = read_u30(data, off)
    doubles = [float('nan')]
    for _ in range(double_count - 1):
        v = struct.unpack_from('<d', data, off)[0]
        doubles.append(v)
        off += 8
    
    # string_count
    string_count, off = read_u30(data, off)
    strings = ['']  # index 0 = empty string
    for _ in range(string_count - 1):
        slen, off = read_u30(data, off)
        s = data[off:off+slen].decode('utf-8', errors='replace')
        strings.append(s)
        off += slen
    
    # namespace_count
    ns_count, off = read_u30(data, off)
    namespaces = [None]
    for _ in range(ns_count - 1):
        kind = data[off]; off += 1
        name_idx, off = read_u30(data, off)
        namespaces.append((kind, name_idx))
    
    # ns_set_count
    nsset_count, off = read_u30(data, off)
    ns_sets = [None]
    for _ in range(nsset_count - 1):
        cnt, off = read_u30(data, off)
        s = []
        for _ in range(cnt):
            v, off = read_u30(data, off)
            s.append(v)
        ns_sets.append(s)
    
    # multiname_count
    mn_count, off = read_u30(data, off)
    multinames = [None]
    for _ in range(mn_count - 1):
        kind = data[off]; off += 1
        if kind in (0x07, 0x0D):  # QName, QNameA
            ns_idx, off = read_u30(data, off)
            name_idx, off = read_u30(data, off)
            multinames.append(('QName', ns_idx, name_idx))
        elif kind in (0x0F, 0x10):  # RTQName
            multinames.append(('RTQName', kind))
        elif kind in (0x11, 0x12):  # RTQNameL
            multinames.append(('RTQNameL', kind))
        elif kind in (0x09, 0x0E):  # Multiname
            name_idx, off = read_u30(data, off)
            nsset_idx, off = read_u30(data, off)
            multinames.append(('Multiname', name_idx, nsset_idx))
        elif kind in (0x1B, 0x1C):  # MultinameL
            nsset_idx, off = read_u30(data, off)
            multinames.append(('MultinameL', nsset_idx))
        elif kind == 0x1D:  # GenericName 
            type_idx, off = read_u30(data, off)
            param_count, off = read_u30(data, off)
            params = []
            for _ in range(param_count):
                p, off = read_u30(data, off)
                params.append(p)
            multinames.append(('Generic', type_idx, params))
        else:
            multinames.append(('Unknown', kind))
    
    return strings, multinames, off

try:
    strings, multinames, cp_end = parse_constant_pool(abc_body, abc_off)
    print(f'Constant pool parsed. {len(strings)} strings, {len(multinames)} multinames')
    print(f'Constant pool ends at offset: {cp_end}')
    
    # Find bm_dairHand string
    bm_idx = None
    for i, s in enumerate(strings):
        if s == 'bm_dairHand':
            bm_idx = i
            print(f'Found "bm_dairHand" string at index {i}')
    
    # Search for the string in raw bytes too
    raw_idx = abc_body.find(b'bm_dairHand')
    if raw_idx >= 0:
        print(f'"bm_dairHand" raw bytes at abc_body offset {raw_idx}')
        # Show surrounding context
        ctx_start = max(0, raw_idx - 20)
        ctx_end = min(len(abc_body), raw_idx + 30)
        print(f'Context: {abc_body[ctx_start:ctx_end].hex()}')
        
except Exception as e:
    print(f'Error parsing constant pool: {e}')
    import traceback
    traceback.print_exc()

# Simple approach: search for bm_dairHand string in whole DoABC
bm_raw = abc_data.find(b'bm_dairHand')
if bm_raw >= 0:
    print(f'\nbm_dairHand raw position in DoABC (full): {bm_raw}')
    print(f'Surrounding hex: {abc_data[bm_raw-5:bm_raw+20].hex()}')

# Search for "pushbyte 5" patterns in the ABC bytecode (opcode 0x24 = pushbyte)
# bm_dairHand super(5, 5) would have pushbyte 5, pushbyte 5 opcodes nearby
# ABC opcode 0x24 = pushbyte (1 byte immediate follows)
# ABC opcode 0x25 = pushshort (2 byte immediate follows)
print('\n=== Searching for pushbyte 5 patterns in ABC ===')
hits = []
for i in range(len(abc_body) - 4):
    if abc_body[i] == 0x24 and abc_body[i+1] == 5:  # pushbyte 5
        if abc_body[i+2] == 0x24 and abc_body[i+3] == 5:  # pushbyte 5 again
            hits.append(i)
            print(f'  offset {i}: pushbyte(5) pushbyte(5) → bytes {abc_body[i:i+12].hex()}')

print(f'Total pushbyte(5) pushbyte(5) pairs: {len(hits)}')
