# SWF Roundtrip Unit Test Plan

## What Each Test Does

Every test follows the same 3-step pattern:

1. **Import**: `SWF → N2D` via `swf_to_n2d.N2DBuilder`
2. **Export**: `N2D → SWF` via `compile_n2d.N2DCompiler`
3. **Compare**: Parse both SWFs into tag maps, match definition tags by **tag type + body-after-charID** (since charIDs get renumbered). Verify tag count matches and every original define tag has an identical body in the roundtrip SWF.

## What "Success" Means

A test **passes** when:

- The roundtrip SWF has the **same number** of each definition tag type as the original
- Every definition tag body (bytes after the 2-byte charID) is **byte-identical** after charID reference remapping
- Non-define structural tags (FileAttributes, SetBackgroundColor, DoABC, SymbolClass) are present and structurally valid
- The output SWF passes structural validation (no truncated tags, sprites have End tags)

## What's Expected to Differ (NOT a failure)

- CharID numbers (renumbered sequentially)
- Tag emission order (dependency-sorted, not original order)
- SymbolClass body (rebuilt with new charIDs)
- SWF compression method may change

---

## Test Categories & Individual Tests

### Shapes

| # | Test Name | What It Covers | Input | Success Criteria |
|---|-----------|---------------|-------|-----------------|
| 1 | `test_shape_solid_fills` | DefineShape3 with solid RGB/RGBA fills | synthetic | Tag body match after remap |
| 2 | `test_shape_gradient_fills` | Linear + radial gradient fills | synthetic | Gradient records preserved byte-identical |
| 3 | `test_shape_bitmap_fills` | Bitmap fills (clipped 0x41, tiled 0x40, smoothed 0x42/0x43) | synthetic | BitmapId refs correctly remapped |
| 4 | `test_shape_line_styles` | Line widths, cap styles (round/square/none), join styles (round/bevel/miter) | synthetic | Line style records preserved |
| 5 | `test_shape_curved_edges` | Quadratic Bézier curves | synthetic | Edge records bit-identical |
| 6 | `test_shape4_focal_gradient` | DefineShape4 with focal gradient + edge bounds | synthetic | Tag 83 body match |

### Bitmaps

| # | Test Name | What It Covers | Input | Success Criteria |
|---|-----------|---------------|-------|-----------------|
| 7 | `test_bitmap_lossless_rgb` | DefineBitsLossless (tag 20) format 5 (24-bit) | synthetic | Pixel data preserved after zlib roundtrip |
| 8 | `test_bitmap_lossless2_rgba` | DefineBitsLossless2 (tag 36) format 5 (ARGB) | synthetic | RGBA pixel data preserved |
| 9 | `test_bitmap_lossless_palette` | DefineBitsLossless/2 format 3 (palette) | synthetic | Palette + indices preserved |
| 10 | `test_bitmap_jpeg` | DefineBitsJPEG2 (tag 21) | synthetic | JPEG blob byte-identical |
| 11 | `test_bitmap_jpeg_alpha` | DefineBitsJPEG3 (tag 35) JPEG + alpha | synthetic | JPEG + alpha table preserved |

### Fonts & Text

| # | Test Name | What It Covers | Input | Success Criteria |
|---|-----------|---------------|-------|-----------------|
| 12 | `test_font3_glyphs` | DefineFont3 (tag 75) with glyph shapes + code table | real SWF | Glyph data preserved, aux tags present |
| 13 | `test_font_aux_tags` | FontAlignZones (73), CSMTextSettings (74), DefineFontName (88) | real SWF | Aux tags present with correct charID refs |
| 14 | `test_static_text` | DefineText/DefineText2 (tag 11/33) with glyph records | real SWF | Text records + font refs preserved |
| 15 | `test_edit_text` | DefineEditText (tag 37) with all flags | synthetic | All flags + font ref preserved |

### Movie Clips / Sprites

| # | Test Name | What It Covers | Input | Success Criteria |
|---|-----------|---------------|-------|-----------------|
| 16 | `test_sprite_basic` | DefineSprite (tag 39) with single-frame timeline | synthetic | Sprite body match after PlaceObject remap |
| 17 | `test_sprite_multiframe` | Multi-frame sprite with PlaceObject2, RemoveObject2, ShowFrame | synthetic | Timeline sequence preserved |
| 18 | `test_sprite_nested` | Sprite referencing other sprites (nested containers) | synthetic | Dependency order correct, all charIDs remapped |
| 19 | `test_sprite_frame_labels` | FrameLabel tags inside sprites | synthetic | Label names + frame positions preserved |

### Placement Features

