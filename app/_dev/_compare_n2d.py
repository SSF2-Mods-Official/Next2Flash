"""Compare two N2D files to find differences."""
import json, zipfile, zlib, sys, os
from urllib.parse import unquote

def load_n2d(path):
    with open(path, 'rb') as f:
        raw = f.read()
    # Try ZIP first
    if raw[:2] == b'PK':
        with zipfile.ZipFile(path, 'r') as zf:
            return json.loads(zf.read('project.json'))
    # Try zlib
    if raw[:2] in (b'\x78\x9c', b'\x78\x01', b'\x78\xda'):
        text = zlib.decompress(raw).decode('utf-8')
        # May be URL-encoded
        if text.startswith('%7B'):
            text = unquote(text)
        return json.loads(text)
    # Try raw JSON
    text = raw.decode('utf-8')
    if text.startswith('%7B'):
        text = unquote(text)
    return json.loads(text)

cli_path = r'C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\gameandwatch_cli.n2d'
browser_path = r'C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\_last_export.n2d'

print("Loading CLI N2D...")
cli = load_n2d(cli_path)
print("Loading Browser N2D...")
browser = load_n2d(browser_path)

# Top-level keys
print("\n=== TOP-LEVEL KEYS ===")
for key in sorted(set(list(cli.keys()) + list(browser.keys()))):
    cv = cli.get(key)
    bv = browser.get(key)
    if isinstance(cv, (list, dict)):
        cs = f"len={len(cv)}"
    else:
        cs = repr(cv)[:80]
    if isinstance(bv, (list, dict)):
        bs = f"len={len(bv)}"
    else:
        bs = repr(bv)[:80]
    match = "OK" if cs == bs else "DIFF"
    print(f"  [{match}] {key}: cli={cs}  browser={bs}")

# Compare libraries
cli_libs = {lib.get('name', lib.get('id')): lib for lib in cli.get('libraries', [])}
browser_libs = {lib.get('name', lib.get('id')): lib for lib in browser.get('libraries', [])}

print(f"\n=== LIBRARIES ===")
print(f"CLI: {len(cli_libs)} libraries")
print(f"Browser: {len(browser_libs)} libraries")

# Find missing/extra
cli_names = set(cli_libs.keys())
browser_names = set(browser_libs.keys())
missing = cli_names - browser_names
extra = browser_names - cli_names
print(f"Missing from browser: {len(missing)}")
if missing:
    for n in sorted(missing)[:20]:
        lib = cli_libs[n]
        print(f"  - {n} (type={lib.get('type')}, id={lib.get('id')})")
    if len(missing) > 20:
        print(f"  ... and {len(missing)-20} more")
print(f"Extra in browser: {len(extra)}")
if extra:
    for n in sorted(extra)[:20]:
        lib = browser_libs[n]
        print(f"  + {n} (type={lib.get('type')}, id={lib.get('id')})")

# Compare common libraries - check critical fields
print(f"\n=== CRITICAL FIELD COMPARISON (common libs) ===")
common = cli_names & browser_names
field_diffs = {}
missing_rawTagBody = []
missing_rawTagType = []
missing_swfCharId = []
missing_fontAuxTags = []
empty_controller = []
wrong_totalFrame = []

for name in sorted(common):
    cl = cli_libs[name]
    bl = browser_libs[name]
    
    # Check rawTagBody
    if cl.get('rawTagBody') and not bl.get('rawTagBody'):
        missing_rawTagBody.append(name)
    
    # Check rawTagType
    if cl.get('rawTagType') and not bl.get('rawTagType'):
        missing_rawTagType.append(name)
    
    # Check swfCharId
    if cl.get('swfCharId') is not None and bl.get('swfCharId') is None:
        missing_swfCharId.append(name)
    
    # Check fontAuxTags
    if cl.get('fontAuxTags') and not bl.get('fontAuxTags'):
        missing_fontAuxTags.append(name)
    
    # Check totalFrame
    ct = cl.get('totalFrame', 1)
    bt = bl.get('totalFrame', 1)
    if ct != bt:
        wrong_totalFrame.append((name, ct, bt))
    
    # Check controller
    cc = cl.get('controller', {})
    bc = bl.get('controller', {})
    if cc and not bc:
        empty_controller.append(name)

print(f"Missing rawTagBody: {len(missing_rawTagBody)} / {len(common)}")
for n in missing_rawTagBody[:10]:
    cl = cli_libs[n]
    print(f"  {n} (type={cl.get('type')}, rawTagType={cl.get('rawTagType')})")
if len(missing_rawTagBody) > 10: print(f"  ... and {len(missing_rawTagBody)-10} more")

print(f"Missing rawTagType: {len(missing_rawTagType)}")
for n in missing_rawTagType[:5]:
    print(f"  {n}")

print(f"Missing swfCharId: {len(missing_swfCharId)}")
for n in missing_swfCharId[:5]:
    print(f"  {n}")

print(f"Missing fontAuxTags: {len(missing_fontAuxTags)}")
for n in missing_fontAuxTags[:5]:
    print(f"  {n}")

print(f"Empty controller (cli has, browser empty): {len(empty_controller)}")
for n in empty_controller[:5]:
    print(f"  {n} (cli frames: {list(cli_libs[n].get('controller',{}).keys())[:5]})")

print(f"Wrong totalFrame: {len(wrong_totalFrame)}")
for n, ct, bt in wrong_totalFrame[:10]:
    print(f"  {n}: cli={ct} browser={bt}")

# Compare scripts
print(f"\n=== SCRIPTS ===")
cli_scripts = cli.get('scripts', [])
browser_scripts = browser.get('scripts', [])
print(f"CLI scripts: {len(cli_scripts)}")
print(f"Browser scripts: {len(browser_scripts)}")

# Compare rawGlobalTags
print(f"\n=== RAW GLOBAL TAGS ===")
cli_rgt = cli.get('rawGlobalTags', [])
browser_rgt = browser.get('rawGlobalTags', [])
print(f"CLI rawGlobalTags: {len(cli_rgt)}")
print(f"Browser rawGlobalTags: {len(browser_rgt)}")
if cli_rgt:
    print("CLI rawGlobalTags types:")
    for t in cli_rgt[:10]:
        print(f"  type={t.get('type')} len={len(t.get('body',''))//2 if t.get('body') else 0}")
if browser_rgt:
    print("Browser rawGlobalTags types:")
    for t in browser_rgt[:10]:
        print(f"  type={t.get('type')} len={len(t.get('body',''))//2 if t.get('body') else 0}")

# Check main timeline
print(f"\n=== MAIN TIMELINE ===")
for key in ['stage', 'controller']:
    cv = cli.get(key)
    bv = browser.get(key)
    if isinstance(cv, dict) and isinstance(bv, dict):
        print(f"\n  {key}:")
        for k2 in sorted(set(list(cv.keys()) + list(bv.keys()))):
            c2 = cv.get(k2)
            b2 = bv.get(k2)
            if isinstance(c2, (list, dict)):
                c2s = f"len={len(c2)}"
            else:
                c2s = repr(c2)[:60]
            if isinstance(b2, (list, dict)):
                b2s = f"len={len(b2)}"
            else:
                b2s = repr(b2)[:60]
            m = "OK" if c2s == b2s else "DIFF"
            print(f"    [{m}] {k2}: cli={c2s}  browser={b2s}")
