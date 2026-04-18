"""N2D is a ZIP file (504b0304 = PK header). Inspect it."""
import zipfile, io, json, re, struct

with zipfile.ZipFile('converted/blackmage/project.n2d', 'r') as zf:
    print('ZIP contents:', zf.namelist()[:10])
    
    # Read project.json or similar
    for name in zf.namelist():
        if name.endswith('.json') or name == 'project.json':
            with zf.open(name) as f:
                text = f.read().decode('utf-8', errors='replace')
            print(f'JSON file: {name}, size={len(text)}')
            
            # Find rawTagType for swfCharId=1001
            matches = list(re.finditer(r'swfCharId["\s:]+1001', text))
            for m in matches[:3]:
                start = max(0, m.start()-5)
                end = min(len(text), m.end()+400)
                print(f'\nFound swfCharId=1001 context:')
                print(text[start:end][:500])
            
            if not matches:
                # Search for 1001 nearby rawTagType
                # Find all rawTagType values
                rt_matches = list(re.finditer(r'rawTagType["\s:]+(\d+)', text))
                print(f'Total rawTagType entries: {len(rt_matches)}')
                # Find around offset for 1001
                n1001 = text.find('"swfCharId"')
                print(f'First swfCharId mention at: {n1001}')
            break
    else:
        # Try all files
        for name in zf.namelist():
            print(f'File: {name} size={zf.getinfo(name).file_size}')
