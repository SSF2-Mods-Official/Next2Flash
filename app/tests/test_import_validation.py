#!/usr/bin/env python3
"""
test_import_validation.py — Validate SWF→N2D conversion output

Simulates what the browser's LibraryRepository.add() does:
checks every library entry has a valid 'id' field.

This reproduces the error:
  "LibraryRepository.add: library must have an id"

Usage:
    python test_import_validation.py <path_to_swf_or_ssf>
    python test_import_validation.py   (uses default fox.ssf)
"""
import sys
import os
import time
import traceback

# Ensure we can import from app/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DEFAULT_SSF = (
    r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original"
    r"\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"
)


def validate_library(idx, lib):
    """Check a single library entry the way the JS tool does.
    
    Returns list of error strings (empty = OK).
    """
    errors = []

    # JS check: if (!library || typeof library.id === "undefined")
    if not isinstance(lib, dict):
        errors.append(f"[{idx}] not a dict: {type(lib)}")
        return errors

    if "id" not in lib:
        errors.append(f"[{idx}] MISSING 'id' key entirely. keys={sorted(lib.keys())}")
    elif lib["id"] is None:
        errors.append(f"[{idx}] id is None")
    elif not isinstance(lib["id"], (int, float)):
        errors.append(f"[{idx}] id is not numeric: {type(lib['id']).__name__}={lib['id']!r}")

    # JS coercion: const id = library.id | 0;
    # This means id=0 is valid only for the main timeline container
    raw_id = lib.get("id")
    if isinstance(raw_id, (int, float)):
        coerced = int(raw_id) & 0xFFFFFFFF  # JS bitwise OR
        if coerced == 0 and lib.get("type") != "container":
            errors.append(f"[{idx}] id coerces to 0 (id={raw_id}, type={lib.get('type')})")

    # Check required fields for addLibrary
    if "type" not in lib:
        errors.append(f"[{idx}] MISSING 'type' field")

    return errors


def validate_n2d(n2d, verbose=False):
    """Validate entire N2D JSON the way the browser would load it.
    
    Returns (total_libs, error_list).
    """
    libs = n2d.get("libraries", [])
    all_errors = []
    seen_ids = {}
    
    for idx, lib in enumerate(libs):
        errs = validate_library(idx, lib)
        all_errors.extend(errs)

        # Check for duplicate IDs
        lid = lib.get("id") if isinstance(lib, dict) else None
        if lid is not None and isinstance(lid, (int, float)):
            lid = int(lid)
            if lid in seen_ids:
                prev = seen_ids[lid]
                all_errors.append(
                    f"[{idx}] DUPLICATE id={lid} "
                    f"(first at [{prev['idx']}] type={prev['type']} name={prev['name']}), "
                    f"this: type={lib.get('type')} name={lib.get('name')}"
                )
            else:
                seen_ids[lid] = {
                    "idx": idx,
                    "type": lib.get("type", "?"),
                    "name": lib.get("name", "?"),
                }

        if verbose and not errs:
            print(f"  [{idx:4d}] OK  id={lib.get('id'):<6} type={lib.get('type','?'):<12} name={lib.get('name','?')}")

    # Check characterId > max library id
    max_lib_id = max((int(lib.get("id", 0)) for lib in libs if isinstance(lib, dict)), default=0)
    char_id = n2d.get("characterId", 0)
    if char_id <= max_lib_id:
        all_errors.append(
            f"characterId ({char_id}) <= max library id ({max_lib_id}); "
            f"tool will collide when creating new objects"
        )

    return len(libs), all_errors


def simulate_progressive_load(n2d):
    """Simulate the JS progressive loading (chunk by chunk) to find
    exactly which library causes the crash at 88%.
    """
    libs = n2d.get("libraries", [])
    CHUNK_SIZE = 50
    total_chunks = (len(libs) + CHUNK_SIZE - 1) // CHUNK_SIZE

    print(f"\n--- Simulating progressive load ({len(libs)} libs, {total_chunks} chunks) ---")

    for chunk_idx in range(total_chunks):
        start = chunk_idx * CHUNK_SIZE
        end = min(start + CHUNK_SIZE, len(libs))
        pct = round((end / len(libs)) * 100)

        for idx in range(start, end):
            lib = libs[idx]
            errs = validate_library(idx, lib)
            if errs:
                print(f"  CRASH at [{idx}] ({pct}% loaded, chunk {chunk_idx+1}/{total_chunks}):")
                for e in errs:
                    print(f"    {e}")
                print(f"    Library data: {_summarize(lib)}")
                return idx

        # This matches the JS console.log
        # print(f"  Loaded {end}/{len(libs)} ({pct}%)")

    print("  All libraries loaded successfully (no crash)")
    return None


