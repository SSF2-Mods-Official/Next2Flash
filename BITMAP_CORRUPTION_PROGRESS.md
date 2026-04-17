# Bitmap Corruption & Looping Investigation — Progress

## Runtime Symptom

```
ArgumentError: Error #2015: Invalid BitmapData.
  at flash.display::BitmapData/threshold()
  at com.mcleodgaming.ssf2.util::Utils$/replacePaletteHelper() [Utils.as:682]
  at com.mcleodgaming.ssf2.util::Utils$/replacePalette() [Utils.as:657]
  at com.mcleodgaming.ssf2.engine::InteractiveSprite/updatePaletteSwap() [InteractiveSprite.as:983]
  at com.mcleodgaming.ssf2.engine::Character/updatePaletteSwap() [Character.as:9995]
  at com.mcleodgaming.ssf2.engine::Character/playFrame() [Character.as:15854]
```

This fires on attack — Character.Attack() → setState() → playFrame() → updatePaletteSwap() → replacePalette() → threshold() fails because a BitmapData is invalid.

**Suspected cause**: The palette swap rasterizes the character (draw() on BitmapData), then does threshold() on the result. If any child shape or bitmap definition tag is corrupt, draw() can fail silently or produce an invalid BitmapData, and threshold() then throws.

**The "looping" behavior** is likely the game's error recovery — when the palette swap crashes mid-attack, the game catches it and resets the character state, causing the attack animation to restart from frame 1.

---

## Root Cause: Bitmap Corruption (82% of bitmaps)

### Discovery

A pixel-by-pixel comparison of OG vs RT bitmaps revealed:

| Metric | Value |
|--------|-------|
| Total LL2 bitmaps matched | 625 |
| Pixel-identical | 113 |
| **Pixel-different** | **512** |
| Max channel diff | 255 (complete corruption) |
| Avg channels differing | 96.6% |

### Why: Format 3 vs Format 5

**OG SWF bitmaps by format:**
- **512 bitmaps** use **format 3** (8-bit palette/colormapped with alpha)
- **113 bitmaps** use **format 5** (32-bit ARGB direct)

**The decoder (`decode_lossless_to_rgba` in swf_to_n2d.py:2029) correctly handles format 3** — it decompresses, reads the palette, maps indices to RGBA. The decoded RGBA pixels are stored in the N2D `buffer` field.

**The encoder (`build_define_bits_lossless2` in bitmap_converter.py:23) ALWAYS writes format 5** (32-bit ARGB). This is a valid conversion — format 5 can represent everything format 3 can.

**So the corruption is NOT in the format conversion logic itself.** The decoder and encoder both look correct in isolation.

### Where to investigate next

The corruption must be happening somewhere between decode and re-encode:

1. **N2D buffer storage** — When the decoded RGBA is stored in the N2D JSON/msgpack, is it faithfully preserved? Check base64 encoding/decoding, check if the buffer key gets mangled during web editor roundtrip.

2. **Premultiply double-application** — The OG SWF stores premultiplied ARGB in format 5 pixels. The decoder demultiplies format 5 back to straight RGBA. The encoder premultiplies again. If the decoder or encoder has an off-by-one or rounding difference, 113 format-5 bitmaps would show tiny diffs. But we see 512 diffs at 96.6% of channels → this is NOT a premultiply rounding issue.

3. **The 512 corrupt bitmaps are ALL format 3 in the OG** — this is the key. Either:
   - The decoded RGBA from format 3 is wrong (decoder bug)
   - The decoded RGBA is correct but gets corrupted during N2D storage/retrieval
   - The buffer in N2D is correct but the compiler reads wrong width/height/data

4. **Quick diagnostic**: Write a script that decodes a single format-3 bitmap from OG, then re-encodes it to format-5 LL2, then decodes the new tag, and compares pixels. This isolates the decode→encode roundtrip from the N2D storage layer.

---

## Files Changed (Current State)

### compile_n2d.py (~L1547-1575)
**Reinstated-based RO2 logic** — reverted from "always RO2" to "only RO2 when reinstated flag is set":
```python
if is_reinstated and dict_changed:
    # OG pattern: remove old then place fresh (new instance)
    remove_buf.extend(build_remove_object2(swf_depth))
    is_move = False
    place_char_id = swf_char_id
elif prev_char != swf_char_id:
    # Different character at same depth — swap in-place
    is_move = True
    place_char_id = swf_char_id
else:
    # Same instance, same char — just update transform
    is_move = True
    place_char_id = None
```
**Status**: Verified — all 190 container sprites match OG RO2 counts.

### server.py (~L196)
Added `soundStreamParsed` to `roundtrip_keys` tuple:
```python
'soundStreamParsed', # SoundStreamHead2 inside sprites
```

### actionscript-panel.js (~L764-770)
Added `soundStreamParsed` to `ROUNDTRIP_LIB_FIELDS` array and `CONTENT_SKIP_KEYS` object.

---

## Verified Correctness (Not the Problem)

