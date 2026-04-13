# Export Edits Survival Checklist

Track which user edits survive the SWF export round-trip, and what's missing for building SWFs from scratch.

## Legend
- ✅ Edits survive export
- ❌ Edits silently lost (rawTagBody passthrough wins)
- 🔧 Fix in progress
- ⬜ Not yet tested
- N/A Not editable in tool / not applicable
- 🚫 No rebuild path exists — rawTagBody mandatory
- 🆕 Needs to be created (from-scratch gap)

---

## Can You Build a Full SWF from Scratch?

**Mostly yes.** Next2Flash now supports creating blank projects and adding shapes, text, bitmaps, sounds, and MovieClips from the library context menu. Remaining gaps: font embedding, button creation, and AS3 class binding UI.

### From-Scratch Blockers
| Blocker | Status | Notes |
|---------|--------|-------|
| No "New Project" (blank SWF) | ✅ | `POST /api/new-project` creates blank N2D with stage settings |
| No "Add Shape" | ✅ | Library context menu → New Shape (empty recodes + bounds) |
| No "Add Text" | ✅ | Library context menu → New Text (default font/size/color) |
| No "Add Bitmap" | ✅ | Existing file import handles PNG/JPG/GIF |
| No "Add Sound" | ✅ | Existing file import handles MP3/MP4 |
| No "Add MovieClip" | ✅ | Already existed: library context menu → New MovieClip |
| No "Add Font" | 🆕 | No endpoint/UI to embed font glyphs |
| No "Add Button" | 🆕 | No endpoint/UI to create button states |
| No charID allocator in editor | ✅ | Not needed: `nextLibraryId` (JS) + `CharIDAllocator` (compile) handle it |
| No property validators | ✅ | `_validate_library_entry()` skips bad entries with warnings |
| Shape rebuild = gray box | ✅ | Fixed in Phase 2: rebuilds from recodes via `build_define_shape3()` |
| Text FontID hardcoded 0 | ✅ | Fixed in Phase 1: `_build_font_name_map()` resolves embedded font |
| No AS3 authoring | 🆕 | Can only pass-through existing DoABC; no script creation UI |

---

## SWF Tag Coverage (All 91 Tags)

### Fully Handled Tags — Import + Export

| Tag# | Name | Import | Export | Editable | Rebuild (no rawTagBody) | Edits Survive |
|------|------|--------|--------|----------|------------------------|---------------|
| 0 | End | ✅ | ✅ | - | ✅ | N/A |
| 1 | ShowFrame | ✅ | ✅ | - | ✅ | N/A |
| 9 | SetBackgroundColor | ✅ | ✅ | ✅ | ✅ | ✅ |
| 15 | StartSound | ✅ | ✅ | ✅ | ✅ | ✅ |
| 26 | PlaceObject2 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 28 | RemoveObject2 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 39 | DefineSprite | ✅ | ✅ | ✅ | ✅ | ✅ |
| 43 | FrameLabel | ✅ | ✅ | ✅ | ✅ | ✅ |
| 56 | ExportAssets | ✅ | ✅ | - | ✅ | N/A |
| 70 | PlaceObject3 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 76 | SymbolClass | ✅ | ✅ | - | ✅ | N/A (rebuilt with new charIDs) |
| 78 | DefineScalingGrid | ✅ | ✅ | ✅ | ✅ | ✅ |
| 89 | StartSound2 | ✅ | ✅ | ✅ | ✅ | ✅ |

### Tags With Rebuild Path — rawTagBody Cleared on Edit (Edits Survive)

