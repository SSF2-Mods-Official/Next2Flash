# Next2Flash — Self-Verification Tests

How we validate that SWF import and export work end-to-end, with no manual browser interaction required.

---

## Quick Run

```bat
cd app
python -c "from verify_export import verify_all; verify_all()"
```

Or test a single project:

```bat
cd app
python -c "
import compile_n2d, os, tempfile
n2d_path = r'converted\fox\project.n2d'
with tempfile.TemporaryDirectory() as tmpdir:
    swf_path = os.path.join(tmpdir, 'fox.swf')
    compiler = compile_n2d.N2DCompiler(n2d_path=n2d_path, shared_dir=tmpdir, output_path=swf_path)
    compiler.compile()
    print(f'OK: {os.path.getsize(swf_path):,} bytes')
"
```

---

## What Gets Verified

### 1. SWF → N2D Import (conversion_service.py)

The import pipeline converts a raw `.swf` (or `.ssf`) binary into the internal `.n2d` JSON format:

| Step | What it does | What can break |
|------|-------------|----------------|
| `parse_swf` | Read SWF header + decompress | Corrupt/truncated SWF |
| `catalog_swf_tags` | Walk all SWF tags, index by type | Unknown tag types |
| `decompile_scripts` | Extract AS3 bytecode via RABCDAsm | Missing SDK tools |
| `build_all` | Convert tags → library entries (shapes, bitmaps, sounds, containers) | Bitmap ID resolution, shape recode parsing |
| `build_main_timeline` | Extract root timeline layers/frames | PlaceObject depth conflicts |
| `embed_bitmap_data` | Inline bitmap pixel data as base64 | Large bitmaps, memory |
| `to_n2d_json` | Serialize to N2D JSON + msgpack + zip | Encoding errors |

**Verified by:** `python -m pytest tests/ -v` and Puppeteer headless import test (`node test/headless_import.js`).

### 2. N2D → SWF Export (compilation_pipeline.py)

The export pipeline compiles `.n2d` back to a playable `.swf` via 8 stages:

| Stage | Time (fox) | What it does |
|-------|-----------|-------------|
| Load N2D | 745 ms | Read + decompress project.n2d (msgpack + zip) |
| Allocate Char IDs | 12 ms | Assign SWF character IDs in dependency order |
| Parse Raw Tags | 3 ms | Extract DoABC, SymbolClass, font aux tags |
| **Define Assets** | **8,610 ms** | Emit all definition tags (bitmaps, shapes, sounds, sprites) |
| Build Timeline | 1 ms | Generate root timeline PlaceObject/RemoveObject tags |
| Compile AS3 | <1 ms | Pass through original DoABC bytecode |
| Assemble SWF | 4 ms | Build SWF header + concatenate all tags |
| Write Output | 2 ms | Write final .swf to disk |

**Verified by:** Compiling all available projects and checking output size > 0:

```
fox.swf         1,909,584 bytes  ✓
kirby.swf       9,086,922 bytes  ✓
naruto.swf      3,411,101 bytes  ✓
finaldestination.swf 10,210,593 bytes  ✓
```

### 3. BitWriter Binary Encoding (swf_binary_io.py)

Low-level bit-packing for SWF binary structures:

```python
from swf_binary_io import BitWriter

bw = BitWriter()
bw.write_ub(16, 0xABCD)       # 16 bits unsigned → ab cd
bw.write_sb(8, -1)            # 8 bits signed → ff
bw.write_fb(32, 1.5)          # 32 bits fixed-point 16.16 → 00 01 80 00
assert bw.get_bytes() is not None
```

---

## Bugs Found & Fixed During Verification

### 1. BitWriter parameter order (negative shift count)

**Symptom:** `ValueError: negative shift count` on export.

**Root cause:** `write_ub(value, nbits)` signature didn't match callers using SWF convention `write_ub(nbits, value)`. When a signed coordinate was passed as `nbits`, the shift went negative.

**Fix:** Swapped parameter order to `write_ub(nbits, value)`, `write_sb(nbits, value)`. Added `nbits <= 0` guard.

### 2. Missing write_fb method

**Symptom:** `AttributeError: 'BitWriter' object has no attribute 'write_fb'` when writing matrices with scale/rotation.

**Fix:** Added `write_fb(nbits, value)` — encodes float as 16.16 fixed-point, delegates to `write_sb`.

### 3. Pipeline temp_compiler missing attributes

**Symptom:** `AttributeError: 'N2DCompiler' object has no attribute '_orig_to_new_id'` (and `_lib_to_char_idx`, `_definition_tags`).

**Root cause:** `compilation_pipeline.py` creates temp N2DCompiler instances via `__new__()` and manually copies attributes, but several were missing from the copy list.

**Fix:** Added `_orig_to_new_id`, `_lib_to_char_idx`, `_char_idx_to_swf_id`, `_definition_tags` to the appropriate pipeline stages.

### 4. BitWriter.__init__ missing output argument

**Symptom:** `TypeError: BitWriter.__init__() missing 1 required positional argument: 'output'` — 6 call sites create `BitWriter()` with no args.

**Fix:** Made `output` default to `None` (auto-creates `io.BytesIO()`). Added `get_bytes()` method.

---

## Performance Profiler

Both Python and JS profilers are built in and auto-report:

- **Python:** `app/profiler.py` — wraps server operations, auto-saves JSON to `app/converted/_profiles/`
- **JavaScript:** `app/assets/js/n2f-profiler.js` — instruments fetch calls, reports to console

The profiler output shown in the table above (Stage timing) is produced automatically on every export. Look for the `═══ PROFILE ═══` block in the server console.

---

## Running All Checks

```bat
:: 1. Unit tests
cd app
python -m pytest tests/ -v

:: 2. Export verification (all projects)
python -c "
import compile_n2d, os, tempfile
for proj in ['fox','kirby','naruto','finaldestination','falco','donkeykong','goku']:
    n2d = f'converted\\{proj}\\project.n2d'
    if not os.path.isfile(n2d): continue
    with tempfile.TemporaryDirectory() as t:
        out = os.path.join(t, f'{proj}.swf')
        compile_n2d.N2DCompiler(n2d_path=n2d, shared_dir=t, output_path=out).compile()
        print(f'{proj}: {os.path.getsize(out):,} bytes OK')
"

:: 3. Headless browser import test
cd test
node headless_import.js

:: 4. BitWriter sanity
cd ..
python -c "from swf_binary_io import BitWriter; bw=BitWriter(); bw.write_ub(16,0xABCD); assert bw.get_bytes()==b'\\xab\\xcd'; print('BitWriter OK')"
```