| Area | OG vs RT | Status |
|------|----------|--------|
| DoABC bytecode | byte-identical (182,028 bytes) | ✅ |
| SymbolClass | all 185 symbols present and matching | ✅ |
| Sprite count | 190/190 | ✅ |
| Sprite frame counts | all match | ✅ |
| RO2 counts per sprite | all 190 match | ✅ |
| PO2 flags (fox MC) | 0x36 in both (HasChar+HasMatrix+HasRatio+HasName) | ✅ |
| Frame labels | match | ✅ |
| SoundStreamHead2 | present in 190/190 sprites | ✅ |
| FileAttributes | match | ✅ |

---

## Known Differences (Not Yet Causing Issues)

| Difference | OG | RT | Impact |
|------------|----|----|--------|
| Shape tag versions | Mixed (DefShape/2/4) | All DefShape3 | Probably cosmetic |
| Morph tag versions | DefMorphShape | DefMorphShape2 | Probably cosmetic |
| Text tags | DefText | DefEditText | Probably cosmetic |
| CSMTextSettings (tag 74) | Present | Missing | Unknown |
| DefineFontName (tag 88) | Present | Missing | Unknown |
| Bitmap count (editor RT) | 627 | 1506 (explosion) | Only in editor roundtrip |
| Bitmap count (fresh compile) | 627 | 627 | ✅ Matches |

---

## Test Files

- **OG**: `C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf` (1,921,191 bytes)
- **RT**: `C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf` (3,129,025 bytes)

---

## Key Code Locations

| Code | File | Lines | Purpose |
|------|------|-------|---------|
| Bitmap decoder | swf_to_n2d.py | ~2029-2080 | `decode_lossless_to_rgba` — decodes LL/LL2 format 3 and 5 |
| Raw tag storage | swf_to_n2d.py | ~2331, 2390-2446 | `raw_tag_data[cid] = (tag_type, body[2:])` |
| Buffer to N2D | swf_to_n2d.py | ~2881-2884 | Decodes raw_tag_data → RGBA → stored as N2D buffer |
| Bitmap encoder | bitmap_converter.py | 23-90 | `build_define_bits_lossless2` — RGBA → premultiplied ARGB → zlib → tag 36 |
| Bitmap compile | compile_n2d.py | ~2940-2950 | Reads N2D buffer, calls `build_define_bits_lossless2` |
| External bitmap load | compile_n2d.py | ~885-906 | `_load_external_bitmap` — PIL → RGBA → tag 36 |
| Timeline compiler | compile_n2d.py | ~1540-1580 | `build_timeline_tags` — reinstated-based RO2/PO2 logic |
| Server roundtrip | server.py | ~183-200 | `roundtrip_keys` tuple preserving soundStreamParsed |
| JS roundtrip | actionscript-panel.js | ~764-780 | `ROUNDTRIP_LIB_FIELDS` + `CONTENT_SKIP_KEYS` |

---

## Next Steps

1. ~~**Isolate the bitmap corruption**~~ — **DONE**: Decode→encode roundtrip is clean (all 625/625 pass). Pixel data is NOT corrupt.

2. **Root cause found and fixed**: The "corruption" was actually a **bitmap explosion** (627→1506 tags) causing Flash Player memory exhaustion → `Invalid BitmapData` crash.

### The Bug: `bitmapId` Lost During JS Roundtrip

**Shape.js `set recodes`** (line ~293): Converts `{buffer, width, height, bitmapId}` dicts to BitmapData objects but **drops `bitmapId`** — never stored on the BitmapData.

**Shape.js `get recodes`** (line ~262): Converts BitmapData back to dicts but **without `bitmapId`** — always serializes as `bitmapId: 0` (or missing).

**Result**: Every bitmap fill in every shape loses its library reference. The compiler can't resolve `bitmapId=0` to an existing bitmap, so it allocates a **new** DefineBitsLossless2 tag for each bitmap fill occurrence → 879 extra bitmap tags.

### Fixes Applied

1. **Shape.js `get recodes`**: Now emits `"bitmapId": value._$bitmapLibId || 0` in the serialized dict.

2. **Shape.js `set recodes`**: Now stores `value.bitmapId` as `bitmapData._$bitmapLibId` on the BitmapData object.

3. **compile_n2d.py `_resolve_bitmap_fills`**: Added content-hash deduplication. When `bitmap_lib_id=0` (legacy data), hashes pixel data and matches against known bitmap library entries. Falls back to new allocation only for truly novel bitmaps.

4. **compile_n2d.py `_match_bitmap_by_content`**: New method. Lazily builds `(width, height, md5) → SWF charId` cache from all bitmap library entries. O(1) lookup per fill.

### Verified Results

| Metric | Before Fix | After Fix |
|--------|-----------|-----------|
| Bitmap tags in SWF | 1,506 | 627 |
| SWF file size | 3,126,741 bytes | 1,939,543 bytes |
| Pixel integrity | All 625 correct | All 627 correct |

5. **Future**: After the Shape.js fix propagates (next save cycle), the content-hash fallback will no longer be needed — `bitmapId` will be preserved through the JS roundtrip. The dedup remains as a safety net.
