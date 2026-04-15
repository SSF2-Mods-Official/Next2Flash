"""Verify morph end-state has content in roundtripped SWF."""
import struct, zlib
from swf_binary_io import BitReader
from swf_shape_to_recodes import parse_define_morph_shape_to_recodes

with open('test_swfs/lloyd_rt.swf', 'rb') as f:
    data = f.read()
if data[:3] == b'CWS':
    flen = struct.unpack_from('<I', data, 4)[0]
    body = zlib.decompress(data[8:])
    data = b'FWS' + data[3:8] + body[:flen-8]

br = BitReader(data, 8)
nb = br.read_ub(5)
for _ in range(4): br.read_sb(nb)
br.align()
br.read_ui8(); br.read_ui8(); br.read_ui16()
pos = br.byte_pos

morph_count = 0
morph_end_nonempty = 0
while pos < len(data):
    if pos + 2 > len(data): break
    hdr = struct.unpack_from('<H', data, pos)[0]
    tt = hdr >> 6
    tl = hdr & 0x3F
    if tl == 0x3F:
        tl = struct.unpack_from('<I', data, pos+2)[0]
        bs = pos + 6
    else:
        bs = pos + 2
    body_raw = data[bs:bs+tl]
    if tt in (46, 84):
        morph_count += 1
        try:
            cid = struct.unpack_from('<H', body_raw)[0]
            sr, sb, er, eb, hb = parse_define_morph_shape_to_recodes(tt, body_raw[2:], {})
            has_end = len(er) > 1
            if has_end:
                morph_end_nonempty += 1
            print(f'Morph cid={cid} tag={tt}: start={len(sr)} end={len(er)} end_ok={has_end}')
        except Exception as e:
            print(f'Morph parse error: {e}')
    pos = bs + tl
    if tt == 0: break

print(f'\nTotal morphs: {morph_count}, end-state non-empty: {morph_end_nonempty}')
