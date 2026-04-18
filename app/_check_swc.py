import zipfile, re
z = zipfile.ZipFile(r"C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\SSF2 API.swc")
cat = z.read("catalog.xml").decode("utf-8")
defs = re.findall(r'<def id="([^"]+)"', cat)
utils_defs = [d for d in defs if "Utils" in d or "util" in d.lower()]
print("Utils in SWC:", utils_defs[:10])
print("Total defs in SWC:", len(defs))
