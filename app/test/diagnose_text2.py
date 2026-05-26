#!/usr/bin/env python3
"""Deeper diagnosis: what 3 tags are missing, and are font IDs valid?"""
import os, struct, sys, tempfile, zlib
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import swf_to_n2d, compile_n2d
from validate_xref import parse_swf

TAG_NAMES = {
    0: 'End', 1: 'ShowFrame', 2: 'DefineShape', 5: 'RemoveObject',
    6: 'DefineBits', 9: 'SetBgColor', 10: 'DefineFont', 11: 'DefineText',
    14: 'DefineSound', 15: 'StartSound', 20: 'DefineBitsLossless',
    21: 'DefineBitsJPEG2', 22: 'DefineShape2', 24: 'Protect',
    26: 'PlaceObject2', 28: 'RemoveObject2', 32: 'DefineShape3',
    33: 'DefineText2', 35: 'DefineBitsJPEG3', 36: 'DefineBitsLossless2',
    37: 'DefineEditText', 39: 'DefineSprite', 43: 'FrameLabel',
    45: 'SoundStreamHead2', 46: 'DefineMorphShape', 48: 'DefineFont2',
    56: 'ExportAssets', 69: 'FileAttributes', 70: 'PlaceObject3',
    73: 'FontAlignZones', 74: 'CSMTextSettings', 75: 'DefineFont3',
    76: 'SymbolClass', 82: 'DoABC2', 83: 'DefineShape4',
    84: 'DefineMorphShape2', 86: 'SceneFrameLabel', 88: 'DefineFontName',
}

# Set N2F_TEST_SWF env var or replace this path with your local SWF file
swf_path = os.environ.get('N2F_TEST_SWF', r'\path\to\your.swf')

with open(swf_path, 'rb') as f:
    orig_data = f.read()

# Roundtrip
with tempfile.TemporaryDirectory(prefix='diag2_') as tmp:
    n2d_path = os.path.join(tmp, 'project.n2d')
    rt_path = os.path.join(tmp, 'rt.swf')
    header, tags = swf_to_n2d.parse_swf(orig_data)
    builder = swf_to_n2d.N2DBuilder(header, name='test')
    builder.catalog_swf_tags(tags)
    try:
        scripts, fs = swf_to_n2d.decompile_all_scripts(builder.global_raw_tags)
        builder.frame_scripts = fs
        if scripts: builder.scripts.extend(scripts)
    except: pass
    builder.build_all()
    builder.build_main_timeline(tags)
    builder._embed_bitmap_data_in_recodes()
    n2d = builder.to_n2d_json()
    swf_to_n2d.save_n2d(n2d, n2d_path)
    compiler = compile_n2d.N2DCompiler(n2d_path, tmp, rt_path, sdk_path=None)
    compiler.compile()
    with open(rt_path, 'rb') as f:
        rt_data = f.read()

orig_tags = parse_swf(orig_data)
rt_tags = parse_swf(rt_data)

# 1. Tag type histogram comparison
print("=== TAG TYPE HISTOGRAM ===")
orig_hist = {}
for tt, _ in orig_tags:
    orig_hist[tt] = orig_hist.get(tt, 0) + 1
rt_hist = {}
for tt, _ in rt_tags:
    rt_hist[tt] = rt_hist.get(tt, 0) + 1

all_types = sorted(set(orig_hist) | set(rt_hist))
for tt in all_types:
    o = orig_hist.get(tt, 0)
    r = rt_hist.get(tt, 0)
    name = TAG_NAMES.get(tt, f'tag{tt}')
    marker = '  **DIFF**' if o != r else ''
    if o != r or o > 0:
        print(f"  {name:25s} ({tt:3d}): orig={o:4d}  rt={r:4d}{marker}")

# 2. Check what tags went MISSING
print("\n=== MISSING TAGS DETAIL ===")
for tt in all_types:
    o = orig_hist.get(tt, 0)
    r = rt_hist.get(tt, 0)
    if o > r:
        print(f"  {TAG_NAMES.get(tt, f'tag{tt}')} ({tt}): lost {o - r} tags")
    elif r > o:
        print(f"  {TAG_NAMES.get(tt, f'tag{tt}')} ({tt}): gained {r - o} tags")

# 3. Check DefineEditText: are font IDs valid in roundtripped?
DEFINE_TAGS = {2, 22, 32, 83, 6, 21, 35, 90, 20, 36, 39, 46, 84,
               11, 33, 48, 75, 10, 14, 37, 87}
