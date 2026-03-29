"""Quick benchmark of URL-encoding approaches for large JSON strings."""
import time

# Build str.translate table matching JavaScript's encodeURIComponent
# Safe chars: A-Za-z0-9 - _ . ! ~ * ' ( )
_URI_TABLE = {}
for _i in range(128):
    _c = chr(_i)
    if not (_c.isalnum() or _c in "-_.!~*'()"):
        _URI_TABLE[_i] = "%{:02X}".format(_i)

# Test string: typical JSON with lots of special chars
test_json = '{"id":123,"name":"test","data":[1,2,3],"nested":{"a":"b"}}' * 70000
print(f"Input: {len(test_json)} chars")

# Method 1: str.translate (C-level)
t0 = time.time()
result1 = test_json.translate(_URI_TABLE)
t1 = time.time()
print(f"str.translate: {t1-t0:.3f}s, output: {len(result1)} chars")

# Method 2: urllib.parse.quote
from urllib.parse import quote
t0 = time.time()
result2 = quote(test_json, safe='')
t1 = time.time()
print(f"urllib.quote:  {t1-t0:.3f}s, output: {len(result2)} chars")

# Verify they produce the same result
# Note: quote() uses lowercase hex, translate uses uppercase
# encodeURIComponent uses uppercase, so translate is correct
print(f"Match (case-insensitive): {result1.lower() == result2.lower()}")