def _summarize(lib):
    """Summarize a library entry for debugging (truncate large fields)."""
    if not isinstance(lib, dict):
        return repr(lib)[:200]
    summary = {}
    for k, v in lib.items():
        if isinstance(v, str) and len(v) > 100:
            summary[k] = v[:50] + f"...({len(v)} chars)"
        elif isinstance(v, (list, dict)) and len(str(v)) > 100:
            summary[k] = f"<{type(v).__name__} len={len(v)}>"
        else:
            summary[k] = v
    return summary


def run_conversion(swf_path, name=None):
    """Run the full SWF→N2D conversion pipeline."""
    if name is None:
        name = os.path.splitext(os.path.basename(swf_path))[0]

    print(f"Reading: {swf_path}")
    with open(swf_path, "rb") as f:
        data = f.read()
    print(f"  {len(data):,} bytes")

    from conversion_service import ConversionService

    svc = ConversionService()
    t0 = time.time()

    def progress(msg):
        elapsed = time.time() - t0
        print(f"  [{elapsed:5.1f}s] {msg}")

    n2d = svc.convert_swf_to_n2d(data, name=name, progress_callback=progress)
    elapsed = time.time() - t0
    print(f"  Conversion done in {elapsed:.1f}s")
    return n2d


def test_msgpack_roundtrip(n2d):
    """Test that MessagePack serialization preserves all library IDs.
    
    The server sends: msgpack.packb(n2d) → ZIP → browser
    The browser does: unzip → msgpack.decode() → progressive load
    
    This tests the exact same round-trip.
    """
    import msgpack
    import zipfile
    import io

    print(f"\n--- Testing MessagePack round-trip ---")

    # Step 1: Pack exactly like the server does
    packed = msgpack.packb(n2d, use_bin_type=True)
    print(f"  Packed to {len(packed):,} bytes")

    # Step 2: Put in ZIP exactly like the server does
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
        zf.writestr('project.msgpack', packed)
    zip_bytes = zip_buf.getvalue()
    print(f"  ZIP size: {len(zip_bytes):,} bytes")

    # Step 3: Unpack exactly like the browser does
    zip_buf2 = io.BytesIO(zip_bytes)
    with zipfile.ZipFile(zip_buf2) as zf:
        raw = zf.read('project.msgpack')
    decoded = msgpack.unpackb(raw, raw=False)
    print(f"  Decoded {len(decoded.get('libraries', []))} libraries")

    # Step 4: Validate the decoded data
    libs_before = n2d.get('libraries', [])
    libs_after = decoded.get('libraries', [])

    if len(libs_before) != len(libs_after):
        print(f"  ERROR: library count changed: {len(libs_before)} -> {len(libs_after)}")

    diffs = []
    for i, (before, after) in enumerate(zip(libs_before, libs_after)):
        id_before = before.get('id')
        id_after = after.get('id')
        if id_before != id_after:
            diffs.append(f"  [{i}] id changed: {id_before!r} -> {id_after!r}")
        # Check if keys are bytes vs str (msgpack gotcha)
        if 'id' not in after and b'id' in after:
            diffs.append(f"  [{i}] 'id' key is bytes b'id' not str 'id'!")
        if 'id' not in after and b'id' not in after:
            diffs.append(f"  [{i}] 'id' key missing entirely! keys={sorted(after.keys())}")

    # Also check if any keys became bytes (common msgpack issue)
    sample = libs_after[0] if libs_after else {}
    byte_keys = [k for k in sample.keys() if isinstance(k, bytes)]
    if byte_keys:
        print(f"  WARNING: msgpack decoded keys as bytes: {byte_keys[:5]}")
        print(f"  This would cause 'id' to be missing in JS (JS has no bytes type)")
        # Re-validate with string keys
        print(f"  Re-decoding with raw=False, strict_map_key=False...")
        decoded2 = msgpack.unpackb(raw, raw=False, strict_map_key=False)
        sample2 = decoded2.get('libraries', [{}])[0]
        byte_keys2 = [k for k in sample2.keys() if isinstance(k, bytes)]
        if byte_keys2:
            print(f"  Still has byte keys: {byte_keys2[:5]}")

    if diffs:
        print(f"\n  MSGPACK ROUND-TRIP ERRORS ({len(diffs)}):")
        for d in diffs[:20]:
            print(f"    {d}")
        if len(diffs) > 20:
            print(f"    ... and {len(diffs) - 20} more")
    else:
        print(f"  All {len(libs_after)} library IDs preserved through MessagePack")

    # Step 5: Validate the decoded output as the browser would see it
    total, errors = validate_n2d(decoded)
    if errors:
        print(f"\n  POST-MSGPACK VALIDATION ERRORS ({len(errors)}):")
        for e in errors[:20]:
            print(f"    {e}")
    else:
        print(f"  Post-msgpack validation: all {total} OK")

    return len(diffs) + len(errors)


