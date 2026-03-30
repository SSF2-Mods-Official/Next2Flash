#!/usr/bin/env python3
"""
Batch SWF/SSF roundtrip test: SWF → N2D → SWF → compare tags.

For each .ssf/.swf in the source directory, performs a full roundtrip and
compares the original vs output tag-by-tag. Writes results to a JSON report.

Usage:
    python test/roundtrip_all.py <source_dir> [--output report.json] [--limit N]
"""
import argparse
import json
import os
import struct
import sys
import tempfile
import time
import traceback
import zlib

# Add app root to path
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)

import swf_to_n2d
import compile_n2d

# Import xref validator from same directory
_test_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _test_dir)
from validate_xref import validate_swf_xrefs, XRefIssue

# ── SWF Tag Parsing ──────────────────────────────────────────────────────

DEFINE_TAGS = {2, 22, 32, 83, 6, 21, 35, 90, 20, 36, 39, 46, 84,
               11, 33, 48, 75, 10, 14, 37, 87}

TAG_NAMES = {
    0: 'End', 1: 'ShowFrame', 2: 'DefineShape', 4: 'PlaceObject',
    5: 'RemoveObject', 6: 'DefineBits', 7: 'DefineButton', 9: 'SetBgColor',
    10: 'DefineFont', 11: 'DefineText', 13: 'DefineFontInfo', 14: 'DefineSound',
    15: 'StartSound', 17: 'DefineButtonSound', 18: 'SoundStreamHead',
    19: 'SoundStreamBlock', 20: 'DefineBitsLossless', 21: 'DefineBitsJPEG2',
    22: 'DefineShape2', 24: 'Protect', 26: 'PlaceObject2', 28: 'RemoveObject2',
    32: 'DefineShape3', 33: 'DefineText2', 34: 'DefineButton2',
    35: 'DefineBitsJPEG3', 36: 'DefineBitsLossless2', 37: 'DefineEditText',
    39: 'DefineSprite', 43: 'FrameLabel', 45: 'SoundStreamHead2',
    46: 'DefineMorphShape', 48: 'DefineFont2', 56: 'ExportAssets',
    62: 'DefineFontInfo2', 69: 'FileAttributes', 70: 'PlaceObject3',
    72: 'DoABC', 73: 'FontAlignZones', 74: 'CSMTextSettings',
    75: 'DefineFont3', 76: 'SymbolClass', 77: 'Metadata', 78: 'DefineScalingGrid',
    82: 'DoABC2', 83: 'DefineShape4', 84: 'DefineMorphShape2',
    86: 'SceneFrameLabel', 87: 'DefineBinaryData', 88: 'DefineFontName',
    89: 'StartSound2', 90: 'DefineBitsJPEG4',
}


def tag_name(tt):
    return TAG_NAMES.get(tt, f'tag{tt}')


def parse_swf_tags(path):
    """Parse an SWF file into a list of (tag_type, body_bytes) tuples."""
    raw = open(path, 'rb').read()
    data = raw
    magic = raw[:3]
    if magic == b'CWS':
        data = raw[:8] + zlib.decompress(raw[8:])
    elif magic == b'ZWS':
        import lzma
        data = raw[:8] + lzma.decompress(raw[12:])
    elif magic != b'FWS':
        raise ValueError(f"Not a valid SWF file: {path} (magic={magic!r})")

    nbits = (data[8] >> 3) & 0x1f
    total_bits = 5 + nbits * 4
    rect_end = 8 + (total_bits + 7) // 8
    tag_start = rect_end + 4  # skip fps(2) + frameCount(2)
    tags = []
    i = tag_start
    while i < len(data):
        if i + 2 > len(data):
            break
        h = struct.unpack_from('<H', data, i)[0]
        tt = h >> 6
        ln = h & 0x3f
        hdr = 2
        if ln == 0x3f:
            if i + 6 > len(data):
                break
            ln = struct.unpack_from('<I', data, i + 2)[0]
            hdr = 6
        body = data[i + hdr:i + hdr + ln]
        tags.append((tt, body))
        i += hdr + ln
        if tt == 0:
            break
    return tags


def count_tags_by_type(tags):
    """Count tags by tag_type, returns {tag_type: count}."""
    counts = {}
    for tt, _ in tags:
        counts[tt] = counts.get(tt, 0) + 1
    return counts


