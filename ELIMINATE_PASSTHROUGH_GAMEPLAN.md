# Eliminate All Raw Binary Passthrough — Gameplan

Goal: Every SWF tag is fully parsed into editable structured JSON — no base64 blobs, no
raw byte passthrough. Every piece of data the user could edit in Adobe Animate is exposed
as named fields that the UI can bind to. Raw binary is only acceptable for truly opaque
compiled bytecode (AVM2 ABC, AVM1 actions) and arbitrary user-embedded binary data, and
even those have their SWF tag framing fully parsed away.

Guiding principle: **if Animate has a panel/dialog for it, we have editable fields for it.**

---

## Phase 1 — Publish Settings (project-level tags)

These map to Adobe Animate's **File → Publish Settings** and **Modify → Document** dialogs.

### 1A. Protect (Tag 24)
_Animate: Publish Settings → "Protect from import" checkbox._
**Import**: Store `"protectFromImport": true` at project root.
**Export**: `build_tag(24, b'')` when true (already fallback behavior).
**UI**: Checkbox in a Publish Settings panel or the existing stage-setting panel.
**Remove**: Stop storing tag 24 in `rawGlobalTags`.

### 1B. Metadata (Tag 77)
_Animate: File → Publish Settings → metadata fields (title, description, copyright, etc.)._
**Import**: Parse null-terminated UTF-8 XMP string. Extract `dc:title`, `dc:description`,
`dc:creator` into named fields:
```json
{
  "metadata": {
    "title": "My Animation",
    "description": "A cool animation",
    "creator": "Author Name",
    "rawXml": "<?xml ...full XMP if fields above don't cover it..."
  }
}
```
**Export**: Rebuild XMP XML from fields → `build_tag(77, ...)`.
**UI**: Text inputs in a Publish Settings or Document Properties panel.
**Remove**: Stop storing tag 77 in `rawGlobalTags`.

### 1C. SceneAndFrameLabelData (Tag 86)
_Animate: Scene panel (Window → Scene) for scenes. Properties panel for frame labels
when a keyframe is selected._
**Import**: Parse into:
```json
{
  "scenes": [
    { "name": "Scene 1", "startFrame": 0 }
  ]
}
```
Frame labels are already stored per-frame in the timeline data — this tag is just the
compiled index. Don't duplicate them; rebuild entirely from timeline on export.
**Export**: Enumerate scene offsets + frame labels from timeline → build tag 86.
**UI**: Scene names editable in a Scene panel. Frame labels already editable in timeline.
**Remove**: Stop storing tag 86 in `rawGlobalTags`.

### 1D. SoundStreamHead2 (Tag 45) — global & sprite level
_Animate: Sound layer properties in timeline. When you drag a sound to a keyframe and set
sync to "Stream", Animate creates this tag. Properties panel shows compression, sample
rate, etc._
**Import**: Parse bit-packed fields → store as structured object:
```json
{
  "soundStream": {
    "compression": "mp3",
    "sampleRate": 44100,
    "sampleSize": 16,
    "stereo": true,
    "streamSampleCount": 1764,
    "latencySeek": 0
  }
}
```
At project root for the main timeline, per-container for sprites.
**Export**: Re-pack bits → `build_tag(45, ...)`.
**UI**: Editable in a Sound Properties dialog or timeline sound settings (compression
dropdown, sample rate dropdown, stereo checkbox).
**Remove**: `rawSoundStreamHead` field from container entries. Stop storing tag 45 in
`rawGlobalTags`.

---

## Phase 2 — Font Settings

These map to Adobe Animate's **Text → Font Embedding** dialog and font Properties panel.

### 2A. DefineFontAlignZones (Tag 73)
_Animate: Font Embedding dialog → advanced hinting settings. Not directly user-editable
as individual zones, but controlled by the "Anti-alias for readability" / "Anti-alias for
animation" rendering mode selection._
**Import**: Parse per-glyph zones → store on font entry:
```json
{
  "fontHinting": {
    "tableHint": "thin",
    "zones": [
      { "glyphIndex": 0, "zoneX": 0.0, "zoneSizeX": 1.0, "zoneY": 0.0, "zoneSizeY": 1.0 }
    ]
  }
}
```
**Export**: Re-encode → `build_tag(73, ...)`.
**UI**: Dropdown for hinting mode (thin/medium/thick) on the font entry. Individual zones
are auto-generated, not hand-edited.

### 2B. CSMTextSettings (Tag 74)
_Animate: Text anti-aliasing dropdown — "Anti-alias for readability", "Anti-alias for
animation", "Bitmap text (no anti-alias)", "Use device fonts". Also the custom
thickness/sharpness sliders in the Properties panel._
**Import**: Parse → store on font entry:
```json
{
  "textRendering": {
    "renderer": "advanced",
    "gridFit": "subPixel",
    "thickness": 1.0,
    "sharpness": 40.0
  }
}
```
**Export**: Pack → `build_tag(74, ...)`.
**UI**: Anti-alias mode dropdown + thickness/sharpness sliders in text Properties panel
(or per-font settings).

