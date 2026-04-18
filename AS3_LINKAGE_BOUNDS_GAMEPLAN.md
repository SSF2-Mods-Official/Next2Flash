# AS3 Intent Preservation and Full Recompile Gameplan

## Why This Plan Exists

Current behavior can lose original AS3 intent and occasionally keep stale linkage-generated defaults (for example `bm_dairHand` still exporting `5,5` after dimensions changed).

Two specific intent problems must be fixed:

1. Frame-script intent is not preserved:
- Code that originally lived in FLA frame actions should export back as frame actions.

2. Linkage-script intent is not preserved:
- AS3 classes that exist only because of linkage (e.g. `BitmapData` subclasses) should be regenerated from linkage metadata, not reused from old raw bytecode.

## Product Direction (explicit)

Adopt a full decompile/recompile model for AS3 export.

- No raw DoABC passthrough fallback.
- Always compile from normalized project script model.
- Preserve script origin intent via explicit markers and export routing.
- Keep authoring surface FLA-faithful:
  - linkage classes are not persisted as user-visible external scripts
  - frame-derived script code stays in timeline/frame editing model

Absolute compile policy:

- Raw DoABC passthrough is never allowed.
- No conditional passthrough gate (for example, not tied to `scriptsModified` or dimension flags).
- Every export compiles from normalized source/intent model.

## FLA-Faithful Authoring Rules

The project editing model should mirror how FLA behaves, not how decompiled AS3 files look.

1. Linkage-generated classes
- These should not exist as persistent external scripts in project authoring state.
- They are synthetic export artifacts generated only during export/compile.

2. Decompiled frame-script aggregates
- If import produces large decompiled class files that were originally composed from frame actions, they should be normalized back into timeline/frame script ownership.
- They should be editable in Next2Flash frame/script UI, not treated as standalone external class source files.

3. External class-source files
- Keep only scripts that were truly class-source intent (project code files), not synthetic linkage or frame-aggregate artifacts.

## Target Script Model

Introduce explicit script-origin metadata in project data:

- `scriptOrigin: "frame"`
  - means script is tied to a timeline frame action.

- `scriptOrigin: "linkage-generated"`
  - means script is generated from linkage metadata at export time only.
  - should not be persisted as editable external script content.

- `scriptOrigin: "class-source"`
  - means user-authored class source file.

- `scriptOrigin: "imported-doabc"`
  - optional for traceability only; never used directly for export.

Storage intent:

- `frame` and `class-source` are authoring-time editable entities.
- `linkage-generated` is compile-time synthetic and non-persistent in external script surface.

Additional recommended fields:

- `ownerType`: `frame | library | class`
- `ownerId`: frame/library/class id
- `exportPolicy`: `regenerate | compile-source`

## Export Rules (Intent-First)

1. `frame` origin
- Emit as frame action on the original frame/timeline target.
- Do not convert into standalone class unless user explicitly migrates it.

2. `linkage-generated` origin
- Generate code only during export.
- Do not rely on stored external script bodies for these classes.
- For linked bitmap classes, constructor defaults come from current library width/height.

3. `class-source` origin
- Compile from project source as normal class.

4. `imported-doabc` origin
- Treated as historical provenance only.
- Must be decompiled into one of the three exportable origins above before export.

5. Authoring cleanup
- Any script normalized into `frame` origin should be removed from external script file surface.
- Any script normalized into `linkage-generated` should not be emitted as editable external source.

## Phased Implementation Plan

### Phase 1: Remove Passthrough From Compile Policy ✅ DONE

- [x] Delete/disable raw DoABC passthrough branches in compile pipeline.
- [x] Enforce single path: compile from normalized script model.
- [x] Missing SDK now raises hard error for AS3 projects.
- [x] Projects with no non-root exported symbols skip AS3 compilation (test safety).
- [ ] Add startup compile log: `AS3 mode: full-recompile`

### Phase 2: Add Intent Markers 🔄 IN PROGRESS

- [ ] Add `scriptOrigin` field to script structures (`frame` / `linkage-generated` / `class-source`).
- [ ] Add normalization pass on import (`normalize_imported_scripts`):
  - [ ] Detect and drop linkage-generated stubs (simple `extends BitmapData/Sound/MovieClip`, constructor = super() only).
  - [ ] Detect `*_fla` package frame-aggregate classes; extract frame bodies → inject into matching container `lib.actions`.
  - [ ] Tag remaining scripts as `class-source`.
- [ ] Remove synthetic linkage/frame-aggregate artifacts from persisted external script list.
- [ ] Backfill existing loaded projects during open (normalize on load).

### Phase 3: Frame Action Roundtrip

- [ ] Ensure frame action scripts export as frame actions on the correct timeline frame.
- [ ] Add conflict handling if frame indices changed (label+frame mapping, nearest-frame fallback).
- [ ] Frame-origin scripts editable only through timeline/frame surfaces.

### Phase 4: Linkage Regeneration Path

- [ ] Linkage-generated classes are export-time only, always regenerated.
- [ ] Bitmap linkage constructor defaults come from current `library.width` / `library.height`.
- [ ] Never consume stale source/body from imported legacy script for linkage classes.
- [ ] Do not save generated linkage class files as external project scripts.

### Phase 5: Diagnostics and Failsafes

- [ ] Add debug output (toggleable): script counts by origin, frame script reattachment map, linkage class regeneration map.
- [ ] Hard fail export if a script has unknown origin and cannot be normalized.

## Regression Test Matrix

1. Frame Action Preservation
- Import SWF with frame action in known frame.
- Export without edits.
- Verify action remains on same frame.

2. Linkage Regeneration Correctness
- Linked bitmap class starts `5,5`.
- Resize bitmap to `8,8`.
- Export.
- Verify class constructor defaults are `8,8`.

3. No-Edit Refresh Stability
- Refresh assets with no file changes.
- Export.
- Verify no script-origin drift and no shape/morph corruption.

4. Mixed Script Project
- Project with frame scripts + class scripts + linkage-generated scripts.
- Export.
- Verify each script routed by origin rule.
- Verify linkage-generated scripts are absent from persistent external script list.
- Verify frame-origin scripts remain internal to timeline editing surfaces.

5. Legacy Imported DoABC
- Import legacy project containing raw bytecode-only script history.
- Normalize origins.
- Export.
- Verify no passthrough and deterministic compile output.

## Migration Notes

- Existing project data needs one-time origin normalization on load.
- Store normalized result back to project file to avoid repeated inference.
- Keep provenance fields for debugging, but do not drive export from raw imported bytecode.
- During migration, purge synthetic external scripts that normalize to `frame` or `linkage-generated` intent.

## Risks and Mitigations

1. Decompile ambiguities for some legacy bytecode
- Mitigation: explicit normalization warnings and fallback classification requiring user review when ambiguous.

2. Initial export speed regression
- Mitigation: incremental compiler caching keyed by normalized source hash, not raw DoABC passthrough.

3. Timeline drift for frame scripts after edits
- Mitigation: owner mapping by stable identifiers (labels/depth/timeline id) with deterministic fallback.

## Completion Criteria

- Export path contains no raw DoABC passthrough logic.
- Frame-origin scripts export as frame actions in intended locations.
- Linkage-generated scripts always regenerate from current linkage metadata.
- Linked bitmap constructor defaults always match current dimensions.
- Refresh/export flows remain stable for shapes/morphshapes.
- Linkage-generated scripts do not persist as editable external scripts.
- Decompiled frame-script aggregates do not persist as external class scripts; they return to frame/timeline authoring model.
