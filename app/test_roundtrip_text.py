"""
Roundtrip verification: SWF → N2D → SWF → N2D
Ensures text fields, fonts, and the html flag survive the full pipeline
without relying on rawTagBody.

Usage:
    python test_roundtrip_text.py <input.swf>
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time

# Ensure app/ is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import swf_to_n2d
import compile_n2d


def extract_text_entries(n2d: dict) -> list[dict]:
    """Pull text library entries with fields relevant to roundtrip fidelity."""
    texts = []
    for lib in n2d.get("libraries", []):
        if not lib or lib.get("type") != "text":
            continue
        texts.append({
            "id": lib.get("id"),
            "name": lib.get("name"),
            "text": lib.get("text"),
            "font": lib.get("font"),
            "fontType": lib.get("fontType"),
            "inputType": lib.get("inputType"),
            "size": lib.get("size"),
            "color": lib.get("color"),
            "align": lib.get("align"),
            "leading": lib.get("leading"),
            "leftMargin": lib.get("leftMargin"),
            "rightMargin": lib.get("rightMargin"),
            "multiline": lib.get("multiline"),
            "wordWrap": lib.get("wordWrap"),
            "border": lib.get("border"),
            "autoSize": lib.get("autoSize"),
            "html": lib.get("html"),
        })
    return texts


def extract_font_entries(n2d: dict) -> list[dict]:
    """Pull font library entries."""
    fonts = []
    for lib in n2d.get("libraries", []):
        if not lib or not lib.get("isFont"):
            continue
        fonts.append({
            "id": lib.get("id"),
            "name": lib.get("name"),
            "isFont": lib.get("isFont"),
            "fontTagType": lib.get("fontTagType"),
            "has_fontData": bool(lib.get("fontData")),
            "has_fontAuxTags": bool(lib.get("fontAuxTags")),
        })
    return fonts


def compare_entries(label: str, original: list[dict], roundtripped: list[dict]) -> list[str]:
    """Compare original vs roundtripped entries, return list of differences.
    
    Matches entries by content (text+font+size) rather than by position,
    since SWF char IDs are reassigned during compilation.
    """
    diffs = []
    if len(original) != len(roundtripped):
        diffs.append(f"  {label}: count mismatch — original={len(original)}, roundtripped={len(roundtripped)}")

    # Build lookup key for matching: (text, font, size)
    def _match_key(e):
        return (e.get("text", ""), e.get("font", ""), e.get("size"))

    rt_by_key = {}
    for e in roundtripped:
        k = _match_key(e)
        rt_by_key.setdefault(k, []).append(e)

    matched_orig = set()
    matched_rt = set()

    for i, orig in enumerate(original):
        k = _match_key(orig)
        candidates = rt_by_key.get(k, [])
        rt = None
        for c in candidates:
            ci = id(c)
            if ci not in matched_rt:
                rt = c
                matched_rt.add(ci)
                break
        if rt is None:
            diffs.append(f"  {label}: no match for original[{i}] "
                         f"(text={orig.get('text')!r} font={orig.get('font')!r})")
            continue
        matched_orig.add(i)
        for key in orig:
            if key in ("id", "name"):
                continue
            ov = orig[key]
            rv = rt.get(key)
            if ov != rv:
                diffs.append(f"  {label} (text={orig.get('text')!r}): "
                             f"{key}: {ov!r} → {rv!r}")
    return diffs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    swf_path = sys.argv[1]
    if not os.path.isfile(swf_path):
        print(f"Error: file not found: {swf_path}")
        return 1

    name = os.path.splitext(os.path.basename(swf_path))[0]

    with tempfile.TemporaryDirectory() as tmpdir:
        n2d_path_1 = os.path.join(tmpdir, f"{name}_pass1.n2d")
        swf_path_2 = os.path.join(tmpdir, f"{name}_roundtrip.swf")
        n2d_path_2 = os.path.join(tmpdir, f"{name}_pass2.n2d")
        shared_dir = tmpdir

        # ── Pass 1: SWF → N2D ──
        t0 = time.time()
        print(f"=== PASS 1: Import {os.path.basename(swf_path)} → N2D ===")
        with open(swf_path, "rb") as f:
            swf_data = f.read()
        header, tags = swf_to_n2d.parse_swf(swf_data)
        try:
            swf_to_n2d.validate_swf_sprites(tags)
        except ValueError:
            pass
        builder = swf_to_n2d.N2DBuilder(header, name=name)
        builder.catalog_swf_tags(tags)
        scripts, frame_scripts = swf_to_n2d.decompile_all_scripts(builder.global_raw_tags)
        builder.frame_scripts = frame_scripts
        if scripts:
            builder.scripts.extend(scripts)
        builder.build_all()
        builder.build_main_timeline(tags)
        builder._embed_bitmap_data_in_recodes()
        n2d_1 = builder.to_n2d_json()
        swf_to_n2d.save_n2d(n2d_1, n2d_path_1)
        print(f"  → {n2d_path_1} ({os.path.getsize(n2d_path_1):,} bytes)")
        print(f"  {time.time()-t0:.1f}s")

        # Extract original entries
        orig_texts = extract_text_entries(n2d_1)
        orig_fonts = extract_font_entries(n2d_1)
        print(f"  Found: {len(orig_texts)} text fields, {len(orig_fonts)} fonts")
        for t in orig_texts:
            print(f"    Text: {t['name']!r} text={t['text']!r} font={t['font']!r} "
                  f"html={t['html']} size={t['size']} fontType={t['fontType']}")
        for f in orig_fonts:
            print(f"    Font: {f['name']!r} fontTagType={f['fontTagType']} "
                  f"fontData={f['has_fontData']} auxTags={f['has_fontAuxTags']}")

        # Check for rawTagBody (should be NONE)
        raw_count = sum(1 for lib in n2d_1.get("libraries", [])
                        if lib and lib.get("rawTagBody"))
        print(f"  rawTagBody entries: {raw_count} (should be 0)")

        # ── Pass 2: N2D → SWF ──
        t1 = time.time()
        print(f"\n=== PASS 2: Compile N2D → SWF ===")
        compiler = compile_n2d.N2DCompiler(
            n2d_path=n2d_path_1,
            shared_dir=shared_dir,
            output_path=swf_path_2,
        )
        compiler.compile()
        swf2_size = os.path.getsize(swf_path_2)
        print(f"  → {swf_path_2} ({swf2_size:,} bytes)")
        print(f"  {time.time()-t1:.1f}s")

        # ── Pass 3: Re-import SWF → N2D ──
        t2 = time.time()
        print(f"\n=== PASS 3: Re-import roundtripped SWF → N2D ===")
        with open(swf_path_2, "rb") as f:
            swf2_data = f.read()
        header2, tags2 = swf_to_n2d.parse_swf(swf2_data)
        try:
            swf_to_n2d.validate_swf_sprites(tags2)
        except ValueError:
            pass
        builder2 = swf_to_n2d.N2DBuilder(header2, name=name + "_rt")
        builder2.catalog_swf_tags(tags2)
        scripts2, fscripts2 = swf_to_n2d.decompile_all_scripts(builder2.global_raw_tags)
        builder2.frame_scripts = fscripts2
        if scripts2:
            builder2.scripts.extend(scripts2)
        builder2.build_all()
        builder2.build_main_timeline(tags2)
        builder2._embed_bitmap_data_in_recodes()
        n2d_2 = builder2.to_n2d_json()
        swf_to_n2d.save_n2d(n2d_2, n2d_path_2)
        print(f"  → {n2d_path_2} ({os.path.getsize(n2d_path_2):,} bytes)")
        print(f"  {time.time()-t2:.1f}s")

        # Extract roundtripped entries
        rt_texts = extract_text_entries(n2d_2)
        rt_fonts = extract_font_entries(n2d_2)
        print(f"  Found: {len(rt_texts)} text fields, {len(rt_fonts)} fonts")
        for t in rt_texts:
            print(f"    Text: {t['name']!r} text={t['text']!r} font={t['font']!r} "
                  f"html={t['html']} size={t['size']} fontType={t['fontType']}")
        for f in rt_fonts:
            print(f"    Font: {f['name']!r} fontTagType={f['fontTagType']} "
                  f"fontData={f['has_fontData']} auxTags={f['has_fontAuxTags']}")

        raw_count2 = sum(1 for lib in n2d_2.get("libraries", [])
                         if lib and lib.get("rawTagBody"))
        print(f"  rawTagBody entries: {raw_count2} (should be 0)")

        # ── Compare ──
        print(f"\n{'='*60}")
        print("ROUNDTRIP COMPARISON")
        print(f"{'='*60}")

        diffs = []
        diffs.extend(compare_entries("TEXT", orig_texts, rt_texts))
        diffs.extend(compare_entries("FONT", orig_fonts, rt_fonts))

        # Compare stage-level properties
        for key in ("width", "height", "frameRate", "backgroundColor"):
            v1 = n2d_1.get("stage", {}).get(key) or n2d_1.get(key)
            v2 = n2d_2.get("stage", {}).get(key) or n2d_2.get(key)
            if v1 != v2:
                diffs.append(f"  STAGE: {key}: {v1!r} → {v2!r}")

        # Library count comparison
        libs1 = [l for l in n2d_1.get("libraries", []) if l and l.get("type") != "folder"]
        libs2 = [l for l in n2d_2.get("libraries", []) if l and l.get("type") != "folder"]
        type_counts1 = {}
        type_counts2 = {}
        for l in libs1:
            t = l.get("type", "?")
            type_counts1[t] = type_counts1.get(t, 0) + 1
        for l in libs2:
            t = l.get("type", "?")
            type_counts2[t] = type_counts2.get(t, 0) + 1
        print(f"  Original lib types:     {type_counts1}")
        print(f"  Roundtripped lib types: {type_counts2}")
        for t in set(list(type_counts1.keys()) + list(type_counts2.keys())):
            c1 = type_counts1.get(t, 0)
            c2 = type_counts2.get(t, 0)
            if c1 != c2:
                note = ""
                if t == "bitmap" and c2 > c1:
                    note = " (expected: shape-embedded bitmaps get separate tags)"
                diffs.append(f"  LIB COUNT: type={t}: {c1} → {c2}{note}")

        # SWF size comparison
        orig_size = len(swf_data)
        print(f"\n  Original SWF size:     {orig_size:>10,} bytes")
        print(f"  Roundtripped SWF size: {swf2_size:>10,} bytes")
        ratio = swf2_size / orig_size if orig_size else 0
        print(f"  Size ratio:            {ratio:.3f}")

        if diffs:
            print(f"\n  {'⚠ DIFFERENCES FOUND':}")
            for d in diffs:
                print(d)
        else:
            print(f"\n  ✓ ALL TEXT/FONT FIELDS MATCH — roundtrip is 1:1")

        print(f"\n  rawTagBody original: {raw_count}, roundtripped: {raw_count2}")
        if raw_count == 0 and raw_count2 == 0:
            print("  ✓ NO rawTagBody in either pass — fully rebuilt pipeline")
        else:
            print("  ⚠ rawTagBody detected — pipeline is NOT fully rebuilt")

        print(f"\nTotal time: {time.time()-t0:.1f}s")
        return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main())
