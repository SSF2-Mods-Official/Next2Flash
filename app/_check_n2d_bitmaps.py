"""Quick check: how many bitmap library entries in the project.n2d on disk?"""
import sys, os, json, zipfile, io
try:
    import msgpack
except ImportError:
    msgpack = None

def main():
    project_dir = sys.argv[1]
    n2d_path = os.path.join(project_dir, 'project.n2d')
    
    if not os.path.isfile(n2d_path):
        print(f"Not found: {n2d_path}")
        # Also check for project.json or bitmaps dir
        for f in os.listdir(project_dir):
            print(f"  {f}")
        return

    print(f"N2D file: {n2d_path} ({os.path.getsize(n2d_path):,} bytes)")
    
    with zipfile.ZipFile(n2d_path) as zf:
        names = zf.namelist()
        print(f"ZIP contents: {names}")
        
        if 'project.msgpack' in names and msgpack:
            data = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
        elif 'project.json' in names:
            data = json.loads(zf.read('project.json'))
        else:
            print("No project data found")
            return

    libs = data.get('libraries', [])
    print(f"\nTotal library entries: {len(libs)}")
    
    type_counts = {}
    for lib in libs:
        if not lib:
            continue
        t = lib.get('type', 'unknown')
        type_counts[t] = type_counts.get(t, 0) + 1
    
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")
    
    # Check bitmap entries specifically
    bitmaps = [l for l in libs if l and l.get('type') == 'bitmap']
    print(f"\nBitmap entries: {len(bitmaps)}")
    
    # Check for duplicate IDs
    ids = [b['id'] for b in bitmaps]
    unique_ids = set(ids)
    if len(ids) != len(unique_ids):
        print(f"  WARNING: {len(ids) - len(unique_ids)} duplicate IDs!")
    
    # Check for duplicate names
    names = [b.get('name', '') for b in bitmaps]
    name_counts = {}
    for n in names:
        name_counts[n] = name_counts.get(n, 0) + 1
    dupes = {k: v for k, v in name_counts.items() if v > 1}
    if dupes:
        print(f"  Duplicate names: {len(dupes)} groups")
        for name, count in sorted(dupes.items(), key=lambda x: -x[1])[:10]:
            print(f"    '{name}': {count}x")
    
    # Check buffer presence
    with_buffer = sum(1 for b in bitmaps if b.get('buffer'))
    without_buffer = sum(1 for b in bitmaps if not b.get('buffer'))
    print(f"  With buffer: {with_buffer}")
    print(f"  Without buffer: {without_buffer}")
    
    # Check external files
    with_ext = sum(1 for b in bitmaps if b.get('externalFile'))
    print(f"  With externalFile: {with_ext}")
    
    # Show a few samples
    print("\nSample bitmap entries (first 3):")
    for b in bitmaps[:3]:
        buf = b.get('buffer', '')
        buf_info = f"len={len(buf)}" if buf else "empty"
        print(f"  id={b.get('id')} name={b.get('name')} {b.get('width')}x{b.get('height')} "
              f"buffer={buf_info} ext={b.get('externalFile', '')}")

if __name__ == '__main__':
    main()
