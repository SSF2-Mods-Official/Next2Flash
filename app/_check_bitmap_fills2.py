"""Check bitmap fills in N2D shape recodes after a fresh import.
Uses the compile_n2d module directly to trace the bitmap explosion."""
import sys, os, struct, zlib
sys.path.insert(0, os.path.dirname(__file__))

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

# Do a fresh import using N2DBuilder
from swf_to_n2d import parse_swf, N2DBuilder

with open(OG, "rb") as f:
    raw = f.read()
if raw[:3] == b"CWS":
    raw = raw[:8] + zlib.decompress(raw[8:])

header, tags = parse_swf(raw)
print(f"Parsed SWF: {len(tags)} tags")

builder = N2DBuilder(header, "fox")
builder.catalog_swf_tags(tags)
builder.frame_scripts = {}
builder.build_all()
result = builder.to_n2d_json()
libs = result["libraries"]
print(f"Library: {len(libs)} items")

# Count by type
from collections import Counter
types = Counter(lib.get("type") for lib in libs)
print(f"Types: {dict(types)}")

bitmap_ids = {lib["id"] for lib in libs if lib.get("type") == "bitmap"}
print(f"Bitmap IDs: {len(bitmap_ids)}")

# Find shapes with bitmap fills
BITMAP_FILL = 3
shapes_with_bfills = 0
total_bfills = 0
resolved_bfills = 0
unresolved_bfills = 0
embedded_bfills = 0  # has pixel data embedded

for lib in libs:
    if lib.get("type") != "shape":
        continue
    recodes = lib.get("recodes", [])
    if not recodes:
        continue
    
    i = 0
    found = False
    while i < len(recodes):
        val = recodes[i]
        if isinstance(val, bool):
            break
        cmd = int(val)
        i += 1
        
        if cmd == BITMAP_FILL:
            total_bfills += 1
            if not found:
                shapes_with_bfills += 1
                found = True
            
            bmp_ref = recodes[i] if i < len(recodes) else None
            if isinstance(bmp_ref, (int, float)):
                bid = int(bmp_ref)
                if bid in bitmap_ids:
                    resolved_bfills += 1
                elif bid > 0:
                    unresolved_bfills += 1
                else:
                    embedded_bfills += 1
                i += 1  # skip ref
                if i < len(recodes) and isinstance(recodes[i], list):
                    i += 1  # matrix
                if i < len(recodes):
                    i += 1  # repeat
                if i < len(recodes):
                    i += 1  # smooth
            elif isinstance(bmp_ref, dict):
                bid = bmp_ref.get("bitmapId", 0)
                buf = bmp_ref.get("buffer", "")
                if bid in bitmap_ids:
                    resolved_bfills += 1
                elif bid > 0:
                    unresolved_bfills += 1
                elif buf and len(buf) > 4:
                    embedded_bfills += 1
                else:
                    unresolved_bfills += 1
                i += 1  # skip dict
                if i < len(recodes) and isinstance(recodes[i], list):
                    i += 1  # matrix
                if i < len(recodes):
                    i += 1  # repeat
                if i < len(recodes):
                    i += 1  # smooth
            continue
        
        # Skip other command params (rough — just advance)
        # This is approximate but good enough for counting

print(f"\nShapes with bitmap fills: {shapes_with_bfills}")
print(f"Total bitmap fill references: {total_bfills}")
print(f"  Resolved to bitmap lib IDs: {resolved_bfills}")
print(f"  Unresolved (non-zero ID not in bitmaps): {unresolved_bfills}")
print(f"  Embedded (pixel data or zero ID): {embedded_bfills}")

# Now trace what happens in the compiler
from compile_n2d import N2DCompiler
print("\n\n=== COMPILATION TRACE ===")

class TracingCompiler(N2DCompiler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bmp_fill_resolved = 0
        self.bmp_fill_new = 0
    
    def _resolve_bitmap_fills(self, fill_styles):
        from shape_converter import BitmapFill
        for fs in fill_styles:
            if not isinstance(fs, BitmapFill):
                continue
            if fs.bitmap_char_id:
                continue
            if fs.bitmap_lib_id and fs.bitmap_lib_id in self._lib_to_swf_id:
                fs.bitmap_char_id = self._lib_to_swf_id[fs.bitmap_lib_id]
                self.bmp_fill_resolved += 1
                continue
            if not fs.pixel_data or len(fs.pixel_data) <= 4:
                continue
            # This is the fallback — creates a NEW bitmap
            self.bmp_fill_new += 1
            new_id = self._alloc_id()
            fs.bitmap_char_id = new_id
            self._bitmap_char_ids.add(new_id)
            from bitmap_converter import build_define_bits_lossless2
            bmp_tag = build_define_bits_lossless2(new_id, fs.width, fs.height, fs.pixel_data)
            self._definition_tags.extend(bmp_tag)

compiler = TracingCompiler(result)
swf_bytes = compiler.compile()

print(f"\nBitmap fill resolutions:")
print(f"  Resolved to existing SWF IDs: {compiler.bmp_fill_resolved}")
print(f"  Created NEW bitmap tags: {compiler.bmp_fill_new}")
print(f"\nFinal SWF: {len(swf_bytes)} bytes")

# Count bitmap tags in output
if swf_bytes[:3] == b"FWS":
    pos = 8
    nbits = (swf_bytes[pos] >> 3) & 0x1F
    total_bits = 5 + nbits * 4
    pos += (total_bits + 7) // 8
    pos += 4
    bmp_count = 0
    while pos < len(swf_bytes):
        tc = struct.unpack_from("<H", swf_bytes, pos)[0]
        tt = tc >> 6
        length = tc & 0x3F
        pos += 2
        if length == 0x3F:
            length = struct.unpack_from("<I", swf_bytes, pos)[0]
            pos += 4
        if tt in (20, 36, 35, 21, 6, 90):
            bmp_count += 1
        pos += length
        if tt == 0:
            break
    print(f"Bitmap tags in output SWF: {bmp_count}")
