"""Check the existing RT pichu the user has been testing with."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))
from swf_binary_io import BitReader

EXISTING_RT = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\pichu.ssf"

def decompress_swf(raw):
    sig = raw[:3]
    if sig == b'CWS': return raw[:8] + zlib.decompress(raw[8:])
    return raw

def get_offset(data):
    br = BitReader(data, 8)
    nb = br.read_ub(5)
    for _ in range(4): br.read_sb(nb)
    br.align()
    return br.byte_pos + 4

def parse_tags(data, offset):
    tags = []
    while offset < len(data):
        tag_code_and_length = struct.unpack_from('<H', data, offset)[0]
        tag_type = tag_code_and_length >> 6
        tag_length = tag_code_and_length & 0x3F
        offset += 2
        if tag_length == 0x3F:
            tag_length = struct.unpack_from('<I', data, offset)[0]
            offset += 4
        tag_data = data[offset:offset + tag_length]
        tags.append((tag_type, tag_data))
        offset += tag_length
        if tag_type == 0:
            break
    return tags

def find_idle3_sprite(tags):
    for tag_type, tag_data in tags:
        if tag_type == 39:
            char_id = struct.unpack_from('<H', tag_data, 0)[0]
            frame_count = struct.unpack_from('<H', tag_data, 2)[0]
            if frame_count == 249:
                inner_tags = parse_tags(tag_data, 4)
                return char_id, inner_tags
    return None, None

with open(EXISTING_RT, 'rb') as f:
    raw = f.read()
data = decompress_swf(raw)
offset = get_offset(data)
tags = parse_tags(data, offset)
cid, inner_tags = find_idle3_sprite(tags)

if cid is None:
    print("Idle_3 (249 frames) NOT FOUND in existing RT")
else:
    removes = 0
    po_move = 0
    po_fresh = 0
    frame = 0
    for tag_type, tag_data in inner_tags:
        if tag_type == 1: frame += 1
        elif tag_type == 28:
            depth = struct.unpack_from('<H', tag_data, 0)[0]
            if depth == 1: removes += 1
        elif tag_type == 70:
            flags = struct.unpack_from('<H', tag_data, 0)[0]
            depth = struct.unpack_from('<H', tag_data, 2)[0]
            is_move = bool(flags & 0x01)
            has_cid = bool(flags & 0x02)
            if depth == 1 and has_cid:
                if is_move: po_move += 1
                else: po_fresh += 1
    print(f"Existing RT pichu Idle_3 cid={cid}:")
    print(f"  RemoveObject2 at depth 1: {removes}")
    print(f"  PO3 is_move=True + has_cid: {po_move}")
    print(f"  PO3 is_move=False + has_cid: {po_fresh}")
