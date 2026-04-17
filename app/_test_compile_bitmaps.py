"""
Quick compile test: compile fox project and count bitmap tags in output SWF.
Expected: ~627 bitmaps (not 1506).
"""
import sys, os, struct, zlib, tempfile

sys.path.insert(0, os.path.dirname(__file__))

def count_bitmap_tags(swf_path):
    TAG_LL, TAG_LL2 = 20, 36
    count = 0
    with open(swf_path, 'rb') as f:
        sig = f.read(3)
        version = struct.unpack('<B', f.read(1))[0]
        file_len = struct.unpack('<I', f.read(4))[0]
        rest = f.read()
    if sig == b'CWS':
        rest = zlib.decompress(rest)
    nbits = rest[0] >> 3
    rect_bytes = (5 + 4 * nbits + 7) // 8
    offset = rect_bytes + 4
    while offset < len(rest):
        if offset + 2 > len(rest):
            break
        tc = struct.unpack_from('<H', rest, offset)[0]
        offset += 2
        tag_type = tc >> 6
        length = tc & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', rest, offset)[0]
            offset += 4
        offset += length
        if tag_type == 0:
            break
        if tag_type in (TAG_LL, TAG_LL2):
            count += 1
    return count

def main():
    project_dir = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\fox"
    n2d_path = os.path.join(project_dir, "project.n2d")
    shared_dir = os.path.join(os.path.dirname(__file__), "..", "shared")
    
    if not os.path.isdir(shared_dir):
        shared_dir = tempfile.mkdtemp()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "fox_test.swf")
        
        import compilation_pipeline as cp
        ctx = cp.CompilationContext(
            n2d_path=n2d_path,
            shared_dir=shared_dir,
            output_path=output_path,
            project_dir_override=project_dir,
        )
        pipeline = cp.create_default_pipeline()
        pipeline.execute(ctx)
        
        n_bitmaps = count_bitmap_tags(output_path)
        file_size = os.path.getsize(output_path)
        print(f"\n=== RESULT ===")
        print(f"Output: {output_path}")
        print(f"File size: {file_size:,} bytes")
        print(f"Bitmap tags: {n_bitmaps}")
        print(f"Expected: ~627")
        if n_bitmaps <= 650:
            print("STATUS: PASS - No bitmap explosion!")
        else:
            print(f"STATUS: FAIL - {n_bitmaps - 627} extra bitmaps")

if __name__ == '__main__':
    main()
