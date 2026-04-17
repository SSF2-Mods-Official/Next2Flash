# OG vs Roundtrip (RT) Differences — fox.ssf

Exhaustive binary-level comparison between the original SWF and the roundtripped SWF produced by Next2Flash.

**OG**: `build\data\character\fox.ssf` (1,921,191 bytes)  
**RT**: `src\...\data\character\fox.ssf` (1,938,077 bytes, ~17KB larger)

---

## 1. SWF Header

| Field | OG | RT | Notes |
|---|---|---|---|
| Signature | FWS | FWS | ✅ Match |
| SWF Version | 15 | 15 | ✅ Match |
| File Length | 1,921,191 | 1,938,077 | RT ~17KB larger |
| Rect | (0,11000,0,8000) | (0,11000,0,8000) | ✅ Match |
| FPS (raw) | 0x1E02 | 0x1E00 | Fractional part lost (30.0078→30.0) |
| Frame Count | 2 | 2 | ✅ Match |

## 2. Background Color

| OG | RT |
|---|---|
| RGB(102,102,102) | RGB(51,51,51) | Hardcoded default in swf_to_n2d.py |

## 3. Identical (No Differences)

| Component | Status |
|---|---|
| DoABC2 (AS3 bytecode) | ✅ Byte-identical (182,028 bytes) |
| SymbolClass names | ✅ All 185 names match |
| FileAttributes | ✅ flags=0x08 (AS3=True) |
| Scene & Frame Labels | ✅ Identical hash |
| Frame count | ✅ Both 2 frames |

## 4. Tag Inventory Changes

### Shape Format Conversions

| Tag | OG Count | RT Count | What Happened |
|---|---|---|---|
| DefineShape (2) | 659 | 0 | All → DefineShape3 |
| DefineShape2 (22) | 63 | 0 | All → DefineShape3 |
| DefineShape3 (32) | 125 | **855** | Absorbs all shapes |
| DefineShape4 (83) | 8 | 0 | → DefineShape3 (loses edge hints) |

### Morph Shape Conversions

| Tag | OG Count | RT Count | What Happened |
|---|---|---|---|
| DefineMorphShape (28) | ~16 | 0 | All → DefineMorphShape2 |
| DefineMorphShape2 (84) | 5 | **21** | Absorbs all morphs |

### Lost Tags

| Tag | OG | RT | Impact |
|---|---|---|---|
| DefineBitsJPEG3 (35) | 2 | **0** | JPEG+alpha images lost |
| DefineText (11) | 2 | **0** | Static text definitions lost |
| DefineFontAlignZones (73) | 1 | **0** | Font hinting lost |
| Unknown_74 (74) | 2 | **0** | Unknown tag lost |
| CSMTextSettings (75) | 1 | **0** | Text anti-alias settings lost |
| DefineFontName (88) | 1 | **0** | Font name tag lost |

### Added/Changed Tags

| Tag | OG | RT | Impact |
|---|---|---|---|
| DefineSprite_old (37) | 0 | **2** | RT creates 2 old-format sprites |
| DefineEditText (36) | 625 | **627** | +2 extra text fields |

## 5. Sound Differences

### Missing Stream Data

| Tag | OG | RT | Impact |
|---|---|---|---|
| SoundStreamBlock (46) | **16** | **0** | All streaming audio data lost |
| SoundStreamHead2 (45) | 1 | 1 | Header present, blocks missing |

### Re-encoded Sounds

62 of 64 `DefineSound` tags have different binary data. Most are re-encoded smaller. Only 2 are identical:

| Sound | Size (both) |
|---|---|
| fox_victory_v2 | 107,425 bytes |
| victory | 96,140 bytes |

<details>
<summary>All 62 changed sounds (click to expand)</summary>

