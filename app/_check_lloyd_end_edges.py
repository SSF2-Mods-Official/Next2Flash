"""Check that all morph shapes in lloyd_rt.swf have end-state fill_bits=0, line_bits=0."""
import struct, os, sys
from swf_binary_io import BitReader

def check_all_morphs(path):
    import zlib
    with open(path, 'rb') as f:
        sig = f.read(3)
        ver = struct.unpack('B', f.read(1))[0]
        flen = struct.unpack('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    # Skip RECT header + frame rate (2) + frame count (2)
    nbits = (rest[0] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    rect_bytes = (total_bits + 7) // 8
    pos = rect_bytes + 4
    count = 0
    bad = 0
    while pos < len(rest):
        tc = struct.unpack_from('<H', rest, pos)[0]
        pos += 2
        tt = tc >> 6
        ll = tc & 0x3F
        if ll == 0x3F:
            ll = struct.unpack_from('<I', rest, pos)[0]
            pos += 4
        if tt in (46, 84):
            body = rest[pos:pos+ll]
            br2 = BitReader(body, 2)
            for _ in range(2):
                nb2 = br2.read_ub(5)
                for __ in range(4): br2.read_sb(nb2)
                br2.align()
            if tt == 84:
                for _ in range(2):
                    nb2 = br2.read_ub(5)
                    for __ in range(4): br2.read_sb(nb2)
                    br2.align()
                br2.read_ui8()
            br2.align()
            offset = struct.unpack_from('<I', br2.data, br2.byte_pos)[0]
            br2.byte_pos += 4
            after_offset = br2.byte_pos
            end_pos = after_offset + offset
            br2.byte_pos = end_pos
            br2.bit_pos = 0
            end_hdr = br2.read_ui8()
            efb = end_hdr >> 4
            elb = end_hdr & 0x0F
            cid = struct.unpack_from('<H', body, 0)[0]
            count += 1
            if efb != 0 or elb != 0:
                bad += 1
                print(f"  BAD: tag={tt} charId={cid} end fill_bits={efb} line_bits={elb}")
        pos += ll
        if tt == 0:
            break
    print(f"Total morphs: {count}, bad: {bad}")

lloyd = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\lloyd.ssf"
n2d = "test_swfs/lloyd_rt.n2d"
rt = "test_swfs/lloyd_rt.swf"

# Always re-roundtrip to pick up latest code changes
os.system(f'python swf_to_n2d.py "{lloyd}" "{n2d}" >NUL 2>&1')
os.system(f'python compile_n2d.py "{n2d}" -o "{rt}" --shared . >NUL 2>&1')

print("lloyd_rt.swf:")
check_all_morphs(rt)
