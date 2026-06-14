"""
SWF -> N2D -> SWF -> N2D roundtrip gap analyzer.

For each test SWF:
  1. Parse SWF and build N2D_A (the "ground truth" N2D for the original SWF)
  2. Compile N2D_A -> SWF_B
  3. Parse SWF_B and build N2D_B
  4. Diff N2D_A vs N2D_B at the structural level
     (header, library inventory, per-library detail, scripts, timeline frames,
     raw global tags) and print a per-category gap report.

Run:
    python app/tests/test_swf_n2d_roundtrip_gaps.py [swf1.swf swf2.swf ...]

If no SWFs are passed, a default discovery set is used. Returns non-zero
exit code if any roundtrip blew up (compile failure / parse failure), but
*structural diffs are reported as data, not failures* — the point of this
test is to map gaps, not to gatekeep.
"""
from __future__ import annotations

import os
import sys
import time
import tempfile
import traceback
from collections import Counter
from typing import Any

# Make sibling app/ modules importable
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import swf_to_n2d as s2n
import compile_n2d as c2n


# ─────────────────────────────────────────────────────────────────────────
#  N2D summarization
# ─────────────────────────────────────────────────────────────────────────

def swf_to_n2d_dict(swf_path: str) -> dict:
    """Run the full SWF→N2D pipeline and return the in-memory N2D dict."""
    with open(swf_path, "rb") as f:
        data = f.read()
    header, tags = s2n.parse_swf(data)
    name = os.path.splitext(os.path.basename(swf_path))[0]
    builder = s2n.N2DBuilder(header, name=name)
    builder.catalog_swf_tags(tags)
    scripts, frame_scripts = s2n.decompile_all_scripts(builder.global_raw_tags)
    builder.frame_scripts = frame_scripts
    if scripts:
        builder.scripts.extend(scripts)
    builder.build_all()
    builder.build_main_timeline(tags)
    return builder.to_n2d_json()


def summarize_n2d(n2d: dict) -> dict:
    """Reduce an N2D to comparable structural fingerprints."""
    header = n2d.get("header") or {}
    libs = [l for l in (n2d.get("libraries") or []) if l]

    lib_types = Counter()
    lib_detail = {}  # by swfCharId or id
    for lib in libs:
        t = lib.get("type") or ("font" if lib.get("isFont") else "unknown")
        lib_types[t] += 1
        key = lib.get("swfCharId") if lib.get("swfCharId") is not None else f"@{lib.get('id')}"
        d = {"type": t, "name": lib.get("name")}
        if t == "shape":
            d["nFills"] = len(lib.get("fills") or [])
            d["nStrokes"] = len(lib.get("strokes") or [])
            d["nRecodes"] = len(lib.get("recodes") or [])
            d["bounds"] = lib.get("bounds")
        elif t == "bitmap":
            d["w"] = lib.get("width")
            d["h"] = lib.get("height")
            d["hasData"] = bool(lib.get("imageData") or lib.get("bitmapData"))
        elif t == "movieclip":
            d["totalFrame"] = lib.get("totalFrame")
            d["nLayers"] = len(lib.get("layers") or [])
            d["nChars"] = sum(len(l.get("characters") or []) for l in (lib.get("layers") or []))
        elif t == "sound":
            d["sampleRate"] = lib.get("sampleRate")
            d["nSamples"] = lib.get("sampleCount")
        elif t == "text":
            d["text"] = lib.get("text")
            d["font"] = lib.get("font")
            d["size"] = lib.get("size")
            d["html"] = lib.get("html")
            d["inputType"] = lib.get("inputType")
        if lib.get("isFont"):
            d["fontTagType"] = lib.get("fontTagType")
            d["hasFontData"] = bool(lib.get("fontData"))
            d["nGlyphs"] = len(lib.get("glyphs") or [])
        lib_detail[key] = d

    scripts = n2d.get("scripts") or []
    script_paths = sorted(s.get("path") or s.get("name") or "?" for s in scripts)
    script_nonempty = sum(1 for s in scripts if (s.get("source") or "").strip())

    raw_tags = n2d.get("rawGlobalTags") or []
    raw_tag_types = Counter(t.get("type") for t in raw_tags if isinstance(t, dict))

    # Main timeline placements (look for top-level frames / layers)
    main_layers = n2d.get("layers") or []
    main_frame_count = header.get("frameCount")
    main_placement_count = 0
    for lay in main_layers:
        for ch in (lay.get("characters") or []):
            main_placement_count += 1

    return {
        "header": {
            "w": header.get("width"),
            "h": header.get("height"),
            "fps": header.get("fps"),
            "frames": header.get("frameCount"),
            "version": header.get("version"),
        },
        "libTypes": dict(lib_types),
        "libCount": len(libs),
        "libDetail": lib_detail,
        "scriptCount": len(scripts),
        "scriptNonEmpty": script_nonempty,
        "scriptPaths": script_paths,
        "rawTagTypes": dict(raw_tag_types),
        "rawTagCount": len(raw_tags),
        "mainLayers": len(main_layers),
        "mainPlacements": main_placement_count,
        "mainFrames": main_frame_count,
    }


