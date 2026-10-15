"""Compare two SWFs: parse both, diff text/font entries, tag counts, sizes."""
from __future__ import annotations
import os, sys, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swf_to_n2d

def summarize(path):
    with open(path, 'rb') as f:
        data = f.read()
    header, tags = swf_to_n2d.parse_swf(data)
    
    # Tag type distribution
    tag_counts = {}
    for t in tags:
        tag_counts[t.tag_type] = tag_counts.get(t.tag_type, 0) + 1
    
    # Build char types + font names
    builder = swf_to_n2d.N2DBuilder(header, name=os.path.basename(path))
    builder.catalog_swf_tags(tags)
    scripts, frame_scripts = swf_to_n2d.decompile_all_scripts(builder.global_raw_tags)
    builder.frame_scripts = frame_scripts
    if scripts:
        builder.scripts.extend(scripts)
    builder.build_all()
    builder.build_main_timeline(tags)
    n2d = builder.to_n2d_json()
    
    texts = []
    fonts = []
    for lib in n2d.get('libraries', []):
        if not lib:
            continue
        if lib.get('type') == 'text':
            texts.append({
                'id': lib.get('id'),
                'swfCharId': lib.get('swfCharId'),
                'name': lib.get('name'),
                'text': lib.get('text'),
                'font': lib.get('font'),
                'size': lib.get('size'),
                'fontType': lib.get('fontType'),
                'html': lib.get('html'),
                'inputType': lib.get('inputType'),
                'color': lib.get('color'),
            })
        if lib.get('isFont'):
            fonts.append({
                'id': lib.get('id'),
                'swfCharId': lib.get('swfCharId'),
                'name': lib.get('name'),
                'fontTagType': lib.get('fontTagType'),
                'has_fontData': bool(lib.get('fontData')),
            })
    
    return {
        'size': len(data),
        'header': header,
        'tag_counts': tag_counts,
        'total_tags': len(tags),
        'texts': texts,
        'fonts': fonts,
        'lib_count': len(n2d.get('libraries', [])),
    }

def main():
    if len(sys.argv) < 3:
        print("Usage: python compare_swfs.py <original.swf> <exported.swf>")
        return 1
    
    p1, p2 = sys.argv[1], sys.argv[2]
    print(f"=== ORIGINAL: {os.path.basename(p1)} ===")
    s1 = summarize(p1)
    print(f"  Size: {s1['size']:,} bytes")
    print(f"  Dimensions: {s1['header']['width']}x{s1['header']['height']}")
    print(f"  FPS: {s1['header']['fps']}, Frames: {s1['header']['frameCount']}")
    print(f"  Total tags: {s1['total_tags']}, Libraries: {s1['lib_count']}")
    print(f"  Texts ({len(s1['texts'])}):")
    for t in s1['texts']:
        print(f"    charId={t['swfCharId']} text={t['text']!r} font={t['font']!r} size={t['size']} html={t['html']}")
    print(f"  Fonts ({len(s1['fonts'])}):")
    for f in s1['fonts']:
        print(f"    charId={f['swfCharId']} name={f['name']!r} tagType={f['fontTagType']} data={f['has_fontData']}")
    
    print(f"\n=== EXPORTED: {os.path.basename(p2)} ===")
    s2 = summarize(p2)
    print(f"  Size: {s2['size']:,} bytes")
    print(f"  Dimensions: {s2['header']['width']}x{s2['header']['height']}")
    print(f"  FPS: {s2['header']['fps']}, Frames: {s2['header']['frameCount']}")
    print(f"  Total tags: {s2['total_tags']}, Libraries: {s2['lib_count']}")
    print(f"  Texts ({len(s2['texts'])}):")
    for t in s2['texts']:
        print(f"    charId={t['swfCharId']} text={t['text']!r} font={t['font']!r} size={t['size']} html={t['html']}")
    print(f"  Fonts ({len(s2['fonts'])}):")
    for f in s2['fonts']:
        print(f"    charId={f['swfCharId']} name={f['name']!r} tagType={f['fontTagType']} data={f['has_fontData']}")
    
    print(f"\n=== DIFFERENCES ===")
    diffs = []
    
    # Size
    print(f"  Size: {s1['size']:,} -> {s2['size']:,} (ratio: {s2['size']/s1['size']:.3f})")
    
    # Header
    for k in ('width', 'height', 'fps', 'frameCount'):
        v1, v2 = s1['header'].get(k), s2['header'].get(k)
        if v1 != v2:
            diffs.append(f"  Header {k}: {v1} → {v2}")
            print(f"  Header {k}: {v1} → {v2}")
    
    # Text comparison by content matching
    orig_texts = {t['text']: t for t in s1['texts']}
    exp_texts = {t['text']: t for t in s2['texts']}
    
    print(f"\n  Text entries in original only:")
    for txt in orig_texts:
        if txt not in exp_texts:
            print(f"    MISSING: {txt!r}")
            diffs.append(f"Text missing in export: {txt!r}")
    
    print(f"  Text entries in export only:")
    for txt in exp_texts:
        if txt not in orig_texts:
            print(f"    NEW: {txt!r}")
    
    print(f"\n  Text entries in both:")
    for txt in orig_texts:
        if txt in exp_texts:
            o, e = orig_texts[txt], exp_texts[txt]
            match = all(o.get(k) == e.get(k) for k in ('font', 'size', 'fontType', 'html', 'color'))
            status = "✓ MATCH" if match else "⚠ DIFFER"
            print(f"    {txt!r}: {status}")
            if not match:
                for k in ('font', 'size', 'fontType', 'html', 'color'):
                    if o.get(k) != e.get(k):
                        print(f"      {k}: {o.get(k)!r} → {e.get(k)!r}")
                        diffs.append(f"Text {txt!r} {k}: {o.get(k)!r} → {e.get(k)!r}")
    
    # Tag count differences
    all_tag_types = set(list(s1['tag_counts'].keys()) + list(s2['tag_counts'].keys()))
    tag_diffs = []
    for tt in sorted(all_tag_types):
        c1 = s1['tag_counts'].get(tt, 0)
        c2 = s2['tag_counts'].get(tt, 0)
        if c1 != c2:
            tag_diffs.append((tt, c1, c2))
    if tag_diffs:
        print(f"\n  Tag count differences:")
        for tt, c1, c2 in tag_diffs:
            print(f"    tag {tt}: {c1} → {c2}")
    
    if diffs:
        print(f"\n  TOTAL DIFFERENCES: {len(diffs)}")
    else:
        print(f"\n  ✓ No significant differences found")
    
    return 1 if diffs else 0

if __name__ == '__main__':
    sys.exit(main())
