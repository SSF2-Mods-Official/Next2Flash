"""
Inspect dair bitmaps in compiled blackmage.ssf
- Find SWF char IDs allocated for dair N2D bitmap IDs (994-1004)
- Check if they have LL2 tags
- Check if they're placed in any sprites via PO3
"""
import sys, struct, zlib
sys.path.insert(0, r'C:\Users\glwex\Documents\GitHub\Next2Flash\app')
from compile_n2d import load_n2d

# Step 1: Get char ID allocation from the pipeline
from compilation_pipeline import CompilationContext, Pipeline, build_pipeline

N2D = r'C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\blackmage\project.n2d'
data, pdir = load_n2d(N2D)

# Dair bitmap N2D IDs
DAIR_N2D_IDS = {994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004}
DAIR_NAMES = {
    994: 'bm_dair7', 995: 'bm_dair6', 996: 'bm_dair5', 997: 'bm_dair4',
    998: 'bm_dair3', 999: 'bm_dair2', 1000: 'bm_dair1', 1001: 'bm_dairHand',
    1002: 'bm_dairScythe', 1003: 'bm_dairScytheBlade', 1004: 'bm_dair0'
}

# Run just the ID allocation stage
import importlib
cn = importlib.import_module('compile_n2d')

# Find allocate_char_ids function
alloc_fn = getattr(cn, 'allocate_char_ids', None)
if alloc_fn is None:
    print("Looking for allocate_char_ids in compile_n2d...")
    for name in dir(cn):
        if 'alloc' in name.lower() or 'char_id' in name.lower():
            print(f"  Found: {name}")
else:
    print("Found allocate_char_ids")

# Step 2: Parse the compiled SWF to do our own analysis
SWF = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
with open(SWF, 'rb') as f:
    raw_data = f.read()

sig = raw_data[:3]
if sig == b'CWS':
    body = zlib.decompress(raw_data[8:])
    raw = raw_data[:8] + body
elif sig == b'FWS':
    raw = raw_data
else:
    print('Unknown sig', sig)
    exit()

# Parse FrameSize to find where tags start
pos = 8
b = raw[pos]
nbits = (b >> 3) & 0x1f
total_bits = 5 + nbits*4
pos += (total_bits + 7) // 8
pos += 4  # FrameRate + FrameCount

# Scan all tags and build a map of char_id -> tag_type
tag_map = {}  # char_id -> (tag_type, file_offset)
po3_placements = []  # (container_id, depth, char_id, flags)
current_sprite = None
sprite_stack = []

def parse_tags(raw, start_pos, end_pos):
    """Parse SWF tags in a range, yield (pos, tag_type, payload)"""
    pos = start_pos
    while pos < end_pos - 1:
        hdr = struct.unpack_from('<H', raw, pos)[0]
        tag_type = hdr >> 6
        short_len = hdr & 0x3f
        hdr_size = 2
        pos += 2
        if short_len == 0x3f:
            length = struct.unpack_from('<I', raw, pos)[0]
            hdr_size += 4
            pos += 4
        else:
            length = short_len
        yield pos - hdr_size, tag_type, raw[pos:pos+length]
        pos += length
        if tag_type == 0:
            break

# Find tag start (root level)
root_end = len(raw)
ll2_ids = {}
ds3_ids = {}
po2_placements = []  # list of (depth, char_id, has_image, name)
define_sprite_ranges = []

pos = 8
b = raw[pos]
nbits = (b >> 3) & 0x1f
total_bits = 5 + nbits * 4
tag_start = pos + (total_bits + 7) // 8 + 4

print("\n=== Scanning SWF tags ===")
# First pass: collect all definitions
pos = tag_start
while pos < len(raw) - 1:
    hdr = struct.unpack_from('<H', raw, pos)[0]
    tag_type = hdr >> 6
    short_len = hdr & 0x3f
    pos += 2
    if short_len == 0x3f:
        length = struct.unpack_from('<I', raw, pos)[0]
        pos += 4
    else:
        length = short_len
    payload = raw[pos:pos+length]
    
    if tag_type == 36:  # DefineBitsLossless2
        cid = struct.unpack_from('<H', payload)[0]
        w = struct.unpack_from('<H', payload, 3)[0]
        h = struct.unpack_from('<H', payload, 5)[0]
        ll2_ids[cid] = (w, h)
    elif tag_type == 32:  # DefineShape3
        cid = struct.unpack_from('<H', payload)[0]
        ds3_ids[cid] = True
    elif tag_type == 26:  # PlaceObject2
        flags = payload[0]
        depth = struct.unpack_from('<H', payload, 1)[0]
        p = 3
        char_id = None
        has_char = flags & 0x02
        has_name = flags & 0x20
        if has_char:
            char_id = struct.unpack_from('<H', payload, p)[0]
            p += 2
        name = None
        # skip matrix, color etc to find name
        # simpler: just note has_image = PlaceObject3 flag
        po2_placements.append((depth, char_id, False, name))
    elif tag_type == 70:  # PlaceObject3
        flags1 = payload[0]
        flags2 = payload[1]
        depth = struct.unpack_from('<H', payload, 2)[0]
        p = 4
        has_char = flags1 & 0x02
        has_image = flags2 & 0x10
        has_name = flags1 & 0x20
        char_id = None
        if has_char:
            char_id = struct.unpack_from('<H', payload, p)[0]
            p += 2
        po2_placements.append((depth, char_id, has_image, None))
    elif tag_type == 0:
        break
        
    pos += length

print(f"Total LL2: {len(ll2_ids)}, Total DS3: {len(ds3_ids)}")
print(f"Total placements (PO2+PO3): {len(po2_placements)}")

# Now search for what SWF char IDs the dair bitmaps correspond to
# We need to find which LL2 char IDs correspond to the dair bitmaps
# The N2D IDs are abstract; we need the compiled SWF IDs
# The char IDs 994-1004 are N2D IDs. Let's check if those specific IDs are in the SWF LL2 list
print("\n=== Checking if N2D IDs 994-1004 directly appear as SWF char IDs ===")
for n2d_id in sorted(DAIR_N2D_IDS):
    name = DAIR_NAMES[n2d_id]
    in_ll2 = n2d_id in ll2_ids
    in_ds3 = n2d_id in ds3_ids
    placed = [(d,ci,hi) for (d,ci,hi,nm) in po2_placements if ci == n2d_id]
    print(f"  N2D ID {n2d_id} ({name}): LL2={in_ll2}, DS3={in_ds3}, placements={placed}")

# Check what IDs ARE around the dair region
print("\n=== LL2 IDs in range 980-1020 ===")
for cid in sorted(ll2_ids.keys()):
    if 980 <= cid <= 1020:
        w, h = ll2_ids[cid]
        placed = [(d,hi) for (d,ci,hi,nm) in po2_placements if ci == cid]
        in_ds3 = cid in ds3_ids
        print(f"  LL2 char_id={cid} size={w}x{h} DS3={in_ds3} placed={placed}")
