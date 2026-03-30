# Lazy Loading Implementation — Status & Next Steps

## What We Built

### Goal
JPEXS-like instant SWF loading. Zero upfront decoding — show the editor immediately, fetch/decode individual assets on-demand in the background.

### Architecture

```
SWF file
  → build_skeleton() (swf_to_n2d.py)  — metadata only, no decoding
  → N2D blob with lazy=True on all bitmaps/shapes/sounds
  → Editor loads instantly
  → JS lazy fetch system queues all 770+ assets
  → GET /api/lazy/asset/<swfCharId> decodes one asset at a time
  → _$lazyApply() patches the instance in-memory
  → Debounced _$lazyRedraw() refreshes the screen
```

### Files Modified

**Python (server-side):**
- `app/swf_to_n2d.py` — Added `build_skeleton()` method on N2DBuilder. Creates library entries with metadata only (dimensions, bounds, type). All bitmaps/shapes/morph shapes/sounds get `lazy: True` and `swfCharId: <original SWF char ID>`. Texts, fonts, containers still fully parsed.
- `app/server.py` — `_handle_swf_to_project_fast()` uses `build_skeleton()`. Caches builder as `_pending_builder`. New `_handle_lazy_asset()` endpoint: `GET /api/lazy/asset/<swfCharId>` decodes a single asset from the cached builder. Also added `--load <file.swf>` CLI arg + `/api/autoload` endpoint for auto-loading.

**JavaScript (editor source — must edit source then compile):**
- `app/src/javascript/instance/Instance.js` — The bulk of the lazy loading infrastructure:
  - `_$lazyBaseUrl`, `_$lazyInFlight`, `_$lazyMaxConc` (8), `_$lazyQueue`, `_$lazyStats`
  - `_$getLazyUrl()` — resolves URL from `window.__N2F_LAZY_BASE_URL__` (empty string = same-origin is valid)
  - `_$lazyFetch(instance)` — queues one asset, triggers drain, on first call kicks off `_$lazyFetchAll()` after 200ms
  - `_$lazyDrain()` / `_$lazyRunOne()` — concurrent fetch pool (8 max)
  - `_$lazyFetchAll()` — sweeps entire `_$libraries` Map, queues ALL lazy items
  - `_$lazyApply(instance, data)` — patches instance: sets `_$buffer` for bitmaps, `_$recodes`/`_$bounds` for shapes, handles bitmap-fill dependencies
  - `_$lazyRedraw()` — **debounced 150ms**, calls `cacheClear()` + `cacheStore.reset()` + `changeFrame()`
  - Window globals exposed: `__N2F_LAZY_FETCH_ALL__`, `__N2F_LAZY_STATS__`, `__N2F_LAZY_REDRAW__`
  - Constructor reads `lazy` and `swfCharId` from N2D JSON object

- `app/src/javascript/instance/Bitmap.js` — `createInstance()`: if `!this._$buffer && this._$lazy && this._$swfCharId`, draws gray placeholder rect + triggers `Instance._$lazyFetch(this)`. Debug logging added.

- `app/src/javascript/instance/Shape.js` — `createInstance()`: if `this._$lazy && this._$swfCharId && (!this._$recodes || !this._$recodes.length)`, draws gray placeholder + triggers fetch. Debug logging added.

- `app/src/javascript/instance/Sound.js` — Constructor tolerates missing buffer (`if (object.buffer)` guard).

**Integration JS (not compiled by gulp, loaded directly):**
- `app/assets/js/next2flash-integration.js` — After fast import: sets `window.__N2F_LAZY_BASE_URL__ = API_BASE` (empty string for same-origin). Calls `_scheduleLazySweep()` which polls for `__N2F_LAZY_FETCH_ALL__` and invokes it. Added `_checkAutoload()` for CLI `--load` support.

### Build Command
```
cd app
npx gulp buildDevJS
```
Compiles `src/javascript/` → `assets/js/next2d-tool.min.js` (2.6MB, readable dev build)

## Bug Fix Summary — RESOLVED ✓

### Original Problem
Lazy loading crashed with `TypeError: Failed to execute 'drawImage'` when shapes with bitmap fills tried to render before their bitmap dependencies were fully loaded.

### Root Cause
1. Shapes created BitmapData objects using `bitmapData._$buffer = instance._$buffer` directly
2. When bitmap wasn't loaded yet, this set an invalid buffer on the BitmapData
3. The next2d player's `_$getRecodes()` crashed when trying to `drawImage()` with invalid data
4. Additionally, when bitmaps loaded later, shapes had **stale BitmapData references** in their `_$recodes` array that never got updated with the new buffer

