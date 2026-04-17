#!/usr/bin/env python3
"""
Simulate web tool roundtrip data loss.
Strips fields that JS toObject() doesn't produce, then compiles.
Compares output with pure Python roundtrip.
"""
import sys, os, struct, zlib, tempfile, copy, json
sys.path.insert(0, os.path.dirname(__file__))
from swf_to_n2d import N2DBuilder, parse_swf, save_n2d
from compile_n2d import load_n2d
from swf_binary_io import BitReader

SSF_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\fox.ssf"

def decompress_swf(raw):
    sig = raw[:3]
    if sig == b'CWS': return raw[:8] + zlib.decompress(raw[8:])
    return raw

def get_offset(data):
    br = BitReader(data, 8)
    nb = br.read_ub(5)
    for _ in range(4): br.read_sb(nb)
    br.align()
    return br.byte_pos + 4

def parse_tags_raw(data, offset):
    tags = []; pos = offset
    while pos < len(data):
        if pos + 2 > len(data): break
        tcl = struct.unpack_from('<H', data, pos)[0]
        tt = tcl >> 6; tl = tcl & 0x3F; pos += 2
        if tl == 0x3F:
            tl = struct.unpack_from('<I', data, pos)[0]; pos += 4
        body = data[pos:pos+tl]; tags.append((tt, body)); pos += tl
        if tt == 0: break
    return tags

def simulate_js_toobject(n2d_data):
    """Simulate what Next2D editor's toObject() would produce.
    
    This strips fields that JS drops, mimicking the data loss of:
    - MovieClip.toObject(): drops totalFrame, rawTagBody, rawTagType, etc.
    - Layer.toObject(): drops swfDepth
    - Character.toObject(): preserves places, startFrame, endFrame, tween, name, libraryId, id
    - Shape.toObject(): preserves recodes, bounds, bitmapId, inBitmap
    """
    data = copy.deepcopy(n2d_data)
    
    for lib in data.get('libraries', []):
        lib_type = lib.get('type', '')
        
        if lib_type == 'folder':
            # Folder.toObject() keeps: id, name, type, symbol, folderId, mode
            continue
        
        if lib_type == 'container':
            # MovieClip.toObject() output: id, name, type, symbol, folderId,
            #   currentFrame, leftFrame, layers, labels, sounds, actions
            # DROPS: totalFrame, rawTagBody, rawTagType, isMorphShape, swfCharId
            for key in list(lib.keys()):
                if key not in ('id', 'name', 'type', 'symbol', 'folderId',
                              'currentFrame', 'leftFrame', 'layers', 'labels',
                              'sounds', 'actions'):
                    lib.pop(key)
            
            # Layer.toObject() drops swfDepth
            for layer in lib.get('layers', []):
                layer.pop('swfDepth', None)
                
                # Character.toObject() preserves: id, name, libraryId, places, startFrame, endFrame, tween
                for char in layer.get('characters', []):
                    for key in list(char.keys()):
                        if key not in ('id', 'name', 'libraryId', 'places',
                                      'startFrame', 'endFrame', 'tween'):
                            char.pop(key)
        
        elif lib_type == 'shape':
            # Shape.toObject() keeps: id, name, type, symbol, folderId,
            #   bitmapId, grid, inBitmap, recodes, bounds
            for key in list(lib.keys()):
                if key not in ('id', 'name', 'type', 'symbol', 'folderId',
                              'bitmapId', 'grid', 'inBitmap', 'recodes', 'bounds'):
                    lib.pop(key)
        
        elif lib_type == 'bitmap':
            # Bitmap.toObject() — keep basic fields + buffer
            # In "light-mode" editor blob, buffer may be absent
            pass
        
        elif lib_type == 'sound':
            # Sound fields that JS drops
            pass
    
    return data


