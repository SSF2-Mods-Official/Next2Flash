#!/usr/bin/env python3
"""
Diagnostic script to test script normalization on a real SWF.
Shows how many scripts are detected, how many are linkage stubs, etc.
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import SWFImporter, normalize_imported_scripts, _is_linkage_stub

def test_normalization_on_swf(swf_path: str):
    """Test normalization on a real SWF file."""
    
    if not os.path.isfile(swf_path):
        print(f"ERROR: SWF not found: {swf_path}")
        return
    
    print(f"\n{'='*70}")
    print(f"Testing Script Normalization")
    print(f"{'='*70}")
    print(f"SWF: {swf_path}")
    print()
    
    # Parse SWF
    with open(swf_path, 'rb') as f:
        swf_data = f.read()
    
    importer = SWFImporter(swf_data, name=os.path.splitext(os.path.basename(swf_path))[0])
    header, tags = importer.parse_swf(swf_data)
    importer.catalog_swf_tags(tags)
    
    # Decompile scripts
    print("Decompiling AS3 scripts...")
    scripts, frame_scripts = importer.decompile_all_scripts(importer.global_raw_tags)
    importer.scripts.extend(scripts)
    print(f"Found {len(scripts)} scripts")
    print()
    
    # Analyze linkage stubs
    print("Analyzing scripts:")
    print("-" * 70)
    n_linkage = 0
    for idx, script in enumerate(scripts):
        is_stub = _is_linkage_stub(script.get('source', ''))
        origin = "LINKAGE STUB" if is_stub else "class-source (keep)"
        n_linkage += is_stub
        
        name = script.get('name', '?')
        path = script.get('path', '?')
        source_len = len(script.get('source', ''))
        
        if is_stub:
            print(f"[{idx:3d}] {origin:20s} | {name:30s} | src={source_len:5d}b")
    
    print("-" * 70)
    print(f"\nSummary:")
    print(f"  Total scripts decompiled: {len(scripts)}")
    print(f"  Linkage stubs detected:   {n_linkage}")
    print(f"  Real scripts to keep:     {len(scripts) - n_linkage}")
    print()
    
    # Now test normalization
    print("Running normalize_imported_scripts()...")
    importer.build_all()
    normalized = normalize_imported_scripts(scripts, importer.libraries)
    print(f"After normalization: {len(normalized)} scripts")
    print()
    
    # Show origins
    origins = {}
    for s in normalized:
        origin = s.get('scriptOrigin', 'unknown')
        origins[origin] = origins.get(origin, 0) + 1
    
    print("Scripts by origin:")
    for origin, count in sorted(origins.items()):
        print(f"  {origin:20s}: {count:3d}")
    print()
    
    # Percentage reduction
    reduction = (len(scripts) - len(normalized)) / len(scripts) * 100 if scripts else 0
    print(f"Reduction: {len(scripts)} → {len(normalized)} ({reduction:.1f}%)")
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Try common SWF locations
        from pathlib import Path
        home = Path.home()
        candidates = [
            home / "Documents" / "ssf2.swf",
            home / "Downloads" / "ssf2.swf",
            Path("c:/tmp/ssf2.swf"),
            Path("c:/tmp/donkeykong.swf"),
        ]
        
        found = False
        for candidate in candidates:
            if candidate.exists():
                print(f"Found SWF: {candidate}")
                test_normalization_on_swf(str(candidate))
                found = True
                break
        
        if not found:
            print("Usage: python test_script_normalization.py <swf_path>")
            print()
            print("Could not find test SWF. Specify path explicitly.")
    else:
        test_normalization_on_swf(sys.argv[1])