def build_define_map(tags):
    """Build {(tag_type, charId): body} for all definition tags."""
    m = {}
    for tt, body in tags:
        if tt in DEFINE_TAGS and len(body) >= 2:
            cid = struct.unpack_from('<H', body, 0)[0]
            key = (tt, cid)
            m[key] = body
    return m


def build_body_set(tags):
    """Build {tag_type: set_of_body_after_charID} for passthrough comparison.
    
    Since charIDs are renumbered, we compare the body AFTER the first 2 bytes
    (the charID). For sprite bodies this won't match (internal charID refs),
    but for leaf tags like bitmaps and sounds it should be byte-identical.
    """
    result = {}
    for tt, body in tags:
        if tt in DEFINE_TAGS and len(body) >= 2:
            body_after_cid = body[2:]
            result.setdefault(tt, set()).add(body_after_cid)
    return result


# ── Roundtrip Pipeline ───────────────────────────────────────────────────

def roundtrip_swf(swf_path, tmpdir):
    """SWF → N2D → SWF roundtrip. Returns (n2d_path, rt_swf_path, errors)."""
    errors = []
    name = os.path.splitext(os.path.basename(swf_path))[0]
    n2d_path = os.path.join(tmpdir, name + '.n2d')
    rt_swf_path = os.path.join(tmpdir, name + '_rt.swf')

    # Step 1: SWF → N2D
    with open(swf_path, 'rb') as f:
        swf_data = f.read()
    header, tags = swf_to_n2d.parse_swf(swf_data)
    builder = swf_to_n2d.N2DBuilder(header, name=name)
    builder.catalog_swf_tags(tags)

    try:
        scripts, frame_scripts = swf_to_n2d.decompile_all_scripts(
            builder.global_raw_tags)
        builder.frame_scripts = frame_scripts
        if scripts:
            builder.scripts.extend(scripts)
    except Exception as e:
        errors.append(f"AS3 decompile warning: {e}")

    builder.build_all()
    builder.build_main_timeline(tags)
    builder._embed_bitmap_data_in_recodes()
    n2d = builder.to_n2d_json()
    swf_to_n2d.save_n2d(n2d, n2d_path)

    # Step 2: N2D → SWF
    compiler = compile_n2d.N2DCompiler(
        n2d_path=n2d_path,
        shared_dir=tmpdir,
        output_path=rt_swf_path,
        sdk_path=None,
    )
    compiler.compile()

    return n2d_path, rt_swf_path, errors


# ── Tag Comparison ───────────────────────────────────────────────────────

# Tags where body-after-charID should be IDENTICAL (leaf assets, no internal refs)
LEAF_TAGS = {
    20: 'DefineBitsLossless',
    36: 'DefineBitsLossless2',
    6: 'DefineBits',
    21: 'DefineBitsJPEG2',
    35: 'DefineBitsJPEG3',
    90: 'DefineBitsJPEG4',
    14: 'DefineSound',
    87: 'DefineBinaryData',
}

# Tags where body-after-charID may differ due to internal charID references
REREF_TAGS = {
    2: 'DefineShape', 22: 'DefineShape2', 32: 'DefineShape3', 83: 'DefineShape4',
    39: 'DefineSprite',
    46: 'DefineMorphShape', 84: 'DefineMorphShape2',
    11: 'DefineText', 33: 'DefineText2', 37: 'DefineEditText',
    75: 'DefineFont3', 48: 'DefineFont2', 10: 'DefineFont',
}


