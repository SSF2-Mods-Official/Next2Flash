"""Check bitmap fill smooth/repeat values stored in N2D for shapes with known mismatches."""
import zipfile, msgpack, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swf_constants import ShapeCommand

N2D = "test_swfs/lloyd.n2d"
BITMAP_FILL = ShapeCommand.BITMAP_FILL.value  # 13

# Shapes with known bitmap fill type mismatches (from comparison output)
# orig=0x43 (clipped, non-smooth) -> rt=0x41 (clipped, smooth)
MISMATCH_0x43_to_0x41 = [139, 141, 143, 145, 205, 207, 209, 211, 213, 215, 217]
# orig=0x41 (clipped, smooth) -> rt=0x43 (clipped, non-smooth)
MISMATCH_0x41_to_0x43 = [248, 251, 253, 254, 255, 256, 257, 263, 1547]
# orig=0x42 (repeating, non-smooth) -> rt=0x43 (clipped, non-smooth)
MISMATCH_0x42_to_0x43 = [1539]

ALL_MISMATCH = MISMATCH_0x43_to_0x41 + MISMATCH_0x41_to_0x43 + MISMATCH_0x42_to_0x43

with zipfile.ZipFile(N2D) as z:
    with z.open("project.msgpack") as mf:
        project = msgpack.unpack(mf, raw=False)

libs = project.get('libraries', [])
by_cid = {}
for lib in libs:
    if lib.get('type') == 'shape' and not lib.get('endRecodes'):
        cid = lib.get('swfCharId')
        if cid is not None:
            by_cid[cid] = lib

for cid in ALL_MISMATCH:
    if cid not in by_cid:
        print(f"CID {cid}: NOT FOUND in N2D")
        continue
    
    lib = by_cid[cid]
    recodes = lib.get('recodes', [])
    
    # Find BITMAP_FILL commands in recodes
    i = 0
    while i < len(recodes):
        if recodes[i] == BITMAP_FILL:
            i += 1  # skip CMD
            bmp_id = recodes[i]; i += 1
            matrix = recodes[i]; i += 1
            repeat_val = recodes[i]; i += 1
            smooth_val = recodes[i]; i += 1
            
            expected = ''
            if cid in MISMATCH_0x43_to_0x41:
                expected = 'should be: repeat=no-repeat, smooth=False (orig 0x43)'
            elif cid in MISMATCH_0x41_to_0x43:
                expected = 'should be: repeat=no-repeat, smooth=True (orig 0x41)'
            elif cid in MISMATCH_0x42_to_0x43:
                expected = 'should be: repeat=repeat, smooth=False (orig 0x42)'
            
            # Show bmp_id as type + value (avoid printing pixel data)
            bmp_type = type(bmp_id).__name__
            if isinstance(bmp_id, dict):
                bmp_info = f"dict(width={bmp_id.get('width')},height={bmp_id.get('height')},bitmapId={bmp_id.get('bitmapId')})"
            else:
                bmp_info = repr(bmp_id)
            print(f"CID {cid}: bmp={bmp_info}, repeat={repeat_val!r}, smooth={smooth_val!r}  ({expected})")
            break
        else:
            i += 1
    else:
        print(f"CID {cid}: no BITMAP_FILL in recodes (len={len(recodes)})")
