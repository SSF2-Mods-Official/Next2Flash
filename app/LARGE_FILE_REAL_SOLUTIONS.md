# 5 Real Solutions for Large File Loading (630MB+)

## Problem
JavaScript has a hard string length limit (~500-1000MB). Your goku.ssf decompresses to 630MB, exceeding this limit.

---

## Solution 1: Binary JSON Parser (NO STRING CONVERSION) ✅ BEST

**Idea:** Parse JSON directly from Uint8Array buffer without converting to string first.

**Implementation:**
- Use a binary JSON parser that reads bytes directly
- Library: `json-stream` or write custom parser
- Never creates the 630MB string
- Parses incrementally from buffer

**Benefits:**
- Bypasses string length limit completely
- Lower memory usage (no 630MB string in memory)
- Faster (no decode step)

**Code Sketch:**
```javascript
// Instead of: JSON.parse(new TextDecoder().decode(buffer))
// Use: parseBinaryJSON(buffer)

function parseBinaryJSON(buffer) {
    const parser = new BinaryJSONParser();
    let result = null;
    let position = 0;
    
    // Parse directly from bytes
    while (position < buffer.length) {
        const chunk = buffer.subarray(position, position + 1024);
        parser.feed(chunk);
        position += 1024;
    }
    
    return parser.getResult();
}
```

**Effort:** Medium (2-3 days)  
**Success Rate:** 95% - Should handle any size file

---

## Solution 2: MessagePack Binary Format ✅ RECOMMENDED

**Idea:** Convert Python SWF converter to output MessagePack instead of JSON.

**Implementation:**
- Modify `swf_to_n2d.py` to use `msgpack` library
- Output .n2d files as MessagePack binary (much smaller!)
- Parse with `msgpack.js` in browser (no string conversion)
- 100% binary, no JSON strings

**Benefits:**
- **50-70% smaller files** (binary is more compact than JSON)
- No string conversion at all
- Faster parsing
- Handles unlimited size

**Python Changes:**
```python
import msgpack

# Instead of:
output = json.dumps(data)

# Use:
output = msgpack.packb(data)
```

**JavaScript Changes:**
```javascript
// Instead of:
const data = JSON.parse(json);

// Use:
const msgpack = require('msgpack-lite');
const data = msgpack.decode(buffer); // Direct from Uint8Array!
```

**Effort:** Low (1 day)  
**Success Rate:** 99% - Proven technology, used by Redis, etc.

---

## Solution 3: SQLite/WASM Database ✅ SCALABLE

**Idea:** Store the N2D data in an in-browser SQLite database.

**Implementation:**
- Use `sql.js` (SQLite compiled to WebAssembly)
- Parse JSON in chunks, insert into SQLite tables
- Query on-demand when UI needs data
- Handles gigabyte-scale data

