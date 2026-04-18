"""Check N2D data for charID=1001."""
import re

with open('converted/blackmage/project.n2d', 'rb') as f:
    raw = f.read()

print('N2D header:', raw[:20].hex())
print('N2D size:', len(raw))

# N2D is likely msgpack or JSON
# Try msgpack
try:
    import msgpack
    data = msgpack.unpackb(raw, raw=False)
    print('Parsed as msgpack')
    # Find library with swfCharId=1001
    if isinstance(data, dict) and 'libraries' in data:
        for lib in data['libraries']:
            if lib.get('swfCharId') == 1001 or lib.get('id') == 1001:
                print('FOUND library for swfCharId=1001:')
                for k, v in lib.items():
                    if k != 'pixelData':
                        print(f'  {k}: {v}')
                    else:
                        pdata = v
                        if isinstance(pdata, (bytes, bytearray)):
                            print(f'  pixelData: {len(pdata)} bytes, first 20: {pdata[:20].hex()}')
                        else:
                            print(f'  pixelData type: {type(pdata)}')
                break
except ModuleNotFoundError:
    print('msgpack not available')
except Exception as e:
    print(f'msgpack error: {e}')

# Try JSON
try:
    import json
    text = raw.decode('utf-8', errors='replace')
    idx1 = text.find('1001')
    print(f'First occurrence of "1001": at offset {idx1}')
    # Look for rawTagType near swfCharId 1001
    matches = [m.start() for m in re.finditer(r'swfCharId.*?1001', text)]
    for m in matches[:3]:
        print(f'swfCharId=1001 context at {m}: {text[m:m+100]}')
except Exception as e:
    print(f'JSON error: {e}')
