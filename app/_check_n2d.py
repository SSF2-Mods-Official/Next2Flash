import zlib, json, struct, os
from urllib.parse import unquote

path = 'converted/gameandwatchOG/project.n2d'
data = open(path, 'rb').read()
print('File size:', len(data))
print('First 4 bytes:', data[:4].hex())

# Try zlib with wbits variants
for wbits in [15, -15, 47]:
    try:
        dec = zlib.decompress(data, wbits)
        text = dec.decode('utf-8')
        try:
            j = json.loads(unquote(text))
        except Exception:
            j = json.loads(text)
        bitmaps = [l for l in j.get('libraries', []) if l and l.get('type') == 'bitmap']
        print('wbits=%d: OK, total bitmaps=%d' % (wbits, len(bitmaps)))
        for b in bitmaps[:5]:
            ext = b.get('externalFile')
            buf = b.get('buffer', '')
            print('  id=%s externalFile=%r bufLen=%d' % (b.get('id'), ext, len(buf)))
        break
    except Exception as e:
        print('wbits=%d failed: %s' % (wbits, e))