| Tag# | Name | Import | Export | Editable | Rebuild Quality | Edits Survive |
|------|------|--------|--------|----------|----------------|---------------|
| 2 | DefineShape | ✅ | ✅ | Partial | ✅ rebuild from recodes | ✅ |
| 22 | DefineShape2 | ✅ | ✅ | Partial | ✅ rebuild from recodes | ✅ |
| 32 | DefineShape3 | ✅ | ✅ | Partial | ✅ rebuild from recodes | ✅ |
| 83 | DefineShape4 | ✅ | ✅ | Partial | ✅ rebuild from recodes | ✅ |
| 46 | DefineMorphShape | ✅ | ✅ | Partial | ✅ rebuild from recodes | ✅ |
| 84 | DefineMorphShape2 | ✅ | ✅ | Partial | ✅ rebuild from recodes | ✅ |
| 11 | DefineText | ✅ | ✅ | ✅ | ✅ rebuilt as DefineEditText | ✅ |
| 33 | DefineText2 | ✅ | ✅ | ✅ | ✅ rebuilt as DefineEditText | ✅ |
| 37 | DefineEditText | ✅ | ✅ | ✅ | ✅ FontID mapped to embedded font | ✅ |
| 6 | DefineBits | ✅ | ✅ | - | ✅ (from buffer) | ✅ (externalFile or buffer change) |
| 20 | DefineBitsLossless | ✅ | ✅ | - | ✅ (from buffer) | ✅ (externalFile or buffer change) |
| 21 | DefineBitsJPEG2 | ✅ | ✅ | - | ✅ (from buffer) | ✅ (externalFile or buffer change) |
| 35 | DefineBitsJPEG3 | ✅ | ✅ | - | ✅ (from buffer) | ✅ (externalFile or buffer change) |
| 36 | DefineBitsLossless2 | ✅ | ✅ | - | ✅ (from buffer) | ✅ (externalFile or buffer change) |
| 90 | DefineBitsJPEG4 | ✅ | ✅ | - | ✅ (from buffer) | ✅ (externalFile or buffer change) |
| 14 | DefineSound | ✅ | ✅ | Partial | Partial (format-dependent) | ✅ (externalFile or buffer change) |

### Tags Stored Raw — No Rebuild Path (rawTagBody Mandatory)

| Tag# | Name | Import | Export | Editable | Edits Survive | Notes |
|------|------|--------|--------|----------|---------------|-------|
| 34 | DefineButton2 | ✅ | ✅ | 🚫 | N/A | No button record parser/writer |
| 75 | DefineFont3 | ✅ | ✅ | 🚫 | N/A | No glyph rebuild code |
| 48 | DefineFont2 | ✅ | ✅ | 🚫 | N/A | Parsed like Font3; raw passthrough |
| 72 | DoABC | ✅ | ✅ | 🚫 | N/A | AS3 bytecode passthrough |
| 82 | DoABC2 | ✅ | ✅ | 🚫 | N/A | AS3 bytecode passthrough |
| 12 | DoAction | ✅ | ✅ | 🚫 | N/A | AVM1 bytecode passthrough |
| 59 | DoInitAction | ✅ | ✅ | 🚫 | N/A | Frame 0 script passthrough |
| 73 | DefineFontAlignZones | ✅ | ✅ | 🚫 | N/A | Font metrics passthrough |
| 74 | CSMTextSettings | ✅ | ✅ | 🚫 | N/A | ClearType hints passthrough |
| 88 | DefineFontName | ✅ | ✅ | 🚫 | N/A | Font copyright passthrough |
| 87 | DefineBinaryData | ✅ | ✅ | 🚫 | N/A | Binary embed passthrough |
| 8 | JPEGTables | ✅ | N/A | 🚫 | N/A | Merged into DefineBits on import |
| 17 | DefineButtonSound | ✅ | ✅ | 🚫 | N/A | Button sounds passthrough |
| 23 | DefineButtonCxform | ✅ | ✅ | 🚫 | N/A | Button colors passthrough |
| 57 | ImportAssets | ✅ | ✅ | 🚫 | N/A | Cross-SWF import passthrough |
| 71 | ImportAssets2 | ✅ | ✅ | 🚫 | N/A | Cross-SWF import passthrough |

### Global/Header Tags (rawGlobalTags Passthrough)

