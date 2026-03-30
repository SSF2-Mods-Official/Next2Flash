# MessagePack Implementation - Final Fix

## Problem Solved
The Import SWF button was producing MessagePack N2D files from the server, but the tool's built-in loader (`Project.js`) was trying to decompress them as raw zlib data, causing "incorrect header check" error.

## Root Cause
Two separate code paths:
1. **Server** (`/api/swf-to-project`) → Outputs ZIP with MessagePack ✅
2. **Tool Loader** (`Project.js::load()`) → Expected raw zlib format ❌

## Solution Applied
Modified `src/javascript/view/tool/Project.js` to:

1. **Detect ZIP format** by checking for PK signature (0x50 0x4B)
2. **Extract MessagePack** from ZIP using JSZip
3. **Decode MessagePack** using window.MessagePack.decode()
4. **Convert to zlib** format that the tool expects
5. **Feed to existing pipeline** via unZlibWorker

### Code Flow
```
Server → ZIP(project.msgpack) 
  ↓
Project.js detects PK signature
  ↓
Extract with JSZip
  ↓
Decode with MessagePack
  ↓
Re-compress with pako.deflate
  ↓
Feed to unZlibWorker (existing pipeline)
  ↓
Tool loads successfully!
```

## Changes Made

### File: `app/src/javascript/view/tool/Project.js`
- Modified `load(file)` method
- Added ZIP detection (PK signature check)
- Added MessagePack extraction and decoding
- Added conversion to zlib format for compatibility
- Maintained backwards compatibility with old zlib files

## Testing Steps

1. **Restart server:**
   ```bash
   cd app
   python server.py
   ```

2. **Hard refresh browser** (Ctrl+F5)

3. **Click "Import SWF"** button

4. **Select goku.swf** (630MB test file)

5. **Verify console shows:**
   ```
   [N2F] Detected ZIP format, extracting MessagePack/JSON...
   [N2F] Loading MessagePack format (binary)
   [N2F] MessagePack decoded successfully
   [N2F] Converted to zlib format for tool
   [N2F] Decompressed size: 629.91 MB
   ```

## Expected Result
✅ File loads successfully without string length error  
✅ No "incorrect header check" error  
✅ Console shows MessagePack format detected  
✅ Tool opens with full timeline and libraries  

## Dependencies
- ✅ JSZip (already included in head.ejs)
- ✅ MessagePack (msgpack.min.js in assets/js/)
- ✅ pako (already included in tool)
- ✅ TextEncoder (native browser API)

## Files Modified
1. `app/server.py` - `/api/swf-to-project` endpoint now outputs MessagePack
2. `app/src/javascript/view/tool/Project.js` - Added ZIP+MessagePack handling
3. `app/assets/js/msgpack.min.js` - Downloaded library locally

## Build Status
✅ Build completed successfully (5.81s)  
✅ No syntax errors  
✅ All dependencies available  

---

**Status:** Ready for testing  
**Date:** March 29, 2026
