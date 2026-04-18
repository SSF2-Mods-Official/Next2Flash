"""Recompile blackmage using N2DCompiler and analyze the output."""
import sys, os
sys.path.insert(0, '.')

from compile_n2d import N2DCompiler

n2d_path = r'converted\blackmage\project.n2d'
output_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf'
shared_dir = r'converted\blackmage\scripts'

compiler = N2DCompiler(n2d_path, shared_dir, output_path)
compiler.compile()
print(f"\nCompiled to: {output_path}")
print(f"Size: {os.path.getsize(output_path)} bytes")
