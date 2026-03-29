import swf_to_n2d, struct

path = r'C:\Users\glwex\AppData\Local\Temp\MicrosoftEdgeDownloads\b2655a24-55f5-4204-84a5-87bd47832f87\project.swf'
try:
    with open(path, 'rb') as f:
        data = f.read()
except Exception as e:
    print('Cannot open:', e)
    exit()

header, tags = swf_to_n2d.parse_swf(data)
print('Tags:', len(tags), '  Stage:', header['width'], 'x', header['height'])

sprite_names = {}
for t in tags:
    if t.tag_type == 76:
        sprite_names.update(swf_to_n2d.parse_symbol_class(t.data))

# Find large shapes
big = []
all_shapes = []
for t in tags:
    if t.tag_type in (2, 22, 32, 83):
        try:
            cid, bounds = swf_to_n2d.parse_define_shape_bounds(t.data)
            w = bounds['xMax'] - bounds['xMin']
            h = bounds['yMax'] - bounds['yMin']
            name = sprite_names.get(cid, '')
            all_shapes.append((cid, name, w, h, bounds))
            if w > 500 or h > 500:
                big.append((max(w, h), cid, name, w, h, bounds))
        except Exception as e:
            print('  parse error cid=?:', e)

big.sort(key=lambda x: -x[0])
print('\nShapes with bounds > 500px:')
for _, cid, name, w, h, b in big[:20]:
    print('  cid=%d name="%s" w=%.1f h=%.1f xMin=%.1f xMax=%.1f yMin=%.1f yMax=%.1f' % (
        cid, name, w, h, b['xMin'], b['xMax'], b['yMin'], b['yMax']))
print('Total oversized:', len(big), '/ total shapes:', len(all_shapes))

# Also look for the explode circle
print('\n--- Searching for "explode" or "circle" in names ---')
for cid, name, w, h, b in all_shapes:
    if 'explode' in name.lower() or 'circle' in name.lower() or 'Circle' in name:
        print('  cid=%d name="%s" w=%.1f h=%.1f' % (cid, name, w, h))
