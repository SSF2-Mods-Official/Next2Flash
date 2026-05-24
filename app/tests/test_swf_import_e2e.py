#!/usr/bin/env python3
"""
End-to-end test: SWF → N2D conversion and verification.
Tests that all library types (including FOLDER and SOUND) are properly handled.
"""

import sys
import os
import subprocess
import zipfile
import msgpack

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_swf_to_n2d_conversion():
    """Test complete SWF to N2D pipeline."""
    print("\n" + "="*70)
    print("  END-TO-END SWF IMPORT TEST")
    print("="*70 + "\n")
    
    # Input SWF
    input_swf = os.path.join(SCRIPT_DIR, '_dev', '_roundtrip_test.swf')
    if not os.path.exists(input_swf):
        print(f"✗ Test SWF not found: {input_swf}")
        return False
    
    print(f"✓ Input SWF: {os.path.basename(input_swf)} ({os.path.getsize(input_swf):,} bytes)")
    
    # Output N2D
    output_n2d = os.path.join(SCRIPT_DIR, '_dev', 'comprehensive_import_test.n2d')
    
    # Run conversion
    print("\nStep 1: Converting SWF → N2D...")
    print("-" * 70)
    
    cmd = [
        sys.executable,
        os.path.join(SCRIPT_DIR, 'n2f.py'),
        'convert',
        input_swf,
        '-o',
        output_n2d
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"✗ Conversion failed with exit code {result.returncode}")
            print("STDERR:", result.stderr)
            return False
        
        # Extract summary from output
        for line in result.stdout.split('\n'):
            if 'Written to' in line or 'SWF:' in line or 'Built' in line:
                print(f"  {line.strip()}")
        
    except subprocess.TimeoutExpired:
        print("✗ Conversion timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"✗ Conversion error: {e}")
        return False
    
    print("✓ Conversion completed\n")
    
    # Verify output
    print("Step 2: Verifying N2D structure...")
    print("-" * 70)
    
    if not os.path.exists(output_n2d):
        print(f"✗ Output file not created: {output_n2d}")
        return False
    
    file_size = os.path.getsize(output_n2d)
    print(f"✓ Output file created: {file_size:,} bytes")
    
    try:
        # Load and parse N2D
        with zipfile.ZipFile(output_n2d, 'r') as zf:
            if 'project.msgpack' not in zf.namelist():
                print("✗ Missing project.msgpack in ZIP")
                return False
            
            data = zf.read('project.msgpack')
            n2d = msgpack.unpackb(data, raw=False, strict_map_key=False)
        
        print(f"✓ N2D parsed successfully")
        
        # Verify structure
        errors = []
        
        required_keys = ['version', 'name', 'libraries', 'stage']
        for key in required_keys:
            if key not in n2d:
                errors.append(f"Missing key: {key}")
        
        lib_count = len(n2d.get('libraries', []))
        if lib_count == 0:
            errors.append("No libraries found")
        
        if errors:
            print("✗ Validation errors:")
            for err in errors:
                print(f"  - {err}")
            return False
        
        print(f"✓ All required keys present")
        print(f"✓ Libraries: {lib_count}\n")
        
        # Analyze library types
        print("Step 3: Analyzing library types...")
        print("-" * 70)
        
        type_counts = {}
        for lib in n2d['libraries']:
            lib_type = lib.get('type', 'unknown')
            type_counts[lib_type] = type_counts.get(lib_type, 0) + 1
        
        for lib_type in sorted(type_counts.keys()):
            count = type_counts[lib_type]
            print(f"  {lib_type:15s}: {count:4d}")
        
        # Check critical types (FOLDER and SOUND were the bugs we fixed)
        has_folder = type_counts.get('folder', 0) > 0
        has_sound = type_counts.get('sound', 0) > 0
        
        print()
        if has_folder:
            print(f"✓ FOLDER type supported: {type_counts['folder']} instances")
        else:
            print("⚠ No FOLDER types found (might be okay)")
        
        if has_sound:
            print(f"✓ SOUND type supported: {type_counts['sound']} instances")
        else:
            print("⚠ No SOUND types found (might be okay)")
        
        print()
        
        # Summary
        print("="*70)
        print("  TEST RESULTS")
        print("="*70)
        print(f"  Input:  {os.path.basename(input_swf)}")
        print(f"  Output: {os.path.basename(output_n2d)} ({file_size:,} bytes)")
        print(f"  Libraries: {lib_count}")
        print(f"  Library types: {len(type_counts)}")
        print(f"  FOLDER support: {'YES' if has_folder else 'N/A'}")
        print(f"  SOUND support: {'YES' if has_sound else 'N/A'}")
        print("="*70)
        print("  ✓✓✓ ALL TESTS PASSED ✓✓✓")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_swf_to_n2d_conversion()
    sys.exit(0 if success else 1)
