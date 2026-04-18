import msgpack, zipfile, io, struct, zlib

with open('converted/blackmage/project.n2d','rb') as f: raw=f.read()
with zipfile.ZipFile(io.BytesIO(raw)) as zf:
    doc = msgpack.unpackb(zf.read('project.msgpack'), raw=False)
libs = doc.get('libraries', [])
bm_libs = [l for l in libs if l.get('type')=='bitmap']

# Check if any bitmap has rawTagBody
with_raw = [l for l in bm_libs if l.get('rawTagBody')]
print(f'Bitmaps with rawTagBody: {len(with_raw)}')
# Check rawTagType
raw_types = set(l.get('rawTagType') for l in bm_libs)
print(f'Bitmap rawTagTypes: {sorted(raw_types)}')
# Check specifically dair bitmaps
dair_bm = [l for l in bm_libs if 'dair' in (l.get('name') or '').lower()]
for l in dair_bm[:3]:
    rtag = l.get('rawTagType')
    swfc = l.get('swfCharId')
    w = l.get('width')
    h = l.get('height')
    name = l.get('name')
    lid = l.get('id')
    print(f'  id={lid} name={name} rawTagType={rtag} swfCharId={swfc} w={w} h={h}')

# Count rawTagType=35 (JPEG3) bitmaps
jpeg3_bm = [l for l in bm_libs if l.get('rawTagType')==35]
print(f'\nBitmaps with rawTagType=35 (JPEG3): {len(jpeg3_bm)}')
# Check if any dair bitmaps are JPEG3
dair_jpeg3 = [l for l in dair_bm if l.get('rawTagType')==35]
print(f'Dair bitmaps with JPEG3: {len(dair_jpeg3)}')

# Find OG JPEG3 bitmaps from SWF
OG = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf'
with open(OG, 'rb') as f:
    raw_swf = f.read()
if raw_swf[:3] == b'CWS':
    raw_swf = raw_swf[:8] + zlib.decompress(raw_swf[8:])
pos = 8
nb = (raw_swf[pos] >> 3) & 0x1f
pos += (5 + nb * 4 + 7) // 8 + 4
jpeg3_ids = []
while pos < len(raw_swf)-1:
    hdr = struct.unpack_from('<H', raw_swf, pos)[0]
    tt = hdr >> 6
    sl = hdr & 0x3f
    pos += 2
    if sl == 0x3f:
        l = struct.unpack_from('<I', raw_swf, pos)[0]
        pos += 4
    else:
        l = sl
    pay = raw_swf[pos:pos+l]
    if tt == 0:
        break
    if tt == 35 and l >= 2:
        jpeg3_ids.append(struct.unpack_from('<H', pay)[0])
    pos += l
print(f'\nOG JPEG3 bitmaps ({len(jpeg3_ids)}): {jpeg3_ids[:20]}')
# Check if any dair bitmap swfCharIds are JPEG3 in OG
dair_swfc = set(l.get('swfCharId') for l in dair_bm)
dair_jpeg3_og = [cid for cid in jpeg3_ids if cid in dair_swfc]
print(f'Dair bitmaps that were JPEG3 in OG: {dair_jpeg3_og}')