def simulate_merge(editor_data, disk_data):
    """Simulate _merge_editor_into_disk."""
    # Update top-level
    for key in ('stage', 'name'):
        if key in editor_data:
            disk_data[key] = editor_data[key]
    
    disk_map = {}
    disk_libs = disk_data.get('libraries', [])
    for lib in disk_libs:
        if lib:
            disk_map[lib.get('id')] = lib
    
    roundtrip_keys = ('swfCharId', 'externalFile', 'fontData', 'fontTagType', 'fontFaceName',
                      'buttonData', 'binaryDataBody', 'soundFormat',
                      'isBinaryData', 'isFont', 'isButton', 'isMorphShape',
                      'fontAuxParsed', 'buffer', 'buttonTrackAsMenu', 'buttonActions',
                      'totalFrame', 'endRecodes', 'endBounds', 'rawTagType')
    
    for elib in editor_data.get('libraries', []):
        if not elib:
            continue
        lib_id = elib.get('id')
        dlib = disk_map.get(lib_id)
        if not dlib:
            disk_libs.append(elib)
            continue
        
        # Save roundtrip fields
        saved = {}
        for k in roundtrip_keys:
            if k in dlib:
                saved[k] = dlib[k]
        
        # Save swfDepth per-layer
        disk_layer_depths = {}
        for dl in dlib.get('layers', []):
            lname = dl.get('name')
            if lname and 'swfDepth' in dl:
                disk_layer_depths[lname] = dl['swfDepth']
        
        # Overwrite with editor data
        dlib.clear()
        dlib.update(elib)
        
        # Restore roundtrip fields
        for k, v in saved.items():
            if k not in dlib or not dlib[k]:
                dlib[k] = v
        
        # Restore swfDepth
        if disk_layer_depths:
            for el in dlib.get('layers', []):
                lname = el.get('name')
                if lname and lname in disk_layer_depths and 'swfDepth' not in el:
                    el['swfDepth'] = disk_layer_depths[lname]
    
    return disk_data


