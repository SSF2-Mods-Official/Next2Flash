"""Diagnostic: count bitmap library entries in blackmage project.n2d"""
import sys, os
sys.path.insert(0, '.')
from compile_n2d import load_n2d

n2d_path = r'converted\blackmage\project.n2d'
data, project_dir = load_n2d(n2d_path)

libs = data.get('libraries', [])
bitmap_libs = [l for l in libs if l.get('type') == 'bitmap']
bitmap_with_external = [l for l in bitmap_libs if l.get('externalFile')]
bitmap_with_buffer = [l for l in bitmap_libs if l.get('buffer') and not l.get('externalFile')]

print(f"Total libs: {len(libs)}")
print(f"Type=bitmap libs: {len(bitmap_libs)}")
print(f"  With externalFile: {len(bitmap_with_external)}")
print(f"  With buffer only: {len(bitmap_with_buffer)}")
print(f"  Neither: {len(bitmap_libs) - len(bitmap_with_external) - len(bitmap_with_buffer)}")
print(f"\nproject_dir: {project_dir}")

# Check how many external files actually exist
if project_dir:
    existing = sum(1 for l in bitmap_with_external 
                  if os.path.exists(os.path.join(project_dir, l.get('externalFile',''))))
    print(f"External files that exist: {existing}/{len(bitmap_with_external)}")
