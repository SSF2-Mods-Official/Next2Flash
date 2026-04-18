# Error #2015 Disposed BitmapData — Active Investigation Log

> **COMPACT SUMMARY**: charID fix (swfCharId preservation) is implemented and **working** —
> `bm_dairHand@32831891` IS the correct class (Flash Player found it). But the BitmapData
> is DISPOSED when `threshold()` is called. Root cause UNKNOWN after exhaustive static analysis.

---

## Problem

After roundtripping `blackmage.ssf` (SWF→N2D→SWF), `Error #2015: Invalid BitmapData` fires
during the **dair attack** at `BitmapData.threshold()` in `Utils.replacePaletteHelper()`.

### Call Stack
```
Utils.replacePaletteHelper()  [Utils.as:682]   ← CRASH HERE
Utils$.replacePalette()        [Utils.as:657]
InteractiveSprite.updatePaletteSwap() [InteractiveSprite.as:983]
Character.updatePaletteSwap()         [Character.as:9995]
Character.playFrame()                 [Character.as:15854]
Character.m_controlFrames()           [Character.as:17949]
Character.setState()                  [Character.as:1348]
Character.Attack()
```

---

## Error #2015 — What It Means

From AS3 reference: thrown ONLY when `dispose()` has been called on a BitmapData,
or when it was created with width=0 / height=0.

After the crash, Flash Debugger shows:
```
bitmapData = bm_dairHand@32831891
  height:      Error #2015: Invalid BitmapData.
  rect:        Error #2015: Invalid BitmapData.
  transparent: Error #2015: Invalid BitmapData.
  width:       Error #2015: Invalid BitmapData.
```
`bm_dairHand@32831891` exists as an object (correct class was found → charID fix worked),
but all properties throw → explicit `dispose()` was called on it before `threshold()`.

---

## What Has Been Implemented

### Fix 1: swfCharId Preservation (IMPLEMENTED — not sufficient)
- `AllocateCharIDsStage` in `compilation_pipeline.py` now uses `lib.get('swfCharId')`
- `_assign_ids()` in `compile_n2d.py` similarly updated
- Result: RT SWF charIDs now match OG identically:
  - `bm_dairHand` → charID=1001 ✓  (`bm_dair0` → charID=1004, `DAir_73` → charID=1471)
- Also removed companion DS3 tags from `_emit_bitmap()` (they caused blurriness, not a fix)
- Crash **still persists** after this fix was applied and tested

---

## Confirmed After Exhaustive Analysis

| Check | RT | OG | Match? |
|-------|----|----|--------|
| charID=1001 tag type | LL2 (tag 36) | LL2 (tag 36) | ✅ |
| charID=1001 dims | 5×5, format=5 | 5×5, format=5 | ✅ |
| charID=1001 pixel data | 100 bytes ARGB | 100 bytes ARGB | ✅ Identical |
| Sprite 1471 (DAir_73) frame structure | 34 frames | 34 frames | ✅ Byte-identical |
| Sprite 1556 (m_sprite) structure | same | same | ✅ Byte-identical |
| SymbolClass charID=1001 → `bm_dairHand` | ✅ | ✅ | ✅ |
| DoABC payload | 253301 B | 253301 B | ✅ Byte-identical |
| SymbolClass payload | 11482 B | 11482 B | ✅ Byte-identical |
| Duplicate charIDs in SWF | None | None | ✅ |
| Non-LL2 PO3+HasImage placements | None | None | ✅ |
| DS3 shapes with dair bitmap fills | None | None | ✅ |
| dispose() calls targeting stance bitmaps | None | None | ✅ |
| `Utils.paletteRect.x/y` modified elsewhere | No | No | ✅ |

### SWF Structural Differences (these CANNOT explain the crash)
```
                       OG      RT
DefineBitsLossless2:   735     785   (50 extra from JPEG3→LL2 conversion)
Total shapes:          497     497   (same count; OG=DS1/2/3/4 mix, RT=all DS3)
DefineSprite:          205     205
LL2 zlib level:         9       6   (78DA vs 789C — cosmetic, same decompressed bytes)
```

---

## DAir_73 Frame Structure (Sprite 1471)

Both OG and RT are byte-identical. Key points:
- **Frame 1**: `PO3 depth=9 charID=1001 has_image=1` places bm_dairHand
- **Frames 2–6**: no tag at depth=9 (bm_dairHand persists)
- **Frames 7–34**: `PO2 depth=9` (move-only, bm_dairHand still there)
- **NO `RemoveObject2 depth=9`** in any of the 34 frames