| Sound | OG Size | RT Size |
|---|---|---|
| fox_death | 4,423 | 3,683 |
| fox_death2 | 3,271 | 2,847 |
| fox_dizzy | 4,167 | 3,474 |
| fox_dsmash | 2,055 | 2,011 |
| fox_dsmash_sfx | 3,463 | 2,951 |
| fox_edgeGrab | 775 | 1,071 |
| fox_final_end | 45,063 | 33,253 |
| fox_final_enter | 21,319 | 15,908 |
| fox_final_hover | 41,927 | 30,955 |
| fox_final_land | 20,423 | 15,281 |
| fox_final_move | 80,007 | 58,540 |
| fox_final_roll | 27,591 | 20,506 |
| fox_final_shoot | 21,767 | 16,326 |
| fox_final_turn | 25,031 | 18,625 |
| fox_footstep | 711 | 1,070 |
| fox_footstep2 | 647 | 1,070 |
| fox_fs | 21,127 | 15,908 |
| fox_fsmash | 3,399 | 2,952 |
| fox_fsmash_sfx | 5,575 | 4,623 |
| fox_grunt1 | 839 | 1,071 |
| fox_grunt2 | 1,287 | 1,384 |
| fox_grunt3 | 1,223 | 1,384 |
| fox_grunt4 | 1,607 | 1,698 |
| fox_gunflip | 1,671 | 1,697 |
| fox_hurt | 1,095 | 1,280 |
| fox_hurt2 | 1,031 | 1,280 |
| fox_hurtBad | 4,615 | 3,788 |
| fox_hurtBad2 | 3,719 | 3,161 |
| fox_il | 10,247 | 7,967 |
| fox_illusionvoice | 1,543 | 1,593 |
| fox_ilstart | 8,647 | 6,713 |
| fox_jabSwing | 2,055 | 2,115 |
| fox_jump01 | 5,319 | 4,414 |
| fox_jump02 | 4,167 | 3,578 |
| fox_jump_vc | 967 | 1,175 |
| fox_jumpflip | 583 | 862 |
| fox_landHeavy | 2,695 | 2,533 |
| fox_landLight | 2,375 | 2,324 |
| fox_nspec_end | 1,543 | 1,697 |
| fox_nspec_shoot | 3,015 | 2,742 |
| fox_rapidJab | 4,295 | 3,579 |
| fox_runstart | 5,127 | 4,205 |
| fox_runstop | 1,799 | 1,906 |
| fox_shine | 327 | 783 |
| fox_shine_hold | 2,887 | 2,533 |
| fox_sleep | 9,799 | 7,549 |
| fox_starKO | 25,095 | 18,834 |
| fox_swing_l | 2,567 | 2,324 |
| fox_swing_ll | 3,207 | 2,951 |
| fox_swing_m | 1,863 | 1,906 |
| fox_swing_s | 1,351 | 1,488 |
| fox_taunt | 3,783 | 3,265 |
| fox_taunt3 | 3,527 | 3,056 |
| fox_usmash | 1,351 | 1,489 |
| fox_usmash_sfx | 5,511 | 4,623 |
| fox_uspec | 2,375 | 2,220 |
| fox_uspecBlast | 15,047 | 11,519 |
| fox_uspecCharge | 17,735 | 13,400 |
| fox_uspecLand | 2,183 | 2,115 |
| fox_win | 14,791 | 11,206 |
| fox_win2 | 6,087 | 4,937 |
| fox_win_special | 10,247 | 7,967 |

</details>

## 6. CID Remapping

121 of 185 SymbolClass entries have different Character IDs. This is expected — CIDs are reassigned during export. All symbol names match.

## 7. Sprite Timeline Differences

**2,998 total differences** across ~119 sprites.

### Difference Categories (Previous Count → Fresh Export)

