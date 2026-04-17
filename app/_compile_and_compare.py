"""
Compile fox + deep compare against OG.
"""
import sys, os, struct, zlib, tempfile

sys.path.insert(0, os.path.dirname(__file__))

def main():
    project_dir = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\fox"
    n2d_path = os.path.join(project_dir, "project.n2d")
    shared_dir = os.path.join(os.path.dirname(__file__), "..", "shared")
    if not os.path.isdir(shared_dir):
        shared_dir = tempfile.mkdtemp()
    
    # Compile to a temp file
    output_path = os.path.join(tempfile.mkdtemp(), "fox_fresh.swf")
    
    import compilation_pipeline as cp
    ctx = cp.CompilationContext(
        n2d_path=n2d_path,
        shared_dir=shared_dir,
        output_path=output_path,
        project_dir_override=project_dir,
    )
    pipeline = cp.create_default_pipeline()
    pipeline.execute(ctx)
    
    print(f"\nFresh compile: {output_path}")
    print(f"Size: {os.path.getsize(output_path):,} bytes")
    
    # Now run deep compare
    og_path = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"
    
    # Import and run the comparison
    sys.argv = ['', og_path, output_path]
    exec(open('_deep_compare_sprites.py').read())

if __name__ == '__main__':
    main()
