"""Parse DefineEditText tags from the RT SWF to check text content."""
import struct, zlib
from swf_binary_io import BitReader

data = open('test_swfs/lloyd_rt.swf', 'rb').read()
if data[:3] == b'CWS':
    body = zlib.decompress(data[8:])
    data = data[:8] + body

# Skip SWF header
pos = 8
br = BitReader(data[pos:])
nbits = br.read_ub(5)
for _ in range(4):
    br.read_sb(nbits)
br.align()
pos += br.byte_pos
pos += 4  # frame rate + frame count

# Scan for DefineEditText tags (tag 37)
while pos < len(data) - 2:
    tag_hdr = struct.unpack_from('<H', data, pos)[0]
    tag_type = tag_hdr >> 6
    tag_len = tag_hdr & 0x3f
    pos += 2
    if tag_len == 0x3f:
        tag_len = struct.unpack_from('<I', data, pos)[0]
        pos += 4
    if tag_type == 37:  # DefineEditText
        tag_data = data[pos:pos+tag_len]
        char_id = struct.unpack_from('<H', tag_data, 0)[0]
        # Find initial text - scan for last two null bytes
        idx = len(tag_data) - 1
        nulls = []
        while idx >= 2 and len(nulls) < 3:
            if tag_data[idx] == 0:
                nulls.append(idx)
            idx -= 1
        if len(nulls) >= 2:
            text_start = nulls[1] + 1
            text_end = nulls[0]
            init_text = tag_data[text_start:text_end].decode('utf-8', errors='replace')
            print(f'CID {char_id}: "{init_text}"')
        else:
            print(f'CID {char_id}: (no text found)')
    pos += tag_len
