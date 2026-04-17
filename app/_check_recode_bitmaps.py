"""Check if N2D shape recodes contain inline bitmap data (dicts) vs integer refs."""
import sys, os, json, zipfile
try:
    import msgpack
except ImportError:
    msgpack = None

# Recode commands from swf_constants
BITMAP_FILL = 13
BITMAP_STROKE = 14

def scan_recodes(recodes, shapes_with_inline, shapes_with_refs, shape_name):
    """Scan a recode buffer for bitmap fills by simple sequential search."""
    if not recodes:
        return
    for i, val in enumerate(recodes):
        if isinstance(val, bool) or isinstance(val, str):
            continue
        try:
            cmd = int(val)
        except (ValueError, TypeError):
            continue
        if cmd != BITMAP_FILL:
            continue
        # Found BITMAP_FILL command at position i
        if i + 1 >= len(recodes):
            continue
        bmp_val = recodes[i + 1]
        if isinstance(bmp_val, dict):
            buf = bmp_val.get('buffer', [])
            buf_len = len(buf) if buf else 0
            bmp_id = bmp_val.get('bitmapId', 0)
            w = bmp_val.get('width', 0)
            h = bmp_val.get('height', 0)
            if shapes_with_inline['count'] < 5:
                print(f"  INLINE: shape='{shape_name}' bitmapId={bmp_id} {w}x{h} buf_len={buf_len}")
            shapes_with_inline['count'] += 1
        elif isinstance(bmp_val, (int, float)) and not isinstance(bmp_val, bool):
            # Check if next item is a list (matrix) → rich format with int ref
            if i + 2 < len(recodes) and isinstance(recodes[i + 2], list):
                shapes_with_refs['count'] += 1
            else:
                # Could be flat format width val — harder to distinguish
                shapes_with_refs['count'] += 1  # assume ref

def main():
    project_dir = sys.argv[1]
    n2d_path = os.path.join(project_dir, 'project.n2d')
    
    with zipfile.ZipFile(n2d_path) as zf:
        if 'project.msgpack' in zf.namelist() and msgpack:
            data = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
        else:
            data = json.loads(zf.read('project.json'))

    libs = data.get('libraries', [])
    shapes = [l for l in libs if l and l.get('type') == 'shape' and not l.get('isFont') and not l.get('isButton') and not l.get('isBinaryData')]
    
    print(f"Total shapes to scan: {len(shapes)}")
    
    inline_counter = {'count': 0}
    ref_counter = {'count': 0}
    shapes_with_bitmap = 0
    
    for lib in shapes:
        recodes = lib.get('recodes', [])
        if not recodes:
            continue
        
        # Scan for BITMAP_FILL commands
        has_bitmap = False
        for i, val in enumerate(recodes):
            if isinstance(val, (int, float)) and not isinstance(val, bool) and int(val) == BITMAP_FILL:
                has_bitmap = True
                break
        
        if has_bitmap:
            shapes_with_bitmap += 1
            scan_recodes(recodes, inline_counter, ref_counter, lib.get('name', '?'))
    
    print(f"\nShapes with bitmap fills: {shapes_with_bitmap}")
    print(f"Bitmap fill instances - INLINE (dict): {inline_counter['count']}")
    print(f"Bitmap fill instances - REF (int): {ref_counter['count']}")
    
    # Also check morph shapes
    morphs = [l for l in libs if l and l.get('isMorphShape')]
    print(f"\nMorph shapes: {len(morphs)}")
    morph_inline = {'count': 0}
    morph_ref = {'count': 0}
    for lib in morphs:
        for key in ('recodes', 'startRecodes', 'endRecodes'):
            recodes = lib.get(key, [])
            if recodes:
                scan_recodes(recodes, morph_inline, morph_ref, f"{lib.get('name','?')}/{key}")
    print(f"Morph bitmap fills - INLINE: {morph_inline['count']}")
    print(f"Morph bitmap fills - REF: {morph_ref['count']}")

if __name__ == '__main__':
    main()
