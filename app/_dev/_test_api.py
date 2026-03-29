"""Test the full SSF → N2D conversion via the server API and validate the output format."""
import urllib.request
import zlib

ssf_path = r'C:\Users\glwex\Documents\GitHub\ssf2-idk-140x-original\src\Super Smash Flash 2 Beta v1.4.0.1\data\character\gameandwatch.ssf'
data = open(ssf_path, 'rb').read()
print(f"Input: {len(data)} bytes")

req = urllib.request.Request('http://localhost:5000/api/swf-to-n2d', data=data, method='POST')
req.add_header('Content-Type', 'application/octet-stream')

print("Sending to server...")
resp = urllib.request.urlopen(req, timeout=120)
n2d = resp.read()
print(f"N2D response: {len(n2d)} bytes")
print(f"Headers: Name={resp.headers.get('X-N2D-Name')}, Libs={resp.headers.get('X-N2D-Libraries')}, Scripts={resp.headers.get('X-N2D-Scripts')}")

# Verify it's valid zlib
print("Decompressing...")
inflated = zlib.decompress(n2d)
print(f"Inflated: {len(inflated)} bytes")

# Verify it's URL-encoded JSON
text = inflated.decode('ascii')
print(f"First 80 chars: {text[:80]}")

# Verify decodeURIComponent equivalent works
from urllib.parse import unquote
json_str = unquote(text)
print(f"Decoded JSON: {len(json_str)} chars")
print(f"Starts with: {json_str[:60]}")

# Verify valid JSON
import json
obj = json.loads(json_str)
print(f"Valid JSON with {len(obj.get('libraries',[]))} libraries, {len(obj.get('scripts',[]))} scripts")
print("SUCCESS: Format is valid zlib(URL-encoded JSON)")
