"""Validate SWF file structure."""
import struct, zlib, sys

def validate_swf(path):
    raw = open(path, 'rb').read()
    print(f'File size: {len(raw)}')
    print(f'Magic: {raw[:3]}')
    print(f'Version: {raw[3]}')
    file_len = struct.unpack_from('<I', raw, 4)[0]
    print(f'Declared length: {file_len}')
    data = raw
    if raw[:3] == b'CWS':
        data = raw[:8] + zlib.decompress(raw[8:])
    elif raw[:3] == b'FWS':
        pass
    else:
        print(f'Unknown magic: {raw[:3].hex()}')
        return
    print(f'Decompressed length: {len(data)} (declared: {file_len})')
    nbits = (data[8] >> 3) & 0x1f
    total_bits = 5 + nbits * 4
    rect_end = 8 + (total_bits + 7) // 8
    tag_start = rect_end + 4
    print(f'Rect nbits={nbits}, tag_start={tag_start}')

    tags = []
    i = tag_start
    while i < len(data):
        if i + 2 > len(data): break
        h = struct.unpack_from('<H', data, i)[0]
        tt = h >> 6
        ln = h & 0x3f
        hdr = 2
        if ln == 0x3f:
            ln = struct.unpack_from('<I', data, i+2)[0]
            hdr = 6
        if i + hdr + ln > len(data):
            print(f'Tag {tt} at {i}: overflows by {(i+hdr+ln)-len(data)} bytes')
            break
        tags.append((tt, i, hdr, ln, data[i+hdr:i+hdr+ln]))
        i += hdr + ln
        if tt == 0: break
    print(f'Tags: {len(tags)}')

    # Sprite validation
    sprite_errs = 0
    for tt, off, hdr, ln, body in tags:
        if tt == 39 and len(body) >= 4:
            cid = struct.unpack_from('<H', body, 0)[0]
            fc = struct.unpack_from('<H', body, 2)[0]
            j = 4
            found_end = False
            while j < len(body):
                if j + 2 > len(body): break
                nh = struct.unpack_from('<H', body, j)[0]
                ntt = nh >> 6
                nln = nh & 0x3f
                nhdr = 2
                if nln == 0x3f:
                    if j + 6 > len(body): break
                    nln = struct.unpack_from('<I', body, j+2)[0]
                    nhdr = 6
                j += nhdr + nln
                if ntt == 0:
                    found_end = True
                    break
            if not found_end:
                print(f'  Sprite {cid}: NO END TAG (fc={fc})')
                sprite_errs += 1
            if j != len(body) and found_end:
                print(f'  Sprite {cid}: {j}/{len(body)} bytes consumed')
                sprite_errs += 1
    print(f'Sprite errors: {sprite_errs}')

    # DoABC2 validation
    for tt, off, hdr, ln, body in tags:
        if tt == 82 and len(body) > 4:
            flags = struct.unpack_from('<I', body, 0)[0]
            null_idx = body.find(0, 4)
            if null_idx < 0:
                print('DoABC2: no name null terminator!')
            else:
                name = body[4:null_idx].decode('utf-8', 'replace')
                abc = body[null_idx+1:]
                print(f'DoABC2: flags={flags} name="{name}" abc_len={len(abc)}')
                if len(abc) >= 4:
                    minor, major = struct.unpack_from('<HH', abc, 0)
                    print(f'  ABC version: {major}.{minor}')

    # First 10 tags
    TAG_NAMES = {0:'End',1:'ShowFrame',2:'DefineShape',9:'SetBgColor',
        20:'DefineBitsLossless',21:'DefineBitsJPEG2',22:'DefineShape2',
        24:'Protect',26:'PlaceObject2',28:'RemoveObject2',32:'DefineShape3',
        35:'DefineBitsJPEG3',36:'DefineBitsLossless2',39:'DefineSprite',
        43:'FrameLabel',45:'SoundStreamHead2',46:'MorphShape',48:'DefineFont2',
        56:'ExportAssets',69:'FileAttributes',70:'PlaceObject3',72:'DoABC',
        73:'FontAlignZones',74:'CSMTextSettings',75:'DefineFont3',
        76:'SymbolClass',82:'DoABC2',83:'DefineShape4',84:'MorphShape2',
        86:'SceneFrameLabel',87:'DefineBinaryData',88:'DefineFontName'}
    print("\nFirst 15 tags:")
    for tt, off, hdr, ln, body in tags[:15]:
        name = TAG_NAMES.get(tt, f'tag{tt}')
        cid_str = ""
        if len(body) >= 2 and tt in {2,22,32,83,6,21,35,90,20,36,39,46,84,11,48,75,10,14,37,87}:
            cid = struct.unpack_from('<H', body, 0)[0]
            cid_str = f' charId={cid}'
        first_bytes = body[:20].hex() if body else ''
        print(f'  [{off}] {name}(type={tt}){cid_str} len={ln} body={first_bytes}')

print('=== ROUNDTRIP SWF ===')
validate_swf('_roundtrip_test.swf')
print()
print('=== ORIGINAL SSF ===')
validate_swf(r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.ssf')