def test_server_endpoint(swf_path):
    """Test the actual HTTP endpoint if the server is running."""
    import urllib.request
    import urllib.error

    print(f"\n--- Testing live server endpoint ---")
    try:
        with open(swf_path, 'rb') as f:
            swf_data = f.read()

        # Build multipart form data
        boundary = b'----PythonTestBoundary'
        filename = os.path.basename(swf_path)
        body = (
            b'------PythonTestBoundary\r\n'
            b'Content-Disposition: form-data; name="file"; filename="' + filename.encode() + b'"\r\n'
            b'Content-Type: application/octet-stream\r\n\r\n'
            + swf_data +
            b'\r\n------PythonTestBoundary--\r\n'
        )

        req = urllib.request.Request(
            'http://127.0.0.1:5000/api/swf-to-project',
            data=body,
            headers={
                'Content-Type': 'multipart/form-data; boundary=----PythonTestBoundary',
            },
            method='POST',
        )

        print(f"  POST /api/swf-to-project ({len(swf_data):,} bytes)...")
        resp = urllib.request.urlopen(req, timeout=120)
        resp_data = resp.read()
        print(f"  Response: {resp.status} {resp.reason}, {len(resp_data):,} bytes")
        print(f"  Headers: X-N2D-Name={resp.headers.get('X-N2D-Name')}, "
              f"X-N2D-Libraries={resp.headers.get('X-N2D-Libraries')}")

        # Decode the response the same way the browser does
        import zipfile
        import io
        import msgpack

        zip_buf = io.BytesIO(resp_data)
        with zipfile.ZipFile(zip_buf) as zf:
            names = zf.namelist()
            print(f"  ZIP contents: {names}")
            if 'project.msgpack' in names:
                raw = zf.read('project.msgpack')
                decoded = msgpack.unpackb(raw, raw=False)
            elif 'project.json' in names:
                import json
                decoded = json.loads(zf.read('project.json'))
            else:
                print(f"  ERROR: No project.msgpack or project.json in ZIP")
                return 1

        libs = decoded.get('libraries', [])
        print(f"  Decoded {len(libs)} libraries from server response")

        # Validate
        total, errors = validate_n2d(decoded)
        crash_idx = simulate_progressive_load(decoded)

        if errors:
            print(f"\n  SERVER RESPONSE ERRORS ({len(errors)}):")
            for e in errors[:20]:
                print(f"    {e}")
            return len(errors)
        else:
            print(f"  Server response validation: all {total} OK")
            return 0

    except urllib.error.URLError as e:
        print(f"  Server not running or unreachable: {e}")
        print(f"  (Start server with: python server.py)")
        return -1
    except Exception as e:
        print(f"  ERROR: {e}")
        traceback.print_exc()
        return 1


def main():
    swf_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SSF
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    if not os.path.isfile(swf_path):
        print(f"ERROR: File not found: {swf_path}")
        return 1

    # Step 1: Convert
    try:
        n2d = run_conversion(swf_path)
    except Exception as e:
        print(f"\nCONVERSION FAILED: {e}")
        traceback.print_exc()
        return 2

    # Step 2: Validate all libraries (pre-serialization)
    print(f"\n--- Validating {len(n2d.get('libraries', []))} libraries (pre-serialization) ---")
    total, errors = validate_n2d(n2d, verbose=verbose)

    if errors:
        print(f"\n{'='*60}")
        print(f"PRE-SERIALIZATION ERRORS: {len(errors)} error(s) in {total} libraries")
        print(f"{'='*60}")
        for e in errors:
            print(f"  ERROR: {e}")
    else:
        print(f"\n  All {total} libraries passed validation")

    # Step 3: Test MessagePack round-trip (this is what the browser sees)
    msgpack_errors = test_msgpack_roundtrip(n2d)

    # Step 4: Simulate progressive loading (same as browser)
    crash_idx = simulate_progressive_load(n2d)

    # Step 5: Test live server if running
    server_errors = test_server_endpoint(swf_path)

    # Step 6: Summary
    print(f"\n{'='*60}")
    total_errors = len(errors) + msgpack_errors + (1 if crash_idx is not None else 0)
    if server_errors and server_errors > 0:
        total_errors += server_errors

    if total_errors > 0:
        print(f"RESULT: FAIL — {total_errors} total error(s)")
        if crash_idx is not None:
            print(f"  Browser would crash at library index {crash_idx}")
        return 1
    else:
        print(f"RESULT: PASS — all {total} libraries valid through full pipeline")
        if server_errors == -1:
            print(f"  (server endpoint not tested — start server to include)")
        return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