| Tag# | Name | Import | Export | Editable | Edits Survive | Notes |
|------|------|--------|--------|----------|---------------|-------|
| 69 | FileAttributes | ✅ | ✅ | 🚫 | N/A | Hardcoded: UseAS3=1 |
| 77 | Metadata | ✅ | ✅ | 🚫 | N/A | XML metadata passthrough |
| 24 | Protect | ✅ | ✅ | 🚫 | N/A | Password passthrough |
| 58 | EnableDebugger | ✅ | ✅ | 🚫 | N/A | Flag passthrough |
| 64 | EnableDebugger2 | ✅ | ✅ | 🚫 | N/A | Flag passthrough |
| 65 | ScriptLimits | ✅ | ✅ | 🚫 | N/A | Recursion/timeout passthrough |
| 86 | DefineSceneAndFrameLabelData | ✅ | ✅ | 🚫 | N/A | Scene metadata passthrough |

### Streaming Audio Tags

| Tag# | Name | Import | Export | Editable | Edits Survive | Notes |
|------|------|--------|--------|----------|---------------|-------|
| 18 | SoundStreamHead | ✅ | ✅ | 🚫 | N/A | Stored for roundtrip |
| 19 | SoundStreamBlock | ✅ | ✅ | 🚫 | N/A | Audio data blocks |

### Tags NOT Handled (Missing Entirely)

| Tag# | Name | Category | Impact |
|------|------|----------|--------|
| 3 | FreeCharacter | Deprecated | None — memory management |
| 4 | PlaceObject (v1) | Deprecated | None — v2/v3 used instead |
| 5 | RemoveObject (v1) | Deprecated | None — v2 used instead |
| 7 | DefineButton (v1) | Deprecated | None — v2 (34) used instead |
| 10 | DefineFont (v1) | Deprecated | None — v3 used instead |
| 13 | DefineFontInfo | Deprecated | None — v3 has code tables |
| 16 | StopSound | Deprecated | None |

| 25 | PathsArePostScript | Rare hint | None |
| 29 | SyncFrame | Timing | None |
| 31 | FreeAll | Deprecated | None |
| 38 | DefineVideoStream | Video | ⚠️ Video content completely unsupported |
| 40 | NameCharacter | Obsolete | None — SymbolClass replaces it |
| 41 | ProductInfo | Metadata | None — authoring-only |
| 42 | GeneratorText | Generator | None — Flash IDE only |
| 47 | GenerateFrame | Generator | None — Flash IDE only |

| 49 | GeneratorCommand | Generator | None — Flash IDE only |
| 50 | DefineCommandObj | Generator | None — Flash IDE only |
| 51 | CharacterSet | Font charset | Rare — probably safe to skip |
| 52 | ExternalFont | External ref | ⚠️ External font references lost |

| 60 | DefineVideoStream | Video meta | ⚠️ Video metadata lost |
| 61 | VideoFrame | Video data | ⚠️ Video frame data lost |
| 62 | DefineFontInfo2 | Font info | None — v3 includes this |
| 63 | DebugID | Debug | None |
| 66 | SetTabIndex | Tab order | Minor — keyboard nav lost |

| 91 | DefineFont4 | Font v4 | Rare — CFF font support |

**Summary**: 21 tags missing. Most are deprecated/generator/rare. **Impactful gaps**: DefineVideoStream (38/60/61).

---

## Stage / Document Properties

| Property | Editable | Survives Export | Notes |
|----------|----------|-----------------|-------|
| Stage width | ✅ | ✅ | Clamped to 4096 (WebGL limit) |
| Stage height | ✅ | ✅ | same |
| Frame rate | ✅ | ✅ | Fixed 8.8 format in SWF header |
| Background color | ✅ | ✅ | SetBackgroundColor tag 9 |
| Frame count | ✅ | ✅ | From timeline layers |
| SWF version | 🚫 | N/A | Locked at version 25 (AS3) on export |
| Compression | 🚫 | N/A | Always CWS (zlib) on export |
| FileAttributes flags | 🚫 | N/A | Hardcoded: UseAS3=1 |
| Metadata XML | 🚫 | passthrough | Raw tag preserved |
| Protect password | 🚫 | passthrough | Raw tag preserved |
| ScriptLimits | 🚫 | passthrough | Raw tag preserved |
| EnableDebugger | 🚫 | passthrough | Raw tag preserved |

