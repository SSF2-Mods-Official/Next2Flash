"""Compare SWF headers: version, frame rate, frame size."""
import struct, zlib

OG_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\blackmage.ssf"
RT_PATH = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\blackmage.ssf"

for label, path in [("OG", OG_PATH), ("RT", RT_PATH)]:
    with open(path, 'rb') as f:
        d = f.read(32)
    sig = d[:3]
    version = d[3]
    file_len = struct.unpack_from('<I', d, 4)[0]
    # After decompression if CWS
    if sig == b'CWS':
        full = b'FWS' + d[3:8] + zlib.decompress(open(path,'rb').read()[8:])
    else:
        full = d + open(path,'rb').read(file_len)
    frame_rate_raw = struct.unpack_from('<H', full, 5 + ((full[5]*2+7)//8*8//8) if False else 0, 0)[0]
    # Parse properly
    # SWF structure after signature+version+size:
    # Next is RECT (frame size), then UI16 FrameRate, UI16 FrameCount
    bit_off = 64  # bits, after signature(3)+version(1)+fileLength(4) = 8 bytes = 64 bits
    nbits = ((full[8] >> 3) & 0x1F)
    total_bits = 5 + nbits*4
    byte_end = 8 + (total_bits + 7) // 8
    frame_rate = struct.unpack_from('<H', full, byte_end)[0]
    frame_count = struct.unpack_from('<H', full, byte_end+2)[0]
    print(f"{label}: sig={sig} version={version} file_len={file_len} frame_rate={frame_rate/256:.1f} fps frame_count={frame_count}")
    
    # Also check the FrameLabel for "a_air_down" to make sure it's defined
    start = skip_hdr_full(full)
    showframe_count = 0
    label_found = None
    for tt, body in pparse_tags(full, start):
        if tt == 43:  # FrameLabel
            label_str = body[:body.index(b'\x00')].decode('utf-8','replace')
            if 'air_down' in label_str.lower() or 'dair' in label_str.lower():
                label_found = label_str
        if tt == 1: showframe_count += 1
        if tt == 0: break
    print(f"   Relevant frame label found: {label_found}")

def skip_hdr_full(d):
    bit_off = 64
    first = d[8]
    nbits = (first >> 3) & 0x1F
    total_bits = 5 + nbits*4
    byte_end = 8 + (total_bits + 7) // 8
    return byte_end + 4  # skip FrameRate and FrameCount

def pparse_tags(data, start):
    off = start
    while off < len(data):
        if off+2 > len(data): break
        hdr = struct.unpack_from('<H',data,off)[0]; tt=hdr>>6; ln=hdr&0x3F; off+=2
        if ln==0x3F: ln=struct.unpack_from('<I',data,off)[0]; off+=4
        body = data[off:off+ln]
        yield tt, body; off+=ln
        if tt==0: break
