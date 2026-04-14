"""Quick test: full pipeline for mario.ssf sounds."""
from swf_to_n2d import parse_swf, N2DBuilder, decompile_all_scripts
import time

path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\mario.ssf'

with open(path, 'rb') as f:
    swf_data = f.read()

t0 = time.time()
header, tags = parse_swf(swf_data)
print(f'Parsed in {time.time()-t0:.1f}s: {len(tags)} tags')

builder = N2DBuilder(header, name='mario')
builder.catalog_swf_tags(tags)
sound_count = sum(1 for t in builder.char_types.values() if t == 'sound')
print(f'Cataloged: {sound_count} sounds')

# Set frame_scripts like the real pipeline does
try:
    scripts, frame_scripts = decompile_all_scripts(builder.global_raw_tags)
    builder.frame_scripts = frame_scripts
except Exception:
    builder.frame_scripts = {}

builder.build_all()
sounds = [e for e in builder.libraries if e.get('type') == 'sound']
print(f'Built: {len(sounds)} sound entries in {time.time()-t0:.1f}s')

fmts = {}
empty = 0
for s in sounds:
    f = s.get('soundFormat', '?')
    fmts[f] = fmts.get(f, 0) + 1
    if not s.get('buffer'):
        empty += 1

print(f'By format: {fmts}')
print(f'Empty buffers: {empty}')
for s in sounds[:5]:
    print(f"  {s['name']}: fmt={s['soundFormat']}, buf_len={len(s.get('buffer', ''))}")
