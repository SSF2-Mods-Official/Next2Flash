"""Analyze sound tags in a SWF/SSF file."""
import struct, sys
from swf_binary_io import BitReader

path = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\mario.ssf'

with open(path, 'rb') as f:
    data = f.read()

sig = data[:3]
version = data[3]
file_len = struct.unpack_from('<I', data, 4)[0]
print(f'SWF version: {version}, size: {len(data):,} bytes')

br = BitReader(data, 8)
nbits = br.read_ub(5)
for _ in range(4):
    br.read_sb(nbits)
br.align()
rect_end = br.byte_pos
fps = struct.unpack_from('<H', data, rect_end)[0] / 256.0
frame_count = struct.unpack_from('<H', data, rect_end + 2)[0]
print(f'FPS: {fps}, Frames: {frame_count}')

sound_formats = {
    0: 'Raw PCM (native)', 1: 'ADPCM', 2: 'MP3',
    3: 'Raw PCM (LE)', 4: 'Nellymoser 16kHz',
    5: 'Nellymoser 8kHz', 6: 'Nellymoser', 11: 'Speex'
}
sample_rates = {0: 5512, 1: 11025, 2: 22050, 3: 44100}

offset = rect_end + 4
sounds = []
stream_heads = []
stream_blocks = 0
tag_counts = {}

while offset < len(data):
    tc = struct.unpack_from('<H', data, offset)[0]
    tag_type = tc >> 6
    tag_length = tc & 0x3F
    offset += 2
    if tag_length == 0x3F:
        tag_length = struct.unpack_from('<I', data, offset)[0]
        offset += 4

    tag_name = str(tag_type)
    tag_counts[tag_type] = tag_counts.get(tag_type, 0) + 1

    if tag_type == 14:  # DefineSound
        sound_id = struct.unpack_from('<H', data, offset)[0]
        flags = data[offset + 2]
        fmt = (flags >> 4) & 0xF
        rate_idx = (flags >> 2) & 0x3
        is_16bit = (flags >> 1) & 1
        is_stereo = flags & 1
        sample_count = struct.unpack_from('<I', data, offset + 3)[0]
        sounds.append({
            'id': sound_id,
            'format': fmt,
            'format_name': sound_formats.get(fmt, f'Unknown({fmt})'),
            'rate': sample_rates.get(rate_idx, 0),
            'bits': 16 if is_16bit else 8,
            'channels': 2 if is_stereo else 1,
            'samples': sample_count,
            'data_size': tag_length - 7
        })

    if tag_type in (18, 45):  # SoundStreamHead / SoundStreamHead2
        stream_byte = data[offset + 1]
        sfmt = (stream_byte >> 4) & 0xF
        srate = (stream_byte >> 2) & 0x3
        stream_heads.append({
            'format_name': sound_formats.get(sfmt, f'Unknown({sfmt})'),
            'rate': sample_rates.get(srate, 0),
            'format': sfmt
        })

    if tag_type == 19:
        stream_blocks += 1

    if tag_type == 0:
        break
    offset += tag_length

# Summary
fmt_summary = {}
for s in sounds:
    key = s['format_name']
    if key not in fmt_summary:
        fmt_summary[key] = []
    fmt_summary[key].append(s)

print(f'\n{"="*60}')
print(f'SOUND SUMMARY')
print(f'{"="*60}')
print(f'Total DefineSound tags: {len(sounds)}')
print(f'SoundStreamHead tags:   {len(stream_heads)}')
print(f'SoundStreamBlock tags:  {stream_blocks}')

print(f'\n--- By Format ---')
for fmt_name, items in fmt_summary.items():
    total_bytes = sum(s['data_size'] for s in items)
    print(f'  {fmt_name}: {len(items)} sounds, {total_bytes:,} bytes total')

print(f'\n--- All DefineSound Details ---')
for s in sounds:
    dur = s['samples'] / s['rate'] if s['rate'] else 0
    ch = 'stereo' if s['channels'] == 2 else 'mono'
    print(f"  ID {s['id']:>5}: {s['format_name']:<20} {s['rate']:>5}Hz {s['bits']:>2}bit {ch:<6} {s['samples']:>8,} samples ({dur:>6.2f}s)  data: {s['data_size']:>8,} bytes")

if stream_heads:
    print(f'\n--- Stream Heads ---')
    for sh in stream_heads:
        print(f"  {sh['format_name']} at {sh['rate']}Hz")
