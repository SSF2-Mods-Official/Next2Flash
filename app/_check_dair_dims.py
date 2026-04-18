"""Check dimensions of dair bitmaps in RT SWF vs PNG files."""
import struct, zlib, os

RT_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"
PNG_DIR = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\blackmage\bitmaps"
N2D_PATH = r"C:\Users\glwex\Documents\GitHub\Next2Flash\app\converted\blackmage\project.n2d"

def read_swf(p):
    d = open(p,'rb').read()
    if d[:3]==b'CWS': d = b'FWS'+d[3:8]+zlib.decompress(d[8:])
    return d

def prb(d,bo=0):
    bi=bo//8; bi2=bo%8; nb=0
    for i in range(5): nb=(nb<<1)|((d[bi+(bi2+i)//8]>>(7-(bi2+i)%8))&1)
    return 5+nb*4

def skip_hdr(d): return 8+(prb(d,64)+7)//8+4

data = read_swf(RT_PATH)
root_start = skip_hdr(data)

def parse_tags(data, start_off, end_off=None):
    off = start_off
    if end_off is None: end_off = len(data)
    while off < end_off:
        if off+2 > end_off: break
        hdr = struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; hdr_sz=2; off+=2
        if ln==0x3F:
            ln=struct.unpack_from('<I',data,off)[0]; off+=4; hdr_sz=6
        body = data[off:off+ln]
        yield tt, body, off-hdr_sz, ln
        off+=ln
        if tt==0: break

# Get SymbolClass
sym_class = {}
for tt, body, abs_off, ln in parse_tags(data, root_start):
    if tt == 76:
        count = struct.unpack_from('<H', body, 0)[0]
        off2 = 2
        for _ in range(count):
            cid = struct.unpack_from('<H', body, off2)[0]; off2 += 2
            end_str = body.index(b'\x00', off2)
            name = body[off2:end_str].decode('utf-8', errors='replace'); off2 = end_str+1
            sym_class[name] = cid; sym_class[cid] = name
        break

dair_cids = {sym_class[n]: n for n in sym_class if isinstance(n, str) and 'dair' in n.lower() and 'bm_' in n.lower()}
print(f"Dair bitmap charIds: {dair_cids}")

# Check LL2 tag dimensions
print("\n--- LL2 tag dimensions in RT SWF ---")
for tt, body, abs_off, ln in parse_tags(data, root_start):
    if tt == 36 and len(body) >= 7:  # DefineBitsLossless2
        cid = struct.unpack_from('<H', body, 0)[0]
        if cid in dair_cids:
            fmt = body[2]
            w = struct.unpack_from('<H', body, 3)[0]
            h = struct.unpack_from('<H', body, 5)[0]
            name = dair_cids[cid]
            print(f"  {name} (charId={cid}): fmt={fmt}, w={w}, h={h}, tag_size={ln}")

# Check N2D lib dimensions
print("\n--- N2D lib dimensions ---")
import sys; sys.path.insert(0, '.')
from compile_n2d import load_n2d
n2d_data, project_dir = load_n2d(N2D_PATH)
libs = n2d_data.get('libraries', [])
for lib in libs:
    if lib.get('type') == 'bitmap' and 'dair' in lib.get('name', '').lower() and 'bm_' in lib.get('name', '').lower():
        png = lib.get('externalFile', '')
        n2d_w = lib.get('width', -1)
        n2d_h = lib.get('height', -1)
        full_png = os.path.join(project_dir, png) if png else ''
        # Check actual PNG dims
        actual_w, actual_h = -1, -1
        if full_png and os.path.isfile(full_png):
            try:
                from PIL import Image
                img = Image.open(full_png)
                actual_w, actual_h = img.size
            except Exception as e:
                actual_w, actual_h = f"err:{e}", -1
        match = '✓' if (n2d_w == actual_w and n2d_h == actual_h) else f'MISMATCH! n2d={n2d_w}x{n2d_h} actual={actual_w}x{actual_h}'
        print(f"  {lib['name']}: n2d={n2d_w}x{n2d_h}, png={actual_w}x{actual_h}  {match}")
