"""Decode the CXFORM at frame 1 and frame 7 of smashville_bg depth=1 to verify the bug."""
import struct, zlib

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\stage\smashville.ssf"

def read_swf(path):
    with open(path, 'rb') as f:
        data = f.read()
    if data[:3] == b'CWS':
        data = b'FWS' + data[3:8] + zlib.decompress(data[8:])
    return data

class BitReader:
    def __init__(self, data, byte_offset=0):
        self.data = data
        self.bit_pos = byte_offset * 8
    
    def read_bits(self, n):
        val = 0
        for _ in range(n):
            byte_i = self.bit_pos // 8
            bit_i = 7 - (self.bit_pos % 8)
            val = (val << 1) | ((self.data[byte_i] >> bit_i) & 1)
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

def decode_matrix(data, offset):
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
    consumed = (br.bit_pos + 7) // 8 - offset
    return result, consumed

def decode_cxform_alpha(data, offset):
    br = BitReader(data, offset)
    has_add = br.read_bits(1)
    has_mul = br.read_bits(1)
    nbits = br.read_bits(4)
    result = {'has_add': has_add, 'has_mul': has_mul, 'nbits': nbits}
    
    if has_mul:
        result['mulR'] = br.read_sbits(nbits) / 256.0
        result['mulG'] = br.read_sbits(nbits) / 256.0
        result['mulB'] = br.read_sbits(nbits) / 256.0
        result['mulA'] = br.read_sbits(nbits) / 256.0
    if has_add:
        result['addR'] = br.read_sbits(nbits)
        result['addG'] = br.read_sbits(nbits)
        result['addB'] = br.read_sbits(nbits)
        result['addA'] = br.read_sbits(nbits)
    
    br.align()
    consumed = (br.bit_pos + 7) // 8 - offset
    return result, consumed

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

def main():
    og_data = read_swf(OG)
    og_tags = parse_tags(og_data, skip_header(og_data))
    
    # Find smashville_bg cid
    og_cid = None
    for t, d in og_tags:
        if t == 76:
            count = struct.unpack_from('<H', d)[0]; off = 2
            for _ in range(count):
                cid = struct.unpack_from('<H', d, off)[0]; off += 2
                end = d.index(0, off); name = d[off:end].decode(); off = end + 1
                if name == 'smashville_bg': og_cid = cid; break
    
    print(f"smashville_bg cid: {og_cid}")
    
    # Find sprite
    for t, d in og_tags:
        if t == 39 and struct.unpack_from('<H', d)[0] == og_cid:
            inner = parse_tags(d, 4)
            frame = 1
            for tt, td in inner:
                if tt == 1: frame += 1
                elif tt == 43:
                    lbl = td[:td.index(0)].decode()
                    print(f"\n--- Frame {frame}: {lbl} ---")
                elif tt == 26:  # PlaceObject2
                    flags = td[0]
                    depth = struct.unpack_from('<H', td, 1)[0]
                    off = 3
                    
                    has_char = bool(flags & 0x02)
                    has_matrix = bool(flags & 0x04)
                    has_ct = bool(flags & 0x08)
                    has_ratio = bool(flags & 0x10)
                    has_name = bool(flags & 0x20)
                    is_move = bool(flags & 0x01)
                    
                    char_id = None
                    if has_char:
                        char_id = struct.unpack_from('<H', td, off)[0]; off += 2
                    
                    matrix = None
                    if has_matrix:
                        matrix, consumed = decode_matrix(td, off); off += consumed
                    
                    cxform = None
                    if has_ct:
                        cxform, consumed = decode_cxform_alpha(td, off); off += consumed
                    
                    # Only print if depth is 1 (the one we care about)
                    if depth == 1:
                        print(f"  Frame {frame} depth={depth}: flags=0x{flags:02x} move={is_move} char={char_id}")
                        if matrix: print(f"    Matrix: {matrix}")
                        if cxform: print(f"    CXForm: {cxform}")
                        print(f"    raw: {td.hex()}")
            break

main()