bm_dairHand persists at depth=9 throughout the ENTIRE 34-frame animation without being
removed or replaced. It is only used in Sprite 1471 (no other sprite references charID=1001).

### `replacePalette` traversal of DAir_73 (recursion=2):
1. `depth=1`: **bm_dair0** (25×34) → `threshold()` → ✅ WORKS
2. `depth=4` sub-sprite (Sprite 1469) → recurse:
   - `bm_dairScytheBlade` (13×20) → ✅ WORKS
   - `bm_dairScythe` (21×33) → ✅ WORKS
3. `depth=9`: **bm_dairHand** (5×5) → ❌ **CRASH**

Only bm_dairHand (the SMALLEST at 5×5) fails.

---

## Root Cause — Still Unknown

### Strong Candidates

**H1: Flash Player bug with `threshold(bd, bd, ...)` (self-source) on tiny bitmaps (<8×8)**
The call is `bitmapData.threshold(bitmapData, rect, ...)` where source==destination.
For bm_dair0 (25×34), scythe (21×33), scytheBlade (13×20) — all larger — it WORKS.
For bm_dairHand (5×5) — smallest — it FAILS.
Possibly Flash Player has a code path that enters an invalid state for source==dest
on very small bitmaps, causing it to dispose the BitmapData.

**H2: Flash disposes HasImage BitmapDatas on display list removal**
When Sprite 1556 navigates AWAY from the dair state, Flash removes DAir_73. If Flash
disposes BitmapDatas tied to `has_image=True` placements on removal, then bm_dairHand
would be disposed after the FIRST dair. On the SECOND dair attempt, `bm_dairHand` is
already disposed → threshold() fails.

**H3: 50 extra LL2 tags cause Flash Player memory pressure**
Flash may have a pool limit (~750 BitmapData instances). RT's 785 LL2 (vs 735 OG)
could cause the oldest BitmapDatas to be evicted. bm_dairHand (charID=1001) might be
among the evicted ones by the time dair is first triggered.

### Ruled Out
- Incorrect charIDs (now match OG exactly)
- Incorrect LL2 pixel data (byte-identical to OG)
- Incorrect sprite structure (byte-identical to OG)
- Different DoABC bytecode (raw OG passthrough confirmed = 253301 bytes)
- Different SymbolClass (byte-identical)
- Duplicate charIDs (none found)
- Non-LL2 HasImage placements (none found)
- DS3 shapes with dair bitmap fills (none, verified by proper parsing)
- Direct dispose() calls on stance bitmaps in engine AS3 code

---

## Proposed Fixes

### Fix A — try-catch in replacePaletteHelper (BAND-AID, safe to apply now)
Prevents crash; bm_dairHand won't recolor but game is playable.  
Requires mxmlc recompile (see instructions below).

```actionscript
// Utils.as line 677 — replacePaletteHelper
public static function replacePaletteHelper(bitmapData:BitmapData, paletteData:Object):void {
    Utils.paletteRect.width = bitmapData.width;
    Utils.paletteRect.height = bitmapData.height;
    var i:int;
    while (i < paletteData.colors.length) {
        if (paletteData.colors[i] != paletteData.replacements[i]) {
            try {
                bitmapData.threshold(bitmapData, Utils.paletteRect, Utils.palettePoint,
                    "==", paletteData.colors[i], paletteData.replacements[i],
                    0xFFFFFFFF, true);
            } catch (e:Error) { /* Disposed BitmapData — skip silently */ }
        };
        i++;
    };
}
```

### Fix B — Clone source (POSSIBLE ROOT CAUSE FIX for H1)
Eliminates source==dest in threshold(). Full palette swap preserved.

```actionscript
// Utils.as — replacePaletteHelper
public static function replacePaletteHelper(bitmapData:BitmapData, paletteData:Object):void {
    Utils.paletteRect.width = bitmapData.width;
    Utils.paletteRect.height = bitmapData.height;
    var sourceCopy:BitmapData = bitmapData.clone();
    var i:int;
    while (i < paletteData.colors.length) {
        if (paletteData.colors[i] != paletteData.replacements[i]) {
            bitmapData.threshold(sourceCopy, Utils.paletteRect, Utils.palettePoint,
                "==", paletteData.colors[i], paletteData.replacements[i],
                0xFFFFFFFF, false);
        };
        i++;
    };
    sourceCopy.dispose();
}
```