### 2C. DefineFontName (Tag 88)
_Animate: Font Embedding dialog shows font name. Copyright is embedded metadata from the
TTF/OTF file._
**Import**: Parse two null-terminated strings → store on font entry:
```json
{
  "fontLicense": {
    "displayName": "Arial",
    "copyright": "© Microsoft"
  }
}
```
**Export**: Write strings → `build_tag(88, ...)`.
**UI**: Read-only display in font library entry properties (name + copyright).

**Remove**: The entire `fontAuxTags` base64 array. Replaced by `fontHinting`,
`textRendering`, `fontLicense` structured fields.

---

## Phase 3 — Runtime Shared Libraries

_Animate: Modify → right-click symbol → Properties → Sharing tab. Or File → Publish
Settings → "Runtime Shared Libraries"._

### 3A. ImportAssets / ImportAssets2 (Tags 57 / 71)
**Import**: Parse URL + asset name pairs → store at project root:
```json
{
  "runtimeSharedLibraries": [
    {
      "url": "http://example.com/library.swf",
      "assets": [
        { "name": "Bitmap_Asset", "linkedTo": "LocalBitmapName" },
        { "name": "Sound_Fx", "linkedTo": "LocalSoundName" }
      ]
    }
  ]
}
```
`linkedTo` maps the imported name to a local library entry. Original charIDs are discarded;
new IDs allocated at export based on name matching.
**Export**: Build ImportAssets2 tag from fields.
**UI**: A "Shared Libraries" dialog listing each URL + its imported asset names + local
binding. Add/remove/edit URL and asset mappings.
**Remove**: Stop storing tags 57/71 in `rawGlobalTags`.

### 3B. SymbolClass (Tag 76)
_Animate: Symbol Properties → linkage "Export for ActionScript" class name field._
Already rebuilt from scratch during compilation using per-library-entry `className` fields.
**Remove**: Filter tag 76 out of `rawGlobalTags` on import. Already fully handled.
**UI**: Already supported via the existing "Symbol Name" / class linkage on library entries.

---

## Phase 4 — Buttons

_Animate: Double-click a button symbol to enter its timeline. The timeline shows 4 labeled
frames: Up, Over, Down, Hit. Each frame is a keyframe where you place graphics/clips.
The button actions are set in the Actions panel or via event handlers in AS3._

