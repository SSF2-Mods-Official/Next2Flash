"""Re-roundtrip smashville with the CXFORM fix and verify the day frame gets identity CXFORM."""
import struct, zlib, sys, os, tempfile
sys.path.insert(0, '.')

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\stage\smashville.ssf"
RT_DEST = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\stage\smashville.ssf"

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
            byte_i = self.bit_pos // 8; bit_i = 7 - (self.bit_pos % 8)
            val = (val << 1) | ((self.data[byte_i] >> bit_i) & 1)
            self.bit_pos += 1
        return val
    def read_sbits(self, n):
        val = self.read_bits(n)
        if n > 0 and (val & (1 << (n-1))): val -= (1 << n)
        return val
    def align(self):
        if self.bit_pos % 8: self.bit_pos = (self.bit_pos // 8 + 1) * 8

def decode_matrix(data, offset):
    br = BitReader(data, offset)
    result = {}
    if br.read_bits(1):  # HasScale
        n = br.read_bits(5)
        result['scaleX'] = br.read_sbits(n) / 65536.0
        result['scaleY'] = br.read_sbits(n) / 65536.0
    if br.read_bits(1):  # HasRotate
        n = br.read_bits(5)
        result['rs0'] = br.read_sbits(n) / 65536.0
        result['rs1'] = br.read_sbits(n) / 65536.0
    n = br.read_bits(5)
    if n:
        result['tx'] = br.read_sbits(n)
        result['ty'] = br.read_sbits(n)
    br.align()
    return result, (br.bit_pos + 7) // 8 - offset

def decode_cxform(data, offset):
    br = BitReader(data, offset)
    has_add = br.read_bits(1)
    has_mul = br.read_bits(1)
    nbits = br.read_bits(4)
    result = {}
    if has_mul:
        result['mR'] = br.read_sbits(nbits) / 256.0
        result['mG'] = br.read_sbits(nbits) / 256.0
        result['mB'] = br.read_sbits(nbits) / 256.0
        result['mA'] = br.read_sbits(nbits) / 256.0
    if has_add:
        result['aR'] = br.read_sbits(nbits)
        result['aG'] = br.read_sbits(nbits)
        result['aB'] = br.read_sbits(nbits)
        result['aA'] = br.read_sbits(nbits)
    br.align()
    return result, (br.bit_pos + 7) // 8 - offset, has_add, has_mul

def find_cid(tags, name):
    for t, d in tags:
        if t == 76:
            count = struct.unpack_from('<H', d)[0]; off = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', d, off)[0]; off += 2
                end = d.index(0, off); n = d[off:end].decode(); off = end + 1
                if n == name: return cid
    return None

def check_smashville_bg(swf_data, label):
    tags = parse_tags(swf_data, skip_header(swf_data))
    cid = find_cid(tags, 'smashville_bg')
    if cid is None:
        print(f"{label}: smashville_bg NOT FOUND"); return
    
    for t, d in tags:
        if t == 39 and struct.unpack_from('<H', d)[0] == cid:
            inner = parse_tags(d, 4)
            frame = 1
            for tt, td in inner:
                if tt == 1: frame += 1
                elif tt == 43:
                    lbl = td[:td.index(0)].decode()
                    print(f"\n{label} Frame {frame}: {lbl}")
                elif tt == 26 and struct.unpack_from('<H', td, 1)[0] == 1:  # depth=1 only
                    flags = td[0]; off = 3
                    has_char = bool(flags & 0x02)
                    has_matrix = bool(flags & 0x04)
                    has_ct = bool(flags & 0x08)
                    is_move = bool(flags & 0x01)
                    
                    char_id = None
                    if has_char: char_id = struct.unpack_from('<H', td, off)[0]; off += 2
                    matrix = None
                    if has_matrix: matrix, c = decode_matrix(td, off); off += c
                    cxform = None
                    if has_ct: cxform, c, ha, hm = decode_cxform(td, off); off += c
                    
                    print(f"  {label} depth=1: flags=0x{flags:02x} move={is_move} char={char_id}")
                    print(f"    HasMatrix={has_matrix} HasCXForm={has_ct}")
                    if matrix: print(f"    Matrix: {matrix}")
                    if cxform: print(f"    CXForm: {cxform}")
                    elif has_ct: print(f"    CXForm: IDENTITY (empty)")
            break
    
    # Also check FileAttributes and SetBackgroundColor
    for t, d in tags:
        if t == 69 and len(d) >= 4:
            flags = struct.unpack_from('<I', d)[0]
            print(f"\n{label} FileAttributes: 0x{flags:08X} (UseGPU={bool(flags & 0x20)})")
        elif t == 9 and len(d) >= 3:
            r, g, b = d[0], d[1], d[2]
            print(f"{label} SetBackgroundColor: RGB({r},{g},{b})")

def main():
    from swf_to_n2d import N2DBuilder, save_n2d, parse_swf, validate_swf_sprites
    from compile_n2d import N2DCompiler
    
    print("=== Step 1: Import OG SWF to N2D ===")
    with open(OG, 'rb') as f:
        swf_data = f.read()
    header, tags = parse_swf(swf_data)
    validate_swf_sprites(tags)
    
    builder = N2DBuilder(header, name="smashville")
    builder.catalog_swf_tags(tags)
    builder.frame_scripts = {}
    builder.scripts = []
    builder.build_all()
    builder.build_main_timeline(tags)
    n2d_data = builder.to_n2d_json()
    
    n2d_path = os.path.join(tempfile.gettempdir(), "smashville_fixed.n2d")
    save_n2d(n2d_data, n2d_path)
    print(f"N2D saved: {n2d_path}")
    
    print("\n=== Step 2: Compile N2D back to SWF ===")
    rt_path = os.path.join(tempfile.gettempdir(), "smashville_fixed_rt.ssf")
    compiler = N2DCompiler(n2d_path, shared_dir=tempfile.gettempdir(), output_path=rt_path)
    swf_bytes = compiler.compile()
    with open(rt_path, 'rb') as f:
        swf_bytes = f.read()
    print(f"RT saved: {rt_path} ({len(swf_bytes)} bytes)")
    
    print("\n=== Step 3: Compare depth=1 PlaceObject at 'day' frame ===")
    print("\n--- OG ---")
    og_data = read_swf(OG)
    check_smashville_bg(og_data, "OG")
    
    print("\n--- NEW RT ---")
    rt_data = read_swf(rt_path)
    check_smashville_bg(rt_data, "RT")
    
    # Also compare with the OLD RT
    print("\n--- OLD RT ---")
    old_rt_data = read_swf(RT_DEST)
    check_smashville_bg(old_rt_data, "OLD_RT")
    
    # Check if the new RT is different from the old RT
    with open(rt_path, 'rb') as f:
        new_bytes = f.read()
    with open(RT_DEST, 'rb') as f:
        old_bytes = f.read()
    if new_bytes == old_bytes:
        print("\n⚠ NEW RT is IDENTICAL to OLD RT — fix may not have taken effect!")
    else:
        print(f"\n✓ NEW RT differs from OLD RT ({len(new_bytes)} vs {len(old_bytes)} bytes)")

if __name__ == '__main__':
    main()