# ─────────────────────────────────────────────────────────────────────────
#  Diff
# ─────────────────────────────────────────────────────────────────────────

def diff_summaries(a: dict, b: dict) -> list[str]:
    """Produce a human-readable list of differences."""
    out: list[str] = []

    # Header
    for k, va in a["header"].items():
        vb = b["header"].get(k)
        if va != vb:
            out.append(f"header.{k}: A={va!r} B={vb!r}")

    # Top-level scalars
    for k in ("libCount", "scriptCount", "scriptNonEmpty", "rawTagCount",
              "mainLayers", "mainPlacements", "mainFrames"):
        if a[k] != b[k]:
            out.append(f"{k}: A={a[k]} B={b[k]} (delta {b[k] - a[k] if isinstance(a[k], (int, float)) and isinstance(b[k], (int, float)) else '?'})")

    # libTypes
    all_types = set(a["libTypes"]) | set(b["libTypes"])
    for t in sorted(all_types):
        ca, cb = a["libTypes"].get(t, 0), b["libTypes"].get(t, 0)
        if ca != cb:
            out.append(f"libTypes[{t}]: A={ca} B={cb}")

    # rawTagTypes
    all_rt = set(a["rawTagTypes"]) | set(b["rawTagTypes"])
    for t in sorted(all_rt, key=lambda x: (x is None, x)):
        ca, cb = a["rawTagTypes"].get(t, 0), b["rawTagTypes"].get(t, 0)
        if ca != cb:
            out.append(f"rawTagTypes[{t}]: A={ca} B={cb}")

    # Script paths added/removed
    sa, sb = set(a["scriptPaths"]), set(b["scriptPaths"])
    only_a = sa - sb
    only_b = sb - sa
    if only_a:
        out.append(f"scripts only in A ({len(only_a)}): {sorted(only_a)[:5]}{'...' if len(only_a) > 5 else ''}")
    if only_b:
        out.append(f"scripts only in B ({len(only_b)}): {sorted(only_b)[:5]}{'...' if len(only_b) > 5 else ''}")

    # Library detail by key
    keys_a, keys_b = set(a["libDetail"]), set(b["libDetail"])
    only_lib_a = keys_a - keys_b
    only_lib_b = keys_b - keys_a
    if only_lib_a:
        sample = sorted(str(k) for k in only_lib_a)[:8]
        out.append(f"library keys only in A ({len(only_lib_a)}): {sample}{'...' if len(only_lib_a) > 8 else ''}")
    if only_lib_b:
        sample = sorted(str(k) for k in only_lib_b)[:8]
        out.append(f"library keys only in B ({len(only_lib_b)}): {sample}{'...' if len(only_lib_b) > 8 else ''}")

    # Field-level diffs for libraries present in BOTH
    common = keys_a & keys_b
    detail_diffs: list[str] = []
    for k in sorted(common, key=lambda x: (isinstance(x, str), x)):
        da, db = a["libDetail"][k], b["libDetail"][k]
        sub = []
        for fk in set(da) | set(db):
            va, vb = da.get(fk), db.get(fk)
            if va != vb:
                sub.append(f"{fk}: {va!r} -> {vb!r}")
        if sub:
            detail_diffs.append(f"  lib[{k}] {da.get('type')}: " + "; ".join(sub))
    if detail_diffs:
        out.append(f"per-library field diffs ({len(detail_diffs)} libs):")
        out.extend(detail_diffs[:20])
        if len(detail_diffs) > 20:
            out.append(f"  ... and {len(detail_diffs) - 20} more")

    return out


# ─────────────────────────────────────────────────────────────────────────
#  Roundtrip runner
# ─────────────────────────────────────────────────────────────────────────

