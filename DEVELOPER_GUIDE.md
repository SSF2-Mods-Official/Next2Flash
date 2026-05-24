# Next2Flash — Developer Guide

Welcome to Next2Flash. This guide covers the project architecture, development workflow, key source files, and common tasks for a new developer.

---

## Table of Contents

1. [What Is Next2Flash?](#what-is-next2flash)
2. [Repository Layout](#repository-layout)
3. [Architecture Overview](#architecture-overview)
4. [Development Prerequisites](#development-prerequisites)
5. [Running in Dev Mode](#running-in-dev-mode)
6. [Build Pipeline](#build-pipeline)
7. [Key Source Files](#key-source-files)
8. [SWF Roundtrip Pipeline](#swf-roundtrip-pipeline)
9. [Electron Integration](#electron-integration)
10. [Testing](#testing)
11. [Release Build](#release-build)

---

## What Is Next2Flash?

Next2Flash is a desktop SWF authoring tool built on:

- **Electron** — desktop shell, native menus, file dialogs.
- **Python (Flask)** — local HTTP server that provides the REST API and serves the web UI.
- **Next2D** — web-based animation editor running in the Electron renderer via an embedded browser.

The tool allows you to import an existing SWF file, edit it visually in the animation editor, and export a new SWF — a "roundtrip" workflow.

---

## Repository Layout

```
Next2Flash/
├── app/                        # Web application (editor UI + Python server)
│   ├── src/                    # SOURCE files — edit these, never the built outputs
│   │   ├── javascript/         # Editor JS source (compiled by gulp)
│   │   ├── html/               # EJS templates (compiled into app/index.html)
│   │   ├── stylesheet/         # SCSS/CSS source
│   │   └── languages/          # Localisation strings
│   ├── assets/                 # Build output: JS, CSS, images
│   │   └── js/
│   │       └── next2d-tool.min.js   # Compiled from src/javascript/
│   ├── index.html              # Built from src/html/*.ejs — do not edit directly
│   ├── server.py               # Flask HTTP server + SWF roundtrip logic
│   ├── swf_to_n2d.py           # SWF → N2D import pipeline
│   ├── compile_n2d.py          # N2D → SWF export pipeline
│   ├── gulpfile.js             # Gulp build: concat, minify JS/CSS, build HTML
│   ├── package.json
│   └── tests/                  # Python tests (pytest) + headless JS tests
├── electron/
│   ├── main.js                 # Electron main process
│   ├── preload.js              # Context bridge (window.n2fElectron)
│   ├── splash.html             # Splash screen shown while server starts
│   └── package.json
├── build-release.bat           # Full release build script
└── DEVELOPER_GUIDE.md          # This file
```

---

## Architecture Overview

```
┌─────────────────────────────────────┐
│           Electron Main             │
│  main.js — spawns server.py,        │
│  creates BrowserWindow, native menus│
└───────────────┬─────────────────────┘
                │ IPC (contextBridge)
┌───────────────▼─────────────────────┐
│        Renderer (Chromium)          │
│  index.html + next2d-tool.min.js    │
│  next2flash-integration.js          │
│  window.n2fElectron (bridge)        │
└───────────────┬─────────────────────┘
                │ HTTP (localhost:5000)
┌───────────────▼─────────────────────┐
│         Python Flask Server         │
│  server.py — REST API, file I/O     │
│  swf_to_n2d.py / compile_n2d.py     │
└─────────────────────────────────────┘
```

- The **renderer** is a standard web page; it can only reach native features through `window.n2fElectron` (the contextBridge defined in `electron/preload.js`).
- **IPC channels** connect the Electron menu (`main.js`) to the renderer (`preload.js` → `next2flash-integration.js`).
- The **Python server** runs on `http://127.0.0.1:5000` and is the only process that touches the filesystem directly for SWF data.

---

## Development Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Node.js | 18+ | Manages both `app/` and `electron/` packages |
| npm | 9+ | Comes with Node.js |
| Python | 3.9+ | Required for `server.py` |
| pip packages | — | `flask`, `pillow`, `msgpack` |
| PyInstaller | 6.x | Only for release builds |

```powershell
# Install JS deps
cd app && npm install
cd electron && npm install

# Install Python deps
pip install flask pillow msgpack
```

---

## Running in Dev Mode

Start the Python server and Electron separately in two terminals.

**Terminal 1 — Python server:**
```powershell
cd app
python server.py
# Serves UI at http://127.0.0.1:5000
```

**Terminal 2 — Electron:**
```powershell
cd electron
npx electron .
# Opens the desktop window loading http://127.0.0.1:5000
```

> **Tip:** When running in dev mode, `electron/main.js` detects that `server.py` is already running (it polls `/api/health`) and skips launching its own server process.

---

## Build Pipeline

### Editor JS (most frequent change)

After editing any file under `app/src/javascript/`:

```powershell
cd app
npm run build           # gulp concat + minify → assets/js/next2d-tool.min.js
```

The default build skips uglify for faster iteration. Use `npm run build -- --prodBuild` for a production-minified output.

### HTML

After editing any file under `app/src/html/`:

```powershell
cd app
npm run build           # also rebuilds index.html from EJS templates
```

The entry template is `app/src/html/head.ejs` for `<head>` content. Do not edit `app/index.html` directly.

### CSS

After editing `app/src/stylesheet/`:

```powershell
cd app
npm run build           # also rebuilds assets/css/main.min.css
```

---

## Key Source Files

### Editor JavaScript (`app/src/javascript/`)

| File | Purpose |
|------|---------|
| `Util.js` | Global utilities, shortcut system (`$setShortcut`, `$setGlobalShortcut`), `$currentWorkSpace()` |
| `WorkSpace.js` | Core editor state — `undo()`/`redo()`, `temporarilySaved()`, `_$revision[]` snapshot array |
| `GlobalKeyboardCommand.js` | Registers global keyboard shortcuts (Ctrl+Z, Ctrl+Shift+Z, Ctrl+S, …) |
| `TimelinePlayer.js` | Playback engine |
| `instance/` | Character rendering: `Instance.js`, `Bitmap.js`, `Shape.js`, `SkiaRenderer.js`, `PixiRenderer.js` |

### Shortcut System

Two registration functions exist in `Util.js`:

- `Util.$setShortcut(key, fn)` — **blocked** when `$keyLock = true` (e.g. during text/input editing).
- `Util.$setGlobalShortcut(key, fn)` — **always fires**, bypasses keyLock.

Undo/redo and Save use `$setGlobalShortcut` so they work even while a text field is focused.

### Undo/Redo System

- `WorkSpace._$revision[]` stores lazy snapshot thunks.
- `WorkSpace.temporarilySaved()` pushes a new snapshot (called in 20+ places after any edit).
- `WorkSpace.undo()` decrements `_$position` and calls `reloadData()`.
- `WorkSpace.redo()` increments `_$position` and calls `reloadData()`.

To call undo/redo from outside the editor (e.g. Electron menu or integration script):
```js
Util.$currentWorkSpace().undo();
Util.$currentWorkSpace().redo();
```

### Python Server (`app/server.py`)

The Flask server exposes:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Liveness probe |
| `/api/import-swf` | POST | SWF → N2D conversion |
| `/api/export-swf` | POST | N2D → SWF export |
| `/api/lazy/asset/<charId>` | GET | Lazy-load individual assets |

---

## SWF Roundtrip Pipeline

```
SWF file
  └── swf_to_n2d.py       → N2D JSON (project data in editor)
        └── Edit in UI
              └── compile_n2d.py  → new SWF file
```

Key design rules:
- **CharID preservation** — original `swfCharId` values are kept to avoid Flash Player Error #2015.
- **Bitmap passthrough** — unedited bitmaps use `rawBitmapTagBody` to avoid re-encode/format conversion bugs.
- **Raw tag passthrough** — DoABC, SymbolClass, and font tags are stored in `rawGlobalTags` and replayed verbatim.

---

## Electron Integration

### Context Bridge (`electron/preload.js`)

`window.n2fElectron` exposes:

| Method | Direction | Purpose |
|--------|-----------|---------|
| `openFileDialog(opts)` | renderer→main | Native open dialog |
| `saveFileDialog(opts)` | renderer→main | Native save dialog |
| `readFile(path)` | renderer→main | Read file from disk |
| `writeFile(path, data)` | renderer→main | Write file to disk |
| `onMenuSave(cb)` | main→renderer | File → Save Project menu |
| `onMenuUndo(cb)` | main→renderer | Edit → Undo menu |
| `onMenuRedo(cb)` | main→renderer | Edit → Redo menu |
| `onMenuExportSWF(cb)` | main→renderer | File → Export SWF menu |
| `onImportSWF(cb)` | main→renderer | File → Import SWF menu |

### Adding a New Menu Action

1. Add the menu item in `electron/main.js` with a `click` handler that calls `mainWindow?.webContents.send('menu:your-action')`.
2. Expose a listener in `electron/preload.js`: `onYourAction: (cb) => ipcRenderer.on('menu:your-action', () => cb())`.
3. Wire the callback in `app/assets/js/next2flash-integration.js` inside the `if (window.n2fElectron)` block.

---

## Testing

### Python unit tests

```powershell
cd app
python -m pytest tests/ -v
```

### Headless browser test (Puppeteer)

```powershell
cd app
node tests/headless_import.js
# Starts server on port 5111, imports fox.ssf, checks for errors
```

---

## Release Build

Run the automated build script from the repo root:

```powershell
.\build-release.bat
```

This script:
1. Compiles the editor JS/CSS/HTML with gulp (`npm run build`).
2. Builds the Python server into a standalone EXE with PyInstaller.
3. Runs a smoke test (polls `/api/health` on a temp port for up to 90 s).
4. Packages the Electron app with electron-builder (`dir` target).
5. Zips the output to `build/Next2Flash-win-x64.zip`.

The packaged app lives in `build/win-unpacked/`. The portable ZIP is `build/Next2Flash-win-x64.zip`.

> **Note:** electron-builder uses the `dir` target (not `portable`) to avoid a Windows symlink bug in the winCodeSign module. The final ZIP is produced by PowerShell's `Compress-Archive`.