### 4A. Full parse DefineButton2 (Tag 34)
**Import**: Parse ButtonRecords + ButtonCondActions into an Animate-style state model:
```json
{
  "type": "button",
  "name": "PlayButton",
  "trackAsMenu": false,
  "buttonStates": {
    "up":   [{ "characterId": 234, "depth": 1, "matrix": [1,0,0,1,0,0], "colorTransform": null, "filters": [], "blendMode": "normal" }],
    "over": [{ "characterId": 235, "depth": 1, "matrix": [1,0,0,1,0,0], "colorTransform": null, "filters": [], "blendMode": "normal" }],
    "down": [{ "characterId": 235, "depth": 1, "matrix": [1.05,0,0,1.05,-2,-2], "colorTransform": null, "filters": [], "blendMode": "normal" }],
    "hit":  [{ "characterId": 236, "depth": 1, "matrix": [1,0,0,1,0,0], "colorTransform": null, "filters": [], "blendMode": "normal" }]
  },
  "buttonActions": [
    {
      "conditions": ["overDownToOverUp"],
      "actionBytes": "base64_avm1_bytecode"
    }
  ]
}
```
Each ButtonRecord's state bitfield is unpacked into the 4 named states (a record can
appear in multiple states — e.g. same shape for Up and Over). `actionBytes` stays as
base64 for AVM1 bytecode (same as Animate — you can't edit compiled AVM1 visually).

**Export**: Rebuild tag 34 — merge state arrays back into ButtonRecords (deduplicate
records that appear in multiple states), pack matrices/cxforms/filters bit-by-bit.

**UI — Button Editor**:
- Double-click button in library → opens a 4-frame timeline (Up/Over/Down/Hit)
- Each frame shows placed objects with the existing transform/color/filter panels
- Drag library items onto each state frame to assign graphics
- Hit state shown as semi-transparent overlay
- `trackAsMenu` checkbox in Properties
- AVM1 actions shown read-only (or editable if we add an AVM1 decompiler later)

### 4B. Button Sounds (Tag 17)
_Animate: Button symbol → each state can have an attached sound. Set in the Sound section
of Properties when a button state keyframe is selected._
**Import**: Parse DefineButtonSound → per-state sound assignments:
```json
{
  "buttonSounds": {
    "overUpToOverDown": { "soundId": 10, "soundInfo": { "syncStop": false, "syncNoMultiple": false, "hasEnvelope": false, "hasLoops": false, "hasOutPoint": false, "hasInPoint": false } },
    "overDownToOverUp": { "soundId": 12, "soundInfo": { "syncStop": false, "syncNoMultiple": true } }
  }
}
```
**Export**: Rebuild tag 17 from fields.
**UI**: Sound dropdown per button state (Up→Over, Over→Down, etc.).
**Remove**: `buttonData`, `buttonAuxTags`, `rawTagBody` from button entries.

---

## Phase 5 — Static Text (DefineText / DefineText2)

_Animate: Select static text on stage → Properties panel shows font, size, color,
letter spacing, auto-kern, position. The text content is editable inline on stage.
Static text embeds glyphs — you can't change the font without re-embedding._

### 5A. Full parse (Tags 11 / 33)
**Import**: Convert glyph indices back to actual characters using the referenced font's
glyph table (CodeTable from DefineFont). Store as human-readable, editable text:
```json
{
  "type": "text",
  "staticText": true,
  "textRuns": [
    {
      "text": "Hello World",
      "fontId": 12,
      "fontName": "Arial",
      "color": [255, 0, 0, 255],
      "size": 24,
      "xOffset": 0,
      "yOffset": 0,
      "letterSpacing": [12, 10, 8, 8, 10, 6, 14, 10, 8, 8, 10]
    }
  ],
  "bounds": { "xMin": 0, "xMax": 2000, "yMin": 0, "yMax": 400 },
  "matrix": [1, 0, 0, 1, 100, 50]
}
```
Key difference from old plan: glyph indices are resolved to actual text characters using
the font's CodeTable. `letterSpacing` is an array of per-glyph advance values that
preserves exact spacing. This makes the text readable and editable in the UI.

If the user edits the text string, on export we look up new glyph indices from the font's
CodeTable. Characters not in the font's embedded set trigger a warning.

**Export**: For each textRun, look up glyph indices from the font's CodeTable, compute
glyphBits/advanceBits, pack TextRecords. Remap fontId to new charID.

**UI — Text Editing (mirrors Animate)**:
- Click static text on stage → see the actual text in an editable field
- Properties panel: font (dropdown from available embedded fonts), size, color,
  letter spacing (uniform adjustment or keep per-glyph from import)
- Inline on-stage text editing like Animate's text tool
- Per-run color/font changes (multiple TextRecords = multiple runs)
- Warning indicator when edited text uses characters not in the embedded font

### 5B. Replace remap functions
Delete `_remap_text_raw_body()`. Replace with `_build_text_tag()` that constructs the
binary from structured fields + font CharID lookup.

**Remove**: `rawTagBody`, `rawTagType` from text entries.

---

## Phase 6 — ActionScript / Bytecode

_Animate: Actions panel (Window → Actions) for frame scripts. AS3 class files in the
source project. Code is edited as text and compiled by the IDE on publish._

### 6A. DoABC / DoABC2 (Tags 72 / 82)
**Import**: Parse the tag wrapper, store ABC bytecode separately:
```json
{
  "abcBlocks": [
    {
      "tagVersion": 2,
      "flags": 1,
      "name": "frame1",
      "bytecode": "base64_abc_only",
      "extractedClasses": ["Main", "com.app.Helper", "com.app.GameEngine"],
      "extractedFrameScripts": {
        "MainTimeline": { "0": "stop();" },
        "EnemyClip": { "0": "gotoAndPlay('idle');" }
      }
    }
  ]
}
```
`bytecode` is the ABC file bytes only (no SWF tag header/framing). This is compiled
bytecode — it's the equivalent of a .class file in Java. You don't edit bytecode.

`extractedClasses` and `extractedFrameScripts` are **read from** the ABC constant pool
and addFrameScript() patterns during import. These are what the ActionScript panel
displays. When the user edits frame scripts and recompiles, the entire `bytecode` blob
is replaced by the mxmlc compiler output.

**Export**: Rebuild DoABC2 = flags(U32) + name(NUL-terminated) + bytecode → `build_tag(82, ...)`.
**UI**: Already handled — ActionScript panel shows decompiled frame scripts, user edits
AS3 source, recompilation replaces the bytecode blob.
**Remove**: Tags 72/82 from `rawGlobalTags`. Stored as `"abcBlocks"` at project root.

### 6B. AVM1 bytecode (Tags 12, 59)
_DoAction (12), DoInitAction (59) — legacy AS1/AS2._
Same approach: store as `"avm1Blocks"` with extracted action summaries for display.
Bytecode blob stays base64 since AVM1 is compiled. A future AVM1 decompiler could
make these editable as source text.
**Remove**: From `rawGlobalTags`.

---

## Phase 7 — Binary Data Embeds

_Animate: Right-click in Library → New Symbol → set "Export for ActionScript" and embed
data via [Embed] metadata. Not directly editable in Animate — just a named blob._

### 7A. DefineBinaryData (Tag 87)
**Import**: Store content bytes (after charID + reserved) with a name:
```json
{
  "type": "binaryData",
  "name": "config_data",
  "className": "ConfigData",
  "dataSize": 4096,
  "dataBody": "base64_content_bytes"
}
```
`dataBody` is the **content only** (not the SWF tag wrapper). This is inherently opaque
user data — Animate doesn't let you edit it either. But we surface the name, class
linkage, and size so it shows up in the library panel.

**Export**: `build_tag(87, pack('<HI', swf_id, 0) + decode_b64(dataBody))`.
**UI**: Library shows it as a named binary asset with size. Double-click shows hex preview
or "Binary Data — X bytes" info. Name and class linkage are editable.
**Remove**: `binaryDataBody` / `rawTagBody` → `dataBody` + `className`.

---

## Phase 8 — Cleanup & Migration

### 8A. Remove `rawGlobalTags` entirely
Nothing writes to it after phases 1–7. Remove:
- `self.global_raw_tags` in `swf_to_n2d.py`
- `result['rawGlobalTags']` serialization
- `rawGlobalTags` handling in `compilation_pipeline.py` (`ParseRawTagsStage`)
- `rawGlobalTags` in `actionscript-panel.js`

### 8B. Remove all raw binary fields
- `rawTagBody`, `rawTagType` — from text, button, binary data entries
- `buttonData`, `buttonAuxTags` — from button entries
- `fontAuxTags` — from font entries
- `rawSoundStreamHead` — from container entries
- `binaryDataBody` — replaced by `dataBody`
- `_decode_raw_body()` helpers in `compile_n2d.py` and `compilation_pipeline.py`
- `_remap_text_raw_body()`, `_remap_button_raw_body()`, `_remap_sprite_raw_body()`
  (replaced by field-based builders)

### 8C. Update JS side
- `actionscript-panel.js`: Read/write `abcBlocks` instead of `rawGlobalTags`
- Library panel: Display new structured fields (button states, font settings, etc.)
- Export/save: Preserve all new structured fields

### 8D. Migration for old N2D files
Add a one-time migration in `server.py` that detects old-format N2D files (containing
`rawGlobalTags` / `rawTagBody`) and parses them into the new structured format on load.
This keeps backward compat without maintaining dual code paths.

---

## Execution Order

| # | Phase | What it enables (Animate parity) | Depends On |
|---|-------|--------------------------------|------------|
| 1 | Publish Settings (Protect, Metadata, Scenes, Sound Stream) | Document Properties, Scene panel, Sound layer config | — |
| 2 | Font Settings (AlignZones, CSM, FontName) | Font Embedding dialog, anti-alias settings, text rendering | — |
| 3 | Shared Libraries (ImportAssets, SymbolClass) | Runtime Shared Library dialog, symbol linkage | — |
| 4 | Buttons (DefineButton2, ButtonSound) | Button symbol 4-state editor, per-state sounds | — |
| 5 | Static Text (DefineText/Text2) | On-stage text editing, Properties panel for static text | 2 (needs font CodeTable) |
| 6 | ActionScript (DoABC, DoAction) | Actions panel, frame script editing, recompilation | — |
| 7 | Binary Data | Library display of embedded assets | — |
| 8 | Cleanup + migration | Remove all raw fields, migrate old files | 1–7 |

---

## What stays as base64 (and why — same as Animate)

| Data | Why | Animate equivalent |
|------|-----|--------------------|
| ABC bytecode in `abcBlocks[].bytecode` | Compiled AVM2 — edited as AS3 source, recompiled by mxmlc | You edit .as files, IDE compiles |
| AVM1 actions in `buttonActions[].actionBytes` | Compiled AVM1 — no source available from SWF | Animate doesn't decompile either |
| AVM1 blocks in `avm1Blocks[].bytecode` | Same as above | Same |
| Binary embed in `dataBody` | User's arbitrary data — opaque by design | [Embed] asset, not editable |

Everything else is fully parsed, named, and editable.

---

## Validation

After each phase:
1. Import a test SWF → verify no raw fields remain for that tag type
2. Export back to SWF → open in Ruffle/Flash Player, verify identical behavior
3. Edit a field in the UI → re-export → verify the edit took effect
4. Run `test_roundtrip_text.py` and `test_import_validation.py`
5. Compare: can you do in Next2Flash what you could do in Animate for that feature?