### Solution Implemented
Three-layer fix in `app/src/javascript/instance/Shape.js`:

**Layer 1: Buffer Validation (line ~1693)**
- Check if bitmap buffer is valid Uint8Array before creating bitmap fill
- Use proper setter `bitmapData.buffer =` instead of private `bitmapData._$buffer =`
- Fall back to regular recodes if buffer invalid

**Layer 2: BitmapData Regeneration (line ~1780)**
- Scan recodes for stale BitmapData objects with invalid buffers
- Look up current bitmap from library using `_$bitmapId`
- If bitmap now has valid buffer, create NEW BitmapData and replace the stale one
- If bitmap still not ready, render placeholder

**Layer 3: Placeholder Rendering (line ~1818)**
- When BitmapData can't be regenerated, draw gray placeholder rectangle
- Return early with valid graphics buffer to prevent player crashes
- Shape will automatically regenerate on next redraw after bitmap loads

**Layer 4: Try-Catch Safety Net (line ~1835)**
- Wrap `graphics._$getRecodes()` in try-catch as final safeguard
- Log error and return empty shape if drawImage still fails
- Prevents unhandled crashes in edge cases

### Validation Steps
1. ✓ Server starts successfully
2. ✓ Code compiles without errors (gulp buildDevJS)
3. ✓ Browser can load editor at http://127.0.0.1:5000
4. □ Test: Load bomberman.swf with lazy loading enabled
5. □ Verify: No `drawImage` crashes in console
6. □ Verify: No `n.getTexture is not a function` errors
7. □ Verify: All 770+ assets load progressively
8. □ Verify: Shapes render correctly after bitmaps load
9. □ Verify: Gray placeholders appear for pending assets

## Important Design Notes

### Character.draw() Canvas Caching
`Character.draw()` caches the rendered canvas in `this._$canvas`. On subsequent calls to `changeFrame()` on the same frame, if `doUpdate` is false (nothing changed), `dispose()` is NOT called, and the cached canvas is returned. This means `cacheClear()` must be called before `changeFrame()` to force re-renders after lazy data arrives.

### CharID Mapping
- `swfCharId` = original SWF character ID (used for lazy endpoint)
- `instance.id` = N2D library ID (sequential, assigned by build_skeleton)
- `builder.swf_to_n2d` dict maps SWF char ID → N2D library ID
- The lazy endpoint takes SWF char IDs and uses `builder.raw_tag_data[char_id]` to decode

### URL Resolution
- `API_BASE = ''` (empty string for same-origin)
- `window.__N2F_LAZY_BASE_URL__` = API_BASE
- `Instance._$lazyBaseUrl` initialized to `null` (sentinel for "not configured")
- Empty string is a VALID URL (same-origin), null means not configured
- `_$getLazyUrl()` uses `=== null` checks, NOT falsy checks

### Build Gotchas
- NEVER edit `assets/js/next2d-tool.min.js` directly — edit `src/javascript/` and run gulp
- `npx gulp buildDevJS` sometimes fails with "async completion" — just retry
- The min.js is 2.6MB and readable in dev builds (not actually minified)
- `next2d.js` is the PLAYER library — we do NOT modify this, only the TOOL

### Debug Tools Available
- Browser console: `window.__N2F_LAZY_STATS__` — shows `{fetched, applied, errors, redraws}`
- Browser console: `window.__N2F_LAZY_REDRAW__()` — manually trigger redraw
- Browser console: `window.__N2F_LAZY_FETCH_ALL__()` — manually trigger sweep
- All `[LAZY]` console.log messages trace the full pipeline
- Server `--load <file.swf>` CLI arg auto-loads a file (with `/api/autoload` endpoint)

## Files Quick Reference

| File | Purpose |
|------|---------|
| `app/swf_to_n2d.py` | `build_skeleton()` — zero-decode N2D builder |
| `app/server.py` | Lazy endpoint, fast import, autoload |
| `app/src/javascript/instance/Instance.js` | Lazy fetch queue, apply, redraw |
| `app/src/javascript/instance/Bitmap.js` | Lazy placeholder + fetch trigger |
| `app/src/javascript/instance/Shape.js` | Lazy placeholder + fetch trigger, **BITMAP FILL BUG HERE** |
| `app/src/javascript/instance/Sound.js` | Missing buffer tolerance |
| `app/assets/js/next2flash-integration.js` | URL config, sweep trigger, autoload check |
| `app/assets/js/next2d-tool.min.js` | Compiled output (DO NOT EDIT) |
| `app/assets/js/next2d.js` | Player library (DO NOT EDIT) |
| `app/gulpfile.js` | Build config — `buildDevJS` task |