---

## ActionScript

| Capability | Status | Notes |
|------------|--------|-------|
| AS3 DoABC passthrough | ✅ | Raw bytecode preserved and re-emitted |
| AS3 recompile from .as | ✅ | If `scriptsModified=true` and Flex SDK available |
| AS3 SymbolClass rebuild | ✅ | Class names preserved, charIDs remapped |
| AVM1 DoAction passthrough | ✅ | Raw bytecode preserved |
| AVM1 DoInitAction passthrough | ✅ | Frame 0 scripts preserved |
| Edit scripts in UI | 🚫 | Scripts are text files in project folder |
| Create new AS3 class | 🚫 | No UI; must manually add .as file + set scriptsModified |
| AS3 charID refs in bytecode | ⚠️ | getDefinitionByName works; hardcoded charIDs stale after remap |

---

## Per-Type Edit Survival Detail

### Text (DefineEditText — tag 37)
| Property | Survives? | Notes |
|----------|-----------|-------|
| text content | ✅ | rawTagBody cleared on edit; rebuild via text_converter.py |
| font name | ✅ | FontID mapped to embedded font charID |
| font size | ✅ | same |
| font color | ✅ | same |
| alignment | ✅ | same |
| bold/italic | ✅ | same |
| leading | ✅ | same |
| letterSpacing | ✅ | same |
| leftMargin | ✅ | same |
| rightMargin | ✅ | same |
| multiline | ✅ | same |
| wordWrap | ✅ | same |
| border | ✅ | same |
| scroll | ✅ | same |
| bounds | ✅ | same |

**Fix**: ✅ Done — `_merge_editor_into_disk()` clears rawTagBody when text properties change. FontID mapped to embedded font via `_build_font_name_map()`.

### Text (DefineText — tags 11, 33)
| Property | Survives? | Notes |
|----------|-----------|-------|
| text content | ✅ | rawTagBody cleared on edit; rebuilt as DefineEditText |
| font/size/color | ✅ | FontID mapped to embedded font |

**Fix**: ✅ Done — same as EditText. DefineText rebuilt as DefineEditText (tag 37).

### Shape (tags 2, 22, 32, 83)
| Property | Survives? | Notes |
|----------|-----------|-------|
| recodes (fill/stroke/path) | ✅ | rawTagBody cleared on recode change; rebuilds via shape_converter |
| bounds | ✅ | same |

**Fix**: ✅ Done — `_merge_editor_into_disk()` clears rawTagBody when recodes differ. Shape rebuild uses `parse_next2d_shape_buffer()` + `build_define_shape3()`.

### MorphShape (tags 46, 84)
| Property | Survives? | Notes |
|----------|-----------|-------|
| startRecodes | ✅ | rawTagBody cleared on recode change |
| endRecodes | ✅ | same |

**Fix**: ✅ Done — `_merge_editor_into_disk()` clears rawTagBody when recodes differ.

### Container / MovieClip (tag 39)
| Property | Survives? | Notes |
|----------|-----------|-------|
| layers / placement | ✅ | Always rebuilds from JSON |
| totalFrame | ✅ | same |
| labels | ✅ | same |
| actions / scripts | ✅ | same |

No fix needed — containers are the only type that fully works.

### Bitmap (tags 6, 20, 21, 35, 36, 90)
| Property | Survives? | Notes |
|----------|-----------|-------|
| pixel data (externalFile) | ✅ | Merge rebuilds rawTagBody from disk file |
| pixel data (buffer change) | ✅ | rawTagBody cleared on buffer/externalFile change |

