import zipfile, re
z = zipfile.ZipFile(r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\lib\SSF2.swc")
cat = z.read("catalog.xml").decode("utf-8")
defs = re.findall(r'<def id="([^"]+)"', cat)
utils_defs = [d for d in defs if "util" in d.lower() or "Utils" in d]
print("Total defs:", len(defs))
print("Utils defs:", utils_defs[:5])
print("Sample defs:", defs[:10])