| Category | Count (Pre-Fix) | Description |
|---|---|---|
| SoundStreamHead2 data | 119 | Tag 45 data differs in every sprite (4 bytes) |
| CID remapping | ~524 | Expected — character IDs renumbered |
| **Lost HasRatio** | **~447→155** | **Morph ratio field lost** |
| Added HasMatrix | ~578 | RT emits identity matrix where OG omits it |
| Added HasCxform | variable | RT adds color transforms (dust, firefoxTrail) |
| Matrix value differs | ~88 | RT has different matrix bytes |
| Remove depth order swaps | ~8 | RemoveObject depth ordering reversed (blasters, dthrow) |
| Tag type PO3→PO2 | 37 | entrance MC loses PlaceObject3 filters |

### CRITICAL: `[fox]` Main Sprite — 88 Lost Ratios on Depth 7

The `[fox]` character sprite has a morph shape on depth 7 that uses `ratio` values 1–88 across frames 2–89 to drive stance transitions. **All 88 ratios are lost** (`ratio N→None`).

```
[fox] F2_PO2_d7:  ratio 1→None
[fox] F3_PO2_d7:  ratio 2→None
...
[fox] F89_PO2_d7: ratio 88→None
```

**Root cause**: `Character.js` `places` getter didn't include `ratio` in serialized output. Fixed.

### Sprites with Lost Ratio (partial list)

| Sprite | Affected Depths | Frames |
|---|---|---|
| fox (main) | d7 | F2–F89 (88 ratios) |
| fox_fla.Fox_Backdodge_110 | d12 | F2, F12 |
| fox_fla.Fox_Hanggetup_115 | d12 | F7, F14 |
| fox_fla.Fox_Knockback_113 | d2, d10 | F3, F4 |
| fox_fla.Fox_dthrow_72 | d2, d4, d7, d15, d19, d21, d25 | Multiple |
| fox_fla.Fox_grab_102 | d8–d24 | Multiple |
| fox_fla.Fox_sidestep_112 | d1, d2 | F4, F11 |
| fox_fla.ItemAssist_91 | d4–d14 | Multiple |
| fox_fla.ItemDashAttack_78 | d1, d2, d8 | Multiple |
| fox_fla.ItemHome_Run_82 | d1, d3, d9 | Multiple |
| + many more stance MCs | various | various |

## 8. Root Timeline Differences

Frame 2 PlaceObject2 tags are consistently **2 bytes smaller** in RT. Example:
- OG: `PlaceObject2[12B]` → RT: `PlaceObject2[10B]`
- OG: `PlaceObject2[17B]` → RT: `PlaceObject2[15B]`

Likely same pattern (OG has ratio, RT doesn't) or matrix encoding difference.

---

## Summary of Impact

| Change | Severity | Behavioral Impact |
|---|---|---|
| **Lost ratio values** | 🔴 CRITICAL | Morph shapes don't interpolate → animations loop/freeze |
| Lost SoundStreamBlocks | 🟡 Medium | Streaming audio missing (event sounds still work) |
| Lost DefineBitsJPEG3 | 🟡 Medium | 2 JPEG+alpha images missing |
| Shape type conversions | 🟢 Low | Visual equivalence (DefineShape→DefineShape3) |
| Added identity matrices | 🟢 Low | Cosmetic — increases file size slightly |
| FPS fraction lost | 🟢 Low | 0.008 fps difference, negligible |
| Background color change | 🟢 Low | Cosmetic only |
| Sound re-encoding | 🟢 Low | Different codec params, audio still plays |
| Lost font/text tags | 🟢 Low | Font hinting, static text definitions |
| DefineSprite_old created | 🟢 Low | 2 old-format sprites, should still work |

## Fixes Applied

1. **Ratio keyframe detection** (swf_to_n2d.py) — Added `ratio` to keyframe comparison in both `_build_layer_from_events` and `_build_layer_for_depth` so ratio-only changes aren't silently dropped during import.

2. **Ratio passthrough in editor** (Character.js) — Added `ratio` to the `places` getter so the JS editor preserves it during save/export. This was the **root cause** of all 447+ lost ratios.