def compare_swfs(orig_path, rt_path):
    """Compare original and roundtrip SWFs. Returns a results dict."""
    orig_tags = parse_swf_tags(orig_path)
    rt_tags = parse_swf_tags(rt_path)

    orig_counts = count_tags_by_type(orig_tags)
    rt_counts = count_tags_by_type(rt_tags)

    orig_define = build_define_map(orig_tags)
    rt_define = build_define_map(rt_tags)

    results = {
        'orig_tag_count': len(orig_tags),
        'rt_tag_count': len(rt_tags),
        'orig_define_count': len(orig_define),
        'rt_define_count': len(rt_define),
        'tag_type_counts': {},
        'leaf_tag_results': {},
        'missing_tag_types': [],
        'extra_tag_types': [],
        'issues': [],
    }

    # Compare tag counts by type
    all_types = sorted(set(list(orig_counts.keys()) + list(rt_counts.keys())))
    for tt in all_types:
        oc = orig_counts.get(tt, 0)
        rc = rt_counts.get(tt, 0)
        results['tag_type_counts'][tag_name(tt)] = {'orig': oc, 'rt': rc}
        if oc > 0 and rc == 0:
            results['missing_tag_types'].append(tag_name(tt))
        elif oc == 0 and rc > 0:
            results['extra_tag_types'].append(tag_name(tt))

    # Compare define tag counts by type
    orig_def_by_type = {}
    for (tt, cid) in orig_define:
        orig_def_by_type[tt] = orig_def_by_type.get(tt, 0) + 1
    rt_def_by_type = {}
    for (tt, cid) in rt_define:
        rt_def_by_type[tt] = rt_def_by_type.get(tt, 0) + 1

    for tt in sorted(set(list(orig_def_by_type.keys()) + list(rt_def_by_type.keys()))):
        oc = orig_def_by_type.get(tt, 0)
        rc = rt_def_by_type.get(tt, 0)
        if oc != rc:
            results['issues'].append(
                f"{tag_name(tt)}: count mismatch orig={oc} rt={rc}")

    # For leaf tags, compare body-after-charID using multisets
    for tt in sorted(LEAF_TAGS.keys()):
        orig_bodies = sorted(body[2:] for (t, _), body in orig_define.items() if t == tt)
        rt_bodies = sorted(body[2:] for (t, _), body in rt_define.items() if t == tt)

        if not orig_bodies and not rt_bodies:
            continue

        matched = 0
        unmatched_orig = 0
        unmatched_rt = 0

        # Build multiset from rt
        rt_pool = list(rt_bodies)
        for ob in orig_bodies:
            found = False
            for idx, rb in enumerate(rt_pool):
                if ob == rb:
                    rt_pool.pop(idx)
                    matched += 1
                    found = True
                    break
            if not found:
                unmatched_orig += 1
        unmatched_rt = len(rt_pool)

        total = len(orig_bodies)
        results['leaf_tag_results'][tag_name(tt)] = {
            'total_orig': total,
            'total_rt': len(rt_bodies),
            'matched': matched,
            'unmatched_orig': unmatched_orig,
            'unmatched_rt': unmatched_rt,
        }
        if unmatched_orig > 0 or unmatched_rt > 0:
            results['issues'].append(
                f"{tag_name(tt)}: {unmatched_orig}/{total} orig unmatched, "
                f"{unmatched_rt}/{len(rt_bodies)} rt unmatched")

    # Check for structural tags
    for check_tt in [69, 9]:  # FileAttributes, SetBgColor
        orig_has = any(tt == check_tt for tt, _ in orig_tags)
        rt_has = any(tt == check_tt for tt, _ in rt_tags)
        if orig_has and not rt_has:
            results['issues'].append(f"Missing structural tag: {tag_name(check_tt)}")

    # Count shape/sprite define tags (these have internal charID refs, so
    # body-after-charID won't match directly — just check counts)
    for tt in sorted(REREF_TAGS.keys()):
        oc = orig_def_by_type.get(tt, 0)
        rc = rt_def_by_type.get(tt, 0)
        if oc > 0 or rc > 0:
            results[f'reref_{tag_name(tt)}'] = {'orig': oc, 'rt': rc}

    return results


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_dir', help='Directory containing .ssf/.swf files')
    parser.add_argument('-o', '--output', default='test/roundtrip_report.json',
                        help='Output JSON report path')
    parser.add_argument('--limit', type=int, default=0,
                        help='Limit number of files to process (0=all)')
    parser.add_argument('--keep-tmp', action='store_true',
                        help='Keep temporary N2D/SWF files')
    args = parser.parse_args()

    source_dir = args.source_dir
    if not os.path.isdir(source_dir):
        print(f"Error: directory not found: {source_dir}", file=sys.stderr)
        return 1

    # Find all .ssf/.swf files
    files = []
    for root, dirs, fnames in os.walk(source_dir):
        for fn in sorted(fnames):
            if fn.lower().endswith(('.ssf', '.swf')):
                files.append(os.path.join(root, fn))
    files.sort()

    if args.limit > 0:
        files = files[:args.limit]

    print(f"Found {len(files)} SWF/SSF files to roundtrip")
    print(f"Output report: {args.output}")
    print()

    report = {
        'source_dir': source_dir,
        'total_files': len(files),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'results': [],
        'summary': {
            'pass': 0,
            'fail': 0,
            'error': 0,
            'total_issues': [],
        },
    }

    tmpdir = tempfile.mkdtemp(prefix='n2f_rt_')
    print(f"Temp dir: {tmpdir}")
    print()

    for idx, swf_path in enumerate(files):
        rel = os.path.relpath(swf_path, source_dir)
        size_kb = os.path.getsize(swf_path) // 1024
        print(f"[{idx+1}/{len(files)}] {rel} ({size_kb}KB) ... ", end='', flush=True)

        entry = {
            'file': rel,
            'size_kb': size_kb,
            'status': 'unknown',
            'time_s': 0,
            'import_error': None,
            'compile_error': None,
            'compare': None,
            'issues': [],
        }

        t0 = time.time()
        try:
            # Roundtrip
            n2d_path, rt_swf_path, rt_errors = roundtrip_swf(swf_path, tmpdir)
            entry['issues'].extend(rt_errors)

            # Compare tags
            cmp_result = compare_swfs(swf_path, rt_swf_path)
            entry['compare'] = cmp_result
            entry['issues'].extend(cmp_result.get('issues', []))

            # Cross-reference integrity check on roundtripped SWF
            with open(rt_swf_path, 'rb') as rf:
                rt_data = rf.read()
            xref_issues = validate_swf_xrefs(rt_data)
            xref_errors = [str(x) for x in xref_issues if x.severity == XRefIssue.ERROR]
            xref_warnings = [str(x) for x in xref_issues if x.severity == XRefIssue.WARN]
            entry['xref_errors'] = xref_errors
            entry['xref_warnings'] = xref_warnings
            entry['issues'].extend(xref_errors)

            # Also check original SWF for baseline xref issues
            with open(swf_path, 'rb') as of:
                orig_data = of.read()
            orig_xref = validate_swf_xrefs(orig_data)
            orig_xref_errors = [str(x) for x in orig_xref if x.severity == XRefIssue.ERROR]
            entry['orig_xref_errors'] = orig_xref_errors

            # Count only NEW xref errors (not in original) as failures
            new_xref_errors = [e for e in xref_errors if e not in set(orig_xref_errors)]

            all_issues = cmp_result.get('issues', []) + new_xref_errors
            if len(all_issues) == 0:
                entry['status'] = 'PASS'
                report['summary']['pass'] += 1
                status_msg = 'PASS'
                if xref_warnings:
                    status_msg += f' ({len(xref_warnings)} xref warns)'
                print(status_msg, end='')
            else:
                entry['status'] = 'FAIL'
                report['summary']['fail'] += 1
                n_cmp = len(cmp_result.get('issues', []))
                n_xref = len(new_xref_errors)
                parts = []
                if n_cmp:
                    parts.append(f'{n_cmp} tag')
                if n_xref:
                    parts.append(f'{n_xref} xref')
                print(f"FAIL ({', '.join(parts)})", end='')

        except Exception as e:
            entry['status'] = 'ERROR'
            tb = traceback.format_exc()
            # Determine if import or compile failed
            if 'compile' in tb.lower() or 'N2DCompiler' in tb:
                entry['compile_error'] = str(e)
            else:
                entry['import_error'] = str(e)
            entry['issues'].append(f"Exception: {e}")
            report['summary']['error'] += 1
            print(f"ERROR: {e}", end='')

        entry['time_s'] = round(time.time() - t0, 2)
        report['results'].append(entry)
        print(f"  ({entry['time_s']}s)")

    # Clean up temp dir unless --keep-tmp
    if not args.keep_tmp:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

    # Build summary
    issue_types = {}
    for entry in report['results']:
        for issue in entry.get('issues', []):
            # Normalize issue type
            key = issue.split(':')[0].strip() if ':' in issue else issue[:60]
            issue_types[key] = issue_types.get(key, 0) + 1
    report['summary']['total_issues'] = sorted(
        issue_types.items(), key=lambda x: -x[1])

    # Write report
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print()
    print("=" * 60)
    print(f"RESULTS: {report['summary']['pass']} PASS, "
          f"{report['summary']['fail']} FAIL, "
          f"{report['summary']['error']} ERROR "
          f"/ {len(files)} total")
    print()
    if report['summary']['total_issues']:
        print("Top issues:")
        for issue, count in report['summary']['total_issues'][:20]:
            print(f"  [{count:3d}x] {issue}")
    print()
    print(f"Full report: {args.output}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