| # | Test Name | What It Covers | Input | Success Criteria |
|---|-----------|---------------|-------|-----------------|
| 20 | `test_place_object2` | PlaceObject2 with matrix, colorTransform, name, clipDepth | synthetic | All PO2 fields match |
| 21 | `test_place_object3_blend` | PlaceObject3 with blend mode | synthetic | Blend mode byte preserved |
| 22 | `test_place_object3_filters` | PlaceObject3 with filter list (blur, glow, drop shadow, bevel, color matrix) | synthetic | Filter binary preserved |
| 23 | `test_move_operations` | PlaceObject2 move (same depth, new transform) | synthetic | Move flag + updated matrix |

### Morph Shapes

| # | Test Name | What It Covers | Input | Success Criteria |
|---|-----------|---------------|-------|-----------------|
| 24 | `test_morph_shape` | DefineMorphShape (tag 46) start/end shapes | real SWF | Start+end shape data preserved |
| 25 | `test_morph_shape2` | DefineMorphShape2 (tag 84) with edge bounds | real SWF | Extended morph body match |

### Sounds

| # | Test Name | What It Covers | Input | Success Criteria |
|---|-----------|---------------|-------|-----------------|
| 26 | `test_sound_mp3` | DefineSound (tag 14) format 2 (MP3) | synthetic | Sound body byte-identical |
| 27 | `test_start_sound` | StartSound (tag 15) trigger in timeline | synthetic | Sound reference + flags preserved |

### ActionScript

| # | Test Name | What It Covers | Input | Success Criteria |
|---|-----------|---------------|-------|-----------------|
| 28 | `test_doabc_passthrough` | DoABC2 (tag 82) raw passthrough | real SWF | ABC bytecode byte-identical |
| 29 | `test_symbol_class` | SymbolClass (tag 76) — charID→class mapping rebuilt | real SWF | Same set of class names, mapped to valid charIDs |

### Global / Structural

| # | Test Name | What It Covers | Input | Success Criteria |
|---|-----------|---------------|-------|-----------------|
| 30 | `test_file_attributes` | FileAttributes (tag 69) AS3 flags | synthetic | Flags match |
| 31 | `test_background_color` | SetBackgroundColor (tag 9) | synthetic | RGB value preserved |
| 32 | `test_protect_tag` | Protect (tag 24) passthrough | real SWF | Tag present if original had it |

### Integration / Real SWFs

| # | Test Name | What It Covers | Input | Success Criteria |
|---|-----------|---------------|-------|-----------------|
| 33 | `test_roundtrip_gameandwatch` | Full roundtrip of `gameandwatch_cli.n2d` | `gameandwatch_cli.n2d` | All define tags match, tag counts match |
| 34 | `test_roundtrip_determinism` | Same N2D compiled 3x produces identical SWF | `gameandwatch_cli.n2d` | Byte-identical output across runs |
| 35 | `test_structural_validation` | Output SWF passes structural checks | any roundtrip output | No truncated tags, sprites have End tags, valid header |

---

## Test Infrastructure (shared utilities)

| Utility | Purpose |
|---------|---------|
| `build_minimal_swf(tags)` | Constructs a valid SWF from a list of `(tag_type, body)` tuples (header + compression + End tag) |
| `parse_swf_tags(path)` | Parses SWF → list of `(tag_type, body)` (reused from `_compare_swf.py` logic) |
| `build_define_tag_map(tags, id_map=None)` | Maps define tags to comparable form: `{(tag_type, internal_identity) → body_after_charID}` |
| `roundtrip(swf_path)` | Full SWF→N2D→SWF, returns paths to both files |
| `assert_define_tags_match(orig_tags, rt_tags)` | Core assertion: same tag types/counts, body comparison after charID normalization |

## Synthetic SWF Construction

For tests 1–11, 15–23, 26–27, 30–31: we build minimal SWFs programmatically using `swf_writer.py` primitives (`build_tag`, `build_swf_file`, `build_place_object2`, etc.) so each test isolates **exactly one feature** without depending on external SWF files.

For tests 12–14, 24–25, 28–29, 32–34: we use existing real SWFs from `converted/` that are known to contain those features.

---

## Not Tested (and why)

| Feature | Reason |
|---------|--------|
| DefineButton (tag 7/34) | Not handled by Python pipeline — JS only |
| DefineVideo | Not handled by either parser |
| SoundStreamBlock (tag 19) | Not handled by Python pipeline |
| DefineScalingGrid (tag 78) | Not handled by Python pipeline |
| DefineFontInfo (tag 13/62) | Python only handles DefineFont3 |
| Legacy DefineFont/Font2 (tag 10/48) | Python only handles DefineFont3 |