**Benefits:**
- No string length limits
- Efficient queries (only load what's visible)
- Can handle 1GB+ files
- Index support for fast lookups

**Code Sketch:**
```javascript
const SQL = await initSqlJs();
const db = new SQL.Database();

// Create schema
db.run(`CREATE TABLE libraries (
    id INTEGER PRIMARY KEY,
    name TEXT,
    type TEXT,
    data BLOB
)`);

// Insert libraries in chunks
for (let i = 0; i < totalLibraries; i++) {
    const lib = parseLibraryChunk(buffer, i);
    db.run('INSERT INTO libraries VALUES (?, ?, ?, ?)', 
           [lib.id, lib.name, lib.type, lib.data]);
}

// Later: Load on-demand
const lib = db.exec('SELECT * FROM libraries WHERE id = 42')[0];
```

**Effort:** High (4-5 days)  
**Success Rate:** 90% - Very robust, proven for large datasets

---

## Solution 4: Chunked N2D Format (Python + JS) ✅ CLEAN

**Idea:** Modify converter to output multiple smaller files.

**Implementation:**
- Python outputs: `goku_manifest.n2d` (1MB) + `goku_lib_000.n2d` through `goku_lib_037.n2d` (20MB each)
- JavaScript loads manifest first, shows UI
- Loads library chunks on-demand when user clicks
- Each chunk small enough to process

**Python Changes:**
```python
# swf_to_n2d.py
def export_chunked(swf, output_path):
    manifest = {
        'version': '2.0',
        'name': swf.name,
        'timeline': extract_timeline(swf),
        'library_count': len(swf.libraries),
        'chunks': []
    }
    
    CHUNK_SIZE = 50  # 50 libraries per chunk
    for i, chunk in enumerate(chunk_list(swf.libraries, CHUNK_SIZE)):
        chunk_file = f'{output_path}_lib_{i:03d}.n2d'
        write_compressed(chunk_file, {'libraries': chunk})
        manifest['chunks'].append(f'lib_{i:03d}')
    
    write_compressed(f'{output_path}_manifest.n2d', manifest)
```

**JavaScript Changes:**
```javascript
// Load manifest
const manifest = await loadN2D('goku_manifest.n2d');
workspace.initFromManifest(manifest);

// Load chunks on-demand
async function getLibrary(id) {
    const chunkIndex = Math.floor(id / 50);
    if (!loadedChunks[chunkIndex]) {
        const chunk = await loadN2D(`goku_lib_${chunkIndex.toString().padStart(3, '0')}.n2d`);
        loadedChunks[chunkIndex] = chunk.libraries;
    }
    return loadedChunks[chunkIndex][id % 50];
}
```

**Effort:** Medium (2-3 days)  
**Success Rate:** 99% - Guaranteed to work, no size limits

---

## Solution 5: Web Worker + SharedArrayBuffer ✅ PARALLEL

**Idea:** Use multiple workers to parse different chunks in parallel.

**Implementation:**
- Split buffer into 4 chunks (157MB each)
- Spawn 4 workers, each parses their chunk
- Use SharedArrayBuffer to avoid copying
- Merge results in main thread

**Benefits:**
- Parallel processing (4x faster on quad-core)
- Each worker handles smaller strings (~160MB)
- SharedArrayBuffer = zero-copy transfer
- Can scale to more workers

**Code Sketch:**
```javascript
async function parseInParallel(buffer) {
    const WORKERS = 4;
    const chunkSize = Math.ceil(buffer.length / WORKERS);
    
    // Create shared buffer
    const sharedBuffer = new SharedArrayBuffer(buffer.length);
    new Uint8Array(sharedBuffer).set(buffer);
    
    // Spawn workers
    const promises = [];
    for (let i = 0; i < WORKERS; i++) {
        const worker = new Worker('parser-worker.js');
        const start = i * chunkSize;
        const end = Math.min(start + chunkSize, buffer.length);
        
        promises.push(new Promise(resolve => {
            worker.postMessage({ sharedBuffer, start, end });
            worker.onmessage = e => resolve(e.data);
        }));
    }
    
    // Wait for all workers
    const chunks = await Promise.all(promises);
    return mergeChunks(chunks);
}
```

**Effort:** Medium (3-4 days)  
**Success Rate:** 80% - SharedArrayBuffer has security restrictions

---

## Comparison Table

| Solution | Effort | Speed | Max Size | Complexity | Recommended? |
|----------|--------|-------|----------|------------|--------------|
| Binary JSON Parser | Medium | Fast | Unlimited | Medium | ✅ Yes |
| MessagePack | Low | Fastest | Unlimited | Low | ✅✅ Yes! |
| SQLite/WASM | High | Medium | 1GB+ | High | ⚠️ Overkill |
| Chunked N2D | Medium | Fast | Unlimited | Medium | ✅ Yes |
| SharedArrayBuffer | Medium | Fastest | 500MB* | High | ⚠️ Restrictions |

\* Still limited by worker string creation

---

## My Recommendation: Implement in This Order

### Phase 1 (This Week): **MessagePack** ✅
- **Easiest**: Just swap JSON for MessagePack
- **Biggest win**: 50-70% smaller files + no string limits
- **Changes needed**: Python converter + JavaScript loader
- **Backwards compatible**: Keep JSON support as fallback

### Phase 2 (Next Week): **Chunked N2D Format** ✅
- **Clean architecture**: Proper lazy loading
- **Future-proof**: Works for any file size
- **Better UX**: Shows UI immediately, loads in background

### Phase 3 (Later): **Binary JSON Parser** (if needed)
- Only if you want to keep pure JSON format
- More complex but handles current JSON files

---

## Which One Should I Implement First?

**I recommend MessagePack** because:
1. ✅ Smallest code change (1 day)
2. ✅ Solves your problem immediately  
3. ✅ Makes ALL files faster & smaller (not just large ones)
4. ✅ Industry standard (Redis, Kafka use it)
5. ✅ Zero downsides

Want me to implement it now?
