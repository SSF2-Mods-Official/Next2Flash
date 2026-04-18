"""Verify edit detection works - hash changes when bitmap is modified."""
import sys, json, zlib, base64, hashlib
sys.path.insert(0, '.')

with open('converted/blackmage/project.n2d', 'rb') as f:
    raw = f.read()
data = json.loads(zlib.decompress(raw).decode('utf-8'))

libs = data['libraries']
bitmaps = [l for l in libs if l.get('type') == 'bitmap']
dair = [b for b in bitmaps if b.get('symbol') == 'bm_dairHand']
if dair:
    b = dair[0]
    print(f"bm_dairHand: id={b['id']}, swfCharId={b.get('swfCharId')}, {b['width']}x{b['height']}")
    print(f"  rawTagType={b.get('rawTagType')}")
    print(f"  rawBitmapFormat={b.get('rawBitmapFormat')}")
    print(f"  bufferHash present: {bool(b.get('bufferHash'))}")
    print(f"  rawBitmapTagBody present: {bool(b.get('rawBitmapTagBody'))}")
    
    # Check hash match (unedited)
    buf = b['buffer']
    raw_b64 = buf[4:] if buf.startswith('b64:') else buf
    current_hash = hashlib.sha256(raw_b64.encode('ascii')).hexdigest()
    original_hash = b.get('bufferHash', '')
    print(f"  Hash match (unedited): {current_hash == original_hash}")
    
    # Simulate edit
    rgba = base64.b64decode(raw_b64)
    edited = bytearray(rgba)
    edited[0] = (edited[0] + 1) % 256
    new_b64 = base64.b64encode(bytes(edited)).decode('ascii')
    new_hash = hashlib.sha256(new_b64.encode('ascii')).hexdigest()
    print(f"  Hash match (edited): {new_hash == original_hash}")
    print(f"  Re-encode format will be: {b.get('rawBitmapFormat', 5)} (preserves OG)")
