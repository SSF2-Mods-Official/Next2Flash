# Reconvert Existing N2D Files to MessagePack Format

## Problem
If you have an existing `.n2d` file that was created **before** the MessagePack implementation, it will still contain the old JSON format and will fail to load if it exceeds ~500-630MB.

## Solution
You need to reconvert from the original SWF source file to create a MessagePack-based N2D.

---

## Quick Start

### Option 1: Use the Batch Script (Easiest)

```bash
cd app
reconvert_to_msgpack.bat path\to\your\file.swf output_name.n2d
```

**Example:**
```bash
reconvert_to_msgpack.bat C:\Games\goku.swf goku_msgpack.n2d
```

### Option 2: Direct Python Command

```bash
cd app
python swf_to_n2d.py input.swf output.n2d
```

### Option 3: Use Import SWF Button (UI Method)

1. **Start the server:**
   ```bash
   cd app
   python server.py
   ```

2. **Hard refresh browser** (Ctrl+F5)

3. Click "Import SWF" button and select your original SWF file

4. The server will automatically create a MessagePack N2D

---

## How to Verify It Worked

After loading your new N2D file, check the browser console. You should see:

✅ **Success (MessagePack format):**
```
[N2F] Loading MessagePack format (binary)
[N2F] MessagePack decoded successfully
```

❌ **Old format (will fail for large files):**
```
[N2F] Using chunked TextDecoder for large buffer...
[N2F] Decoded 63/63 chunks (100%)
[N2F] Failed to join chunks into string: RangeError: Invalid string length
```

---

## File Size Comparison

The MessagePack format is also **27-70% smaller**:

- **Old JSON format:** 630MB (fails to load)
- **New MessagePack format:** ~189-459MB (loads successfully)

---

## Important Notes

1. **You cannot convert N2D → N2D directly**  
   You must start from the original `.swf` or `.ssf` source file.

2. **The old N2D file is not broken**  
   It just uses the old JSON format that can't handle 630MB+ files.

3. **Keep your original SWF files**  
   Always keep the source SWF files so you can reconvert if needed.

4. **Existing small N2D files still work**  
   Files under ~400MB will continue to work with the old JSON format. The MessagePack implementation maintains full backwards compatibility.

---

## Where is My Original SWF File?

If you don't have the original SWF file anymore, check these locations:

1. The folder where you first imported it from
2. `app/converted/` folder (may contain backups)
3. Your SSF2 game directory
4. Downloads folder

If you truly lost the SWF source, the old N2D file is unfortunately unrecoverable for files this large (it's the fundamental JavaScript string length limit).