def main():
    with open(SSF_PATH, 'rb') as f: raw = f.read()
    
    # Build N2D
    header, tags = parse_swf(raw)
    builder = N2DBuilder(header, "fox")
    builder.catalog_swf_tags(tags)
    builder.frame_scripts = {}
    builder.build_all()
    builder.build_main_timeline(tags)
    builder._embed_bitmap_data_in_recodes()
    n2d = builder.to_n2d_json()
    
    # Save to disk (the "project.n2d")
    n2d_path = os.path.join(tempfile.gettempdir(), "fox_webtool_sim.n2d")
    save_n2d(n2d, n2d_path, bitmap_buffers=builder.bitmap_buffers)
    
    # Load back (this is what the server would load from disk)
    disk_data, _ = load_n2d(n2d_path)
    
    # Simulate JS editor: strip fields that toObject() doesn't produce
    editor_data = simulate_js_toobject(copy.deepcopy(disk_data))
    
    # Count what was lost
    lost_fields = {}
    for dlib, elib in zip(disk_data.get('libraries', []), editor_data.get('libraries', [])):
        for key in set(dlib.keys()) - set(elib.keys()):
            lost_fields[key] = lost_fields.get(key, 0) + 1
    
    print("=== Fields lost by JS toObject() ===")
    for k, v in sorted(lost_fields.items(), key=lambda x: -x[1]):
        print(f"  {k}: lost in {v} libraries")
    
    # Simulate the merge
    merged = simulate_merge(editor_data, copy.deepcopy(disk_data))
    
    # Check what's different after merge vs original disk data
    print("\n=== Post-merge differences vs original ===")
    merged_map = {lib['id']: lib for lib in merged.get('libraries', []) if lib}
    disk_map = {lib['id']: lib for lib in disk_data.get('libraries', []) if lib}
    
    diff_counts = {}
    diff_examples = {}
    for lib_id in disk_map:
        dlib = disk_map[lib_id]
        mlib = merged_map.get(lib_id, {})
        for key in set(dlib.keys()) | set(mlib.keys()):
            dval = dlib.get(key)
            mval = mlib.get(key)
            if dval != mval:
                diff_counts[key] = diff_counts.get(key, 0) + 1
                if key not in diff_examples:
                    diff_examples[key] = (lib_id, dlib.get('name', '?'), dlib.get('type', '?'))
    
    for k, v in sorted(diff_counts.items(), key=lambda x: -x[1]):
        ex = diff_examples[k]
        print(f"  {k}: differs in {v} libs (e.g. lib {ex[0]} '{ex[1]}' type={ex[2]})")
    
    if not diff_counts:
        print("  No differences! Merge perfectly restores all data.")
    
    # Now compile both: pure Python roundtrip vs simulated web roundtrip
    print("\n=== Compiling both versions ===")
    from compilation_pipeline import CompilationContext, create_default_pipeline
    shared_dir = os.path.join(os.path.dirname(__file__), 'shared')
    
    # Pure Python
    pure_path = os.path.join(tempfile.gettempdir(), "fox_pure_rt.swf")
    ctx1 = CompilationContext(n2d_path=n2d_path, shared_dir=shared_dir, output_path=pure_path)
    p1 = create_default_pipeline()
    p1.execute(ctx1)
    
    # Simulated web (use merged data override)
    web_path = os.path.join(tempfile.gettempdir(), "fox_web_rt.swf")
    ctx2 = CompilationContext(n2d_path=n2d_path, shared_dir=shared_dir, output_path=web_path,
                              data_override=merged, project_dir_override=None)
    p2 = create_default_pipeline()
    p2.execute(ctx2)
    
    with open(pure_path, 'rb') as f: pure_bytes = f.read()
    with open(web_path, 'rb') as f: web_bytes = f.read()
    
    print(f"\n=== SWF Size Comparison ===")
    print(f"  Pure Python: {len(pure_bytes):,} bytes")
    print(f"  Simulated web: {len(web_bytes):,} bytes")
    print(f"  Difference: {len(web_bytes) - len(pure_bytes):+,} bytes")
    
    if pure_bytes == web_bytes:
        print("  SWF files are IDENTICAL!")
    else:
        # Find first difference
        for i in range(min(len(pure_bytes), len(web_bytes))):
            if pure_bytes[i] != web_bytes[i]:
                print(f"  First byte difference at offset {i}")
                break
        
        # Compare tag-level
        pure_data = decompress_swf(pure_bytes)
        web_data = decompress_swf(web_bytes)
        pure_tags = parse_tags_raw(pure_data, get_offset(pure_data))
        web_tags = parse_tags_raw(web_data, get_offset(web_data))
        
        print(f"  Pure tags: {len(pure_tags)}, Web tags: {len(web_tags)}")
        
        # Compare tag by tag
        tag_diffs = 0
        for i in range(min(len(pure_tags), len(web_tags))):
            pt, pb = pure_tags[i]
            wt, wb = web_tags[i]
            if pt != wt or pb != wb:
                tag_diffs += 1
                if tag_diffs <= 20:
                    if pt != wt:
                        print(f"  Tag {i}: type differs Pure={pt} Web={wt}")
                    elif len(pb) != len(wb):
                        print(f"  Tag {i} (type {pt}): size differs Pure={len(pb)} Web={len(wb)}")
                    else:
                        # Same type, same size, different content
                        diff_bytes = sum(1 for a, b in zip(pb, wb) if a != b)
                        # Identify tag for sprites
                        if pt == 39 and len(pb) >= 2:
                            cid = struct.unpack_from('<H', pb, 0)[0]
                            wcid = struct.unpack_from('<H', wb, 0)[0]
                            print(f"  Tag {i} DefineSprite: Pure cid={cid} Web cid={wcid}, {diff_bytes} bytes differ")
                        else:
                            print(f"  Tag {i} (type {pt}): {diff_bytes}/{len(pb)} bytes differ")
        
        if tag_diffs > 20:
            print(f"  ... {tag_diffs - 20} more tag differences")
        print(f"  Total tags with differences: {tag_diffs}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
