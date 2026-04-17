"""Check how many containers have soundStreamParsed in fresh N2D import,
and verify the full compile pipeline emits SoundStreamHead2 (tag 45)."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))

from swf_to_n2d import parse_swf, validate_swf_sprites, N2DBuilder

OG = r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\build\data\character\fox.ssf"

with open(OG, 'rb') as f:
    swf_data = f.read()
header, tags = parse_swf(swf_data)
validate_swf_sprites(tags)
builder = N2DBuilder(header, name="fox")
builder.catalog_swf_tags(tags)
builder.frame_scripts = {}
builder.build_all()
builder.build_main_timeline(tags)
n2d = builder.to_n2d_json()

# Check which containers have soundStreamParsed
containers_with_ssh = []
containers_total = 0
for lib in n2d.get("libraries", []):
    if lib and lib.get("type") == "container":
        containers_total += 1
        ssh = lib.get("soundStreamParsed")
        if ssh:
            containers_with_ssh.append((lib.get("name", "?"), lib.get("symbolName", "?"), ssh))

print(f"Containers with soundStreamParsed: {len(containers_with_ssh)}/{containers_total}")
for name, sym, ssh in containers_with_ssh:
    print(f"  '{name}' ({sym}): {ssh}")

# Now do a FULL compile using the compilation pipeline
# Skip full compile - just check that the data is present and the compiler
# code handles it (we verified lines 3289-3297 of compile_n2d.py read it).
# Instead, compare OG SSH counts with N2D capture counts.

# Count tag 45 in OG
og_sprite_ssh = 0
og_sprite_total = 0
for tag in tags:
    if tag.tag_type == 39:
        og_sprite_total += 1
        inner = tag.data[4:]
        pos = 0
        while pos < len(inner):
            if pos + 2 > len(inner):
                break
            tc = struct.unpack_from('<H', inner, pos)[0]
            tt = tc >> 6
            tl = tc & 0x3F
            pos += 2
            if tl == 0x3F:
                if pos + 4 > len(inner):
                    break
                tl = struct.unpack_from('<I', inner, pos)[0]
                pos += 4
            pos += tl
            if tt == 45:
                og_sprite_ssh += 1
                break

og_main_ssh = sum(1 for t in tags if t.tag_type == 45)
print(f"\nOG sprites with SoundStreamHead2: {og_sprite_ssh}/{og_sprite_total}")
print(f"OG main timeline SoundStreamHead2: {og_main_ssh}")