### Fix C — Pad small bitmaps to 8×8 minimum (targets H1)
In `app/bitmap_converter.py`, `build_define_bits_lossless2()`, before the numpy block:
```python
# Pad to 8×8 minimum to avoid potential Flash Player small-bitmap bugs
if w < 8 or h < 8:
    pw, ph = max(w, 8), max(h, 8)
    import numpy as np
    padded = np.zeros((ph * pw * 4,), dtype=np.uint8)
    for row in range(h):
        padded[row*pw*4 : row*pw*4 + w*4] = np.frombuffer(pixel_data[row*w*4:(row+1)*w*4], np.uint8)
    pixel_data = padded.tobytes()
    w, h = pw, ph
```

### Fix D — Use zlib level 9 (LOW COST TEST, probably no effect)
In `bitmap_converter.py` line 78: `zlib.compress(argb_bytes, 9)` instead of `6`.
Makes RT LL2 tags byte-identical to OG. Rebuild + test: 3 minutes.

---

## IMMEDIATE NEXT ACTIONS

### 1. Determine: first or second dair? (1 minute of play testing)
Load the game. Attempt dair WITHOUT having performed it before. Does it crash?
- **Crashes on first dair**: BitmapData invalid before first use. 
  Likely H3 (pool eviction) or a constructor issue.
- **Crashes on second dair**: Flash disposes HasImage BitmapDatas on removal.
  Likely H2. Fix: re-initialize BitmapData after each animation removes it.

### 2. Apply Fix D (2 minutes) — cheap test
```python
# bitmap_converter.py line 78
compressed = zlib.compress(argb_bytes, 9)  # was level 6
```
Run `python app\_recompile_blackmage.py` and test. If fixed: zlib level quirk in Flash.

### 3. Apply Fix C (5 minutes) — pad small bitmaps
Add the pixel padding code in `build_define_bits_lossless2`. Rebuild and test.

### 4. Try mxmlc recompile for Fix A/B (10 minutes)
Force `scripts_modified = True` in `compilation_pipeline.py` line 644:
```python
scripts_modified = True  # TEMP: force mxmlc for Utils.as fix testing
```
Check that mxmlc compiles without TypeError #1009. If it does, apply Fix B.

---

## Key Files

```
RT SWF:  C:\...\ssf2-idk-140x-original\src\...\data\character\blackmage.ssf
OG SWF:  C:\...\ssf2-idk-140x-original\build\data\character\blackmage.ssf
N2D:     app\converted\blackmage\project.n2d
Scripts: app\converted\blackmage\scripts\

Utils.as:
  C:\...\ssf2-idk-140x-original\src\...\com\mcleodgaming\ssf2\util\Utils.as
  replacePaletteHelper() at line ~672
  threshold() call at line ~682

Key compiler files:
  app\compile_n2d.py          (_emit_bitmap, PO3 has_image logic)
  app\compilation_pipeline.py (AllocateCharIDsStage, CompileAS3Stage)
  app\bitmap_converter.py     (build_define_bits_lossless2, zlib level 6)
  app\_recompile_blackmage.py (run from app\ to rebuild)
  app\_sync_n2d_scripts.py    (run after .as changes → keeps scriptsModified=False)
```

## Diagnostic Scripts (in `app/`)
- `_check_dair73_frames.py` — all 34 frames of Sprite 1471, OG vs RT
- `_check_dup_charids.py` — duplicate charID detection
- `_check_hasimage_nonll2.py` — non-LL2 HasImage PO3 scan
- `_check_ll2_bytes.py` — compare raw LL2 zlib bytes OG vs RT
- `_check_dair73_parent.py` — Sprite 1556 frame labels and structure
- `_check_symclass.py` — SymbolClass charID→class mapping verification
- `_check_cid304.py` — identify depth-10/12 mystery sprite (DefineSprite 304)
- `_check_ds3_fills.py` — DS3 bitmap fill cross-reference scan

## Historical Attempts
- **Attempt 1**: DS3 companion wrapper shapes — fixed crash but broke palette swap (Shape != Bitmap). Reverted.
- **Attempt 2**: charID preservation — implemented, charIDs now match OG. Crash STILL HAPPENS.