def roundtrip_one(swf_path: str) -> dict:
    """Run SWF → N2D → SWF → N2D for a single file."""
    result: dict[str, Any] = {
        "swf": swf_path,
        "swf_size": os.path.getsize(swf_path),
        "stages": {},
        "diffs": None,
        "error": None,
    }
    tmpdir = tempfile.mkdtemp(prefix="rt_gap_")
    try:
        t0 = time.time()
        # Stage 1: SWF → N2D_A
        n2d_a_path = os.path.join(tmpdir, "A.n2d")
        n2d_a = swf_to_n2d_dict(swf_path)
        s2n.save_n2d(n2d_a, n2d_a_path)
        sum_a = summarize_n2d(n2d_a)
        result["stages"]["swf_to_n2d_A"] = {
            "ok": True,
            "seconds": round(time.time() - t0, 1),
            "n2d_size": os.path.getsize(n2d_a_path),
            "summary": sum_a,
        }

        # Stage 2: N2D_A → SWF_B
        t1 = time.time()
        swf_b_path = os.path.join(tmpdir, "B.swf")
        compiler = c2n.N2DCompiler(
            n2d_path=n2d_a_path,
            shared_dir=None,
            output_path=swf_b_path,
            sdk_path=None,  # let compile_n2d auto-find
        )
        compiler.compile()
        result["stages"]["n2d_A_to_swf_B"] = {
            "ok": True,
            "seconds": round(time.time() - t1, 1),
            "swf_size": os.path.getsize(swf_b_path),
        }

        # Stage 3: SWF_B → N2D_B
        t2 = time.time()
        n2d_b = swf_to_n2d_dict(swf_b_path)
        sum_b = summarize_n2d(n2d_b)
        result["stages"]["swf_B_to_n2d_B"] = {
            "ok": True,
            "seconds": round(time.time() - t2, 1),
            "summary": sum_b,
        }

        # Stage 4: diff
        result["diffs"] = diff_summaries(sum_a, sum_b)
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
        result["traceback"] = traceback.format_exc()
    return result


# ─────────────────────────────────────────────────────────────────────────
#  Defaults & main
# ─────────────────────────────────────────────────────────────────────────

DEFAULT_SWFS = [
    os.path.join(APP_DIR, "_dev", "test_bitmap", "test.swf"),
    os.path.join(APP_DIR, "_dev", "fox_fresh.swf"),
    os.path.join(APP_DIR, "_dev", "lloyd_roundtrip.swf"),
]


def print_report(r: dict) -> None:
    name = os.path.basename(r["swf"])
    print()
    print("=" * 72)
    print(f"  {name}   ({r['swf_size']:,} bytes)")
    print("=" * 72)
    if r["error"]:
        print(f"  [X] ERROR: {r['error']}")
        # show a few tb lines
        for line in (r.get("traceback") or "").splitlines()[-6:]:
            print(f"    {line}")
        # still show whatever stages completed
    for stage, info in r["stages"].items():
        secs = info.get("seconds", "?")
        if "n2d_size" in info:
            print(f"  [OK] {stage}: {secs}s  ({info['n2d_size']:,} bytes)")
        elif "swf_size" in info:
            print(f"  [OK] {stage}: {secs}s  ({info['swf_size']:,} bytes)")
        else:
            print(f"  [OK] {stage}: {secs}s")
    if "swf_to_n2d_A" in r["stages"] and "swf_B_to_n2d_B" in r["stages"]:
        sa = r["stages"]["swf_to_n2d_A"]["summary"]
        sb = r["stages"]["swf_B_to_n2d_B"]["summary"]
        print(f"  A: libs={sa['libCount']} (types={sa['libTypes']}) scripts={sa['scriptCount']}({sa['scriptNonEmpty']}) rawTags={sa['rawTagCount']} mainPlacements={sa['mainPlacements']}")
        print(f"  B: libs={sb['libCount']} (types={sb['libTypes']}) scripts={sb['scriptCount']}({sb['scriptNonEmpty']}) rawTags={sb['rawTagCount']} mainPlacements={sb['mainPlacements']}")
    if r["diffs"] is not None:
        if r["diffs"]:
            print(f"  [!] {len(r['diffs'])} structural differences:")
            for d in r["diffs"]:
                print(f"     - {d}")
        else:
            print("  [OK] No structural differences detected.")


def main(argv: list[str]) -> int:
    swfs = argv[1:] if len(argv) > 1 else [p for p in DEFAULT_SWFS if os.path.isfile(p)]
    if not swfs:
        print("No SWFs found. Pass paths on the command line.")
        return 2
    print(f"Testing roundtrip on {len(swfs)} SWF(s):")
    for s in swfs:
        print(f"  - {s}")

    results = [roundtrip_one(s) for s in swfs]
    for r in results:
        print_report(r)

    failed = [r for r in results if r["error"]]
    print()
    print("=" * 72)
    print(f"  SUMMARY: {len(results) - len(failed)}/{len(results)} completed full roundtrip")
    if failed:
        print(f"  {len(failed)} failed:")
        for r in failed:
            print(f"    - {os.path.basename(r['swf'])}: {r['error']}")
    total_diffs = sum(len(r['diffs'] or []) for r in results if r['diffs'] is not None)
    print(f"  {total_diffs} total structural differences across all SWFs")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