FONT_TAGS = {10, 48, 75}

rt_defined = {}
for tt, body in rt_tags:
    if tt in DEFINE_TAGS and len(body) >= 2:
        cid = struct.unpack_from('<H', body, 0)[0]
        rt_defined[cid] = tt

rt_fonts = {cid for cid, t in rt_defined.items() if t in FONT_TAGS}
print(f"\n=== FONT IDs in roundtripped SWF: {sorted(rt_fonts)} ===")

# Check EditText font refs
def skip_rect(buf, off):
    nbits = (buf[off] >> 3) & 0x1f
    total = 5 + nbits * 4
    return off + (total + 7) // 8

bad_fonts = []
for tt, body in rt_tags:
    if tt == 37 and len(body) >= 6:
        cid = struct.unpack_from('<H', body, 0)[0]
        b = body[2:]
        off = skip_rect(b, 0)
        flags1 = b[off]; off += 1
        flags2 = b[off]; off += 1
        if flags1 & 0x01:
            fid = struct.unpack_from('<H', b, off)[0]
            if fid not in rt_defined:
                bad_fonts.append((cid, fid))
                print(f"  BAD: EditText cid={cid} refs font {fid} (NOT DEFINED)")
            elif rt_defined[fid] not in FONT_TAGS:
                bad_fonts.append((cid, fid))
                print(f"  BAD: EditText cid={cid} refs {fid} which is {TAG_NAMES.get(rt_defined[fid], '?')}")

# Also check DefineText font refs
for tt, body in rt_tags:
    if tt in (11, 33) and len(body) >= 6:
        cid = struct.unpack_from('<H', body, 0)[0]
        # Quick scan: just check if any 2-byte value after flags&0x08 points to non-font
        # (full parse is complex, just report counts)

if not bad_fonts:
    print("  All EditText font references are valid!")

# 4. Count how original SWF was loaded - check if texts went through rebuild
print("\n=== N2D TEXT ENTRIES ===")
import json, zipfile
swf_to_n2d.save_n2d(n2d, os.path.join(tmp if os.path.isdir(tmp) else tempfile.mkdtemp(), 'check.n2d'))

# Check the N2D directly
import io
n2d_data = n2d  # already in memory
libs = n2d_data.get('libraries', [])
text_libs = [l for l in libs if l.get('type') == 'text']
print(f"  Total text libraries: {len(text_libs)}")
has_raw = sum(1 for l in text_libs if l.get('rawTagBody'))
no_raw = sum(1 for l in text_libs if not l.get('rawTagBody'))
print(f"  With rawTagBody: {has_raw}")
print(f"  Without rawTagBody (will use rebuild): {no_raw}")

# Check one without raw
for l in text_libs:
    if not l.get('rawTagBody'):
        print(f"\n  Example text WITHOUT rawTagBody:")
        print(f"    id={l['id']}, text={l.get('text','')[:60]!r}")
        print(f"    html={l.get('html')}, size={l.get('size')}")
        break

# 5. Check where the screenshot issues come from
print("\n=== LOOKING FOR 'btn gameM' and similar ===")
# Search all sprite sub-tags for instance names
for tt, body in rt_tags:
    if tt == 39 and len(body) >= 4:
        sprite_cid = struct.unpack_from('<H', body, 0)[0]
        data = body[4:]  # after charID + frameCount
        pos = 0
        while pos < len(data):
            if pos + 2 > len(data): break
            h = struct.unpack_from('<H', data, pos)[0]
            stt = h >> 6; sln = h & 0x3F; shdr = 2
            if sln == 0x3F:
                sln = struct.unpack_from('<I', data, pos + 2)[0]; shdr = 6
            sub = data[pos+shdr:pos+shdr+sln]
            if stt == 26 and len(sub) >= 3:
                flags = sub[0]
                if flags & 0x20:  # HasName
                    # Find name string after matrix/cxform
                    # Quick: search for "btn" or "gameM"
                    try:
                        txt = sub.decode('latin-1')
                        if 'btn' in txt.lower() or 'game' in txt.lower():
                            depth = struct.unpack_from('<H', sub, 1)[0]
                            char_id = struct.unpack_from('<H', sub, 3)[0] if flags & 0x02 else None
                            print(f"  Sprite {sprite_cid}: PlaceObj2 depth={depth} charId={char_id} has 'btn/game' in body")
                    except: pass
            pos += shdr + sln
            if stt == 0: break
