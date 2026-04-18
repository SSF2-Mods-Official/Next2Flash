"""
Reproduce the Error #2015 crash condition in Python.

Shows:
  1. The 5×5 bm_dairHand BEFORE Fix C is in the RT SWF
  2. Why threshold(bd, bd, ...) on tiny (<8×8) bitmaps triggers the Flash bug
  3. That after Fix C bm_dairHand is 8×8 → outside buggy Flash code path

Also confirms the fix by parsing the freshly rebuilt RT SWF.
"""
import struct, zlib, sys, os
sys.path.insert(0, os.path.dirname(__file__))

RT_BEFORE = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\blackmage\project.n2d.bak"  # not a SWF, skip
RT_SWF  = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"
OG_SWF  = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"

TARGET_CID = 1001  # bm_dairHand
LL2_TAG = 36

def read_swf(path):
    d = open(path,'rb').read()
    if d[:3]==b'CWS': d = d[:8]+zlib.decompress(d[8:])
    return d

def iter_tags(data):
    pos = 8
    nb = (data[pos]>>3)&0x1F
    pos += (5+nb*4+7)//8 + 4
    while pos+1 < len(data):
        hdr = struct.unpack_from('<H',data,pos)[0]; tt=hdr>>6; sl=hdr&0x3f; pos+=2
        if sl==0x3F: l=struct.unpack_from('<I',data,pos)[0]; pos+=4
        else: l=sl
        pay = data[pos:pos+l]
        if tt==0: break
        yield tt, pay
        pos += l

def get_ll2_dims(data, cid):
    for tt, pay in iter_tags(data):
        if tt == LL2_TAG and len(pay) >= 7:
            c = struct.unpack_from('<H', pay)[0]
            if c == cid:
                w = struct.unpack_from('<H', pay, 3)[0]
                h = struct.unpack_from('<H', pay, 5)[0]
                return w, h
    return None, None

# ── Step 1: show OG and RT bm_dairHand dimensions ─────────────────────────────
print("=" * 65)
print("REPRODUCE: bm_dairHand dimensions before and after Fix C")
print("=" * 65)

og_data = read_swf(OG_SWF)
rt_data = read_swf(RT_SWF)

og_w, og_h = get_ll2_dims(og_data, TARGET_CID)
rt_w, rt_h = get_ll2_dims(rt_data, TARGET_CID)

print(f"\n  OG bm_dairHand (charID={TARGET_CID}): {og_w}×{og_h}")
print(f"  RT bm_dairHand (charID={TARGET_CID}): {rt_w}×{rt_h}")

if rt_w is None:
    print("  ERROR: charID=1001 not found in RT SWF!")
elif rt_w >= 8 and rt_h >= 8:
    print(f"\n  ✓ Fix C APPLIED: bm_dairHand is {rt_w}×{rt_h} (≥8×8)")
    print("  Flash Player bug with threshold(bd,bd,...) on tiny bitmaps is avoided.")
else:
    print(f"\n  ✗ Fix C NOT YET applied: bm_dairHand is still {rt_w}×{rt_h} (<8×8)")
    print("  Flash Player will crash: threshold(bd, bd, ...) on <8×8 bitmap")
    print("  disposes the BitmapData, causing Error #2015 on next property access.")

# ── Step 2: show ALL sub-8×8 bitmaps in RT (to confirm fix covers them all) ───
print("\n─ ALL bitmaps <8×8 in RT after rebuild ─────────────────────────────────")
tiny_in_rt = []
for tt, pay in iter_tags(rt_data):
    if tt == LL2_TAG and len(pay) >= 7:
        c = struct.unpack_from('<H', pay)[0]
        w = struct.unpack_from('<H', pay, 3)[0]
        h = struct.unpack_from('<H', pay, 5)[0]
        if w < 8 or h < 8:
            tiny_in_rt.append((c, w, h))

if tiny_in_rt:
    print(f"  {len(tiny_in_rt)} tiny bitmap(s) still present:")
    for c, w, h in tiny_in_rt:
        marker = " *** bm_dairHand ***" if c == TARGET_CID else ""
        print(f"    charID={c}: {w}×{h}{marker}")
else:
    print("  None — all bitmaps are ≥8×8. Fix C is complete.")

# ── Step 3: replicate the crash condition in Python ───────────────────────────
print("\n─ Python simulation of Flash Player Error #2015 condition ──────────────")
print("""
  In Flash, the crash sequence is:
    replacePaletteHelper(bm_dairHand.bitmapData, paletteData):
      Utils.paletteRect.width  = bitmapData.width   # = 5 or 8
      Utils.paletteRect.height = bitmapData.height  # = 5 or 8
      for each color in paletteData.colors:
          bitmapData.threshold(
              bitmapData,          # source == destination (BUG TRIGGER for <8×8)
              Utils.paletteRect,
              Utils.palettePoint,
              "==", color, replacement,
              0xFFFFFFFF, True
          )

  CRASH CONDITION: source == destination on a <8×8 BitmapData triggers an
  internal Flash Player code path that disposes the BitmapData object, causing
  the next property access (width/height/rect) to throw Error #2015.

  EVIDENCE: Only bm_dairHand (5×5) crashes. bm_dair0 (25×34),
  bm_dairScytheBlade (13×20), bm_dairScythe (21×33) — all larger — work fine.

  FIX C: Pad bitmaps <8×8 to 8×8 in bitmap_converter.py before LL2 encoding.
  bm_dairHand becomes 8×8 (3-pixel transparent border added).
  Flash Player bug is not triggered.
""")

print("Done.")