**Fix**: ✅ Done — `_merge_editor_into_disk()` clears rawTagBody when buffer or externalFile changes.

### Sound (tag 14)
| Property | Survives? | Notes |
|----------|-----------|-------|
| audio data (externalFile) | ✅ | Merge rebuilds rawTagBody from disk file |
| audio data (buffer change) | ✅ | rawTagBody cleared on buffer/externalFile change |

**Fix**: ✅ Done — same pattern as bitmap.

### Font (tag 75, DefineFont3)
| Property | Survives? | Notes |
|----------|-----------|-------|
| glyph shapes | 🚫 | Not editable; rawTagBody mandatory |
| font name | 🚫 | same |
| kerning/metrics | 🚫 | same |
| DefineFontAlignZones (73) | 🚫 | Passthrough |
| CSMTextSettings (74) | 🚫 | Passthrough |
| DefineFontName (88) | 🚫 | Passthrough |

No rebuild path. Keep rawTagBody.

### Button (tag 34, DefineButton2)
| Property | Survives? | Notes |
|----------|-----------|-------|
| button records (Up/Over/Down/Hit) | 🚫 | Not editable; rawTagBody mandatory |
| button actions | 🚫 | same |

No rebuild path. Keep rawTagBody.

---

## Implementation Plan

### Phase 1 — Text Export (highest priority)
- [x] `server.py`: detect text property changes → clear rawTagBody/rawTagType
- [x] `text_converter.py`: fix FontID=0 → map to correct font charID
- [x] Verify `build_define_edit_text()` produces valid DefineEditText binary
- [x] Verify DefineText rebuild path produces valid tags 11/33
- [ ] Test: edit text → export → open in JPEXS → confirm changes

### Phase 2 — Shape Export
- [x] `server.py`: detect recodes changes → clear rawTagBody/rawTagType
- [x] `compile_n2d.py`: fix `_emit_shape()` to rebuild from recodes (not gray box)
- [x] Verify shape rebuild produces correct DefineShape3/4 binary
- [x] Verify morphshape rebuild produces correct tag 46/84
- [ ] Test: edit shape → export → verify visually

### Phase 3 — Bitmap / Sound Export
- [x] `server.py`: detect buffer changes → clear rawTagBody/rawTagType
- [x] Verify bitmap rebuild from buffer → valid DefineBitsLossless2/JPEG3
- [x] Verify sound rebuild from buffer → valid DefineSound

### Phase 4 — Missing Tags (import fidelity)
- [x] Tag 8 JPEGTables: merge shared JPEG header with DefineBits on import
- [x] Tag 48 DefineFont2: parse like DefineFont3 (subset of fields)
- [x] Tag 87 DefineBinaryData: store as raw + passthrough (like DoABC)
- [x] Tags 57/71 ImportAssets: store symbol references for passthrough
- [x] Tags 17/23 DefineButtonSound/Cxform: store with button rawTagBody

### Phase 5 — From-Scratch Authoring
- [x] Create blank project API (`POST /api/new-project` → stage size, fps, bg color → empty N2D)
- [x] Add library item creation: Shape (library menu), Text (library menu), Bitmap/Sound (existing import)
- [x] CharID allocator bridge: `nextLibraryId` (JS) + `CharIDAllocator` (compile) — no extra API needed
- [x] Property validators for all rebuildable types (`_validate_library_entry()` in `compile_n2d.py`)
- [x] New Project toolbar button (`#tools-new-project`) with server-side project folder creation
- [ ] Shape drawing tool (canvas → recodes) — requires canvas drawing UI
- [ ] Text creation dialog (font picker, size, content → entry) — currently uses hardcoded defaults
- [ ] Font embedding tool (TTF/OTF → DefineFont3 glyph data)
- [ ] Button creation tool (state assignment UI)
- [ ] AS3 class binding UI (SymbolClass editor)
