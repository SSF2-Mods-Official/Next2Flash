<div align="center">

# Next2Flash

**A modern desktop editor for round‑tripping SWF files.**

Import a SWF, edit it visually, export it back to a working SWF — no Adobe Animate required.

[![Platform](https://img.shields.io/badge/platform-Windows-blue)](#)
[![Electron](https://img.shields.io/badge/Electron-desktop-2b2e3a?logo=electron)](#)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](#)
[![License](https://img.shields.io/badge/license-See%20LICENSE-lightgrey)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-join%20chat-5865F2?logo=discord&logoColor=white)](https://discord.gg/MaJFnhHpYx)

### 💬 Questions, bug reports, or just want to chat? [**Join the Discord →**](https://discord.gg/MaJFnhHpYx)

[Quick Start](#-quick-start) · [Features](#-features) · [Usage](#-usage) · [Building from Source](#-building-from-source) · [Project Layout](#-project-layout) · [Troubleshooting](#-troubleshooting)

</div>

---

> ## ⚠️ Heads up — this is alpha software
>
> **Next2Flash is still very much a work in progress and is *not* production‑ready.**
>
> Expect:
> - 🐛 **Bugs in nearly every workflow** — imports may drop characters, exports may produce SWFs that play differently than the original, undo/redo can desync, the editor can lag or freeze on large projects.
> - 🧪 **Half‑finished features** — many controllers, tools, and menu items are wired up but not fully implemented or only work in narrow cases.
> - 💾 **No guarantees about your project files** — save often, keep backups, and don't trust a single `.n2d` as your only copy. Autosave‑on‑close is currently *disabled*.
> - 🔁 **Round‑trip is not byte‑perfect** — even untouched SWFs can come out structurally different. AS3 may fall back to the original bytecode if recompile fails.
> - 🏗️ **Architecture is still moving** — APIs, project format, IPC channels, and folder layout can change between commits without notice.
>
> Getting all of the advertised "features" working flawlessly is going to take a **lot** more iteration. If you're here, you're an early tester — please open issues with reproducible cases, and don't be surprised when things break.
>
> **TL;DR:** cool toy, do not ship anything important with it yet.

---

## ✨ What is it?

**Next2Flash** is a desktop SWF authoring tool built on top of the [Next2D](https://next2d.app/) NoCode editor. It gives you a visual timeline + stage workflow for editing existing SWF files (shapes, bitmaps, movie clips, fonts, ActionScript 3) and writes a new, runnable SWF on export.

It bundles three pieces into a single app:

| Layer | Tech | Role |
|---|---|---|
| Shell | **Electron** | Desktop window, native menus, file dialogs |
| Editor | **Next2D** (JS/HTML/CSS) | Timeline, stage, library, controllers |
| Backend | **Python + Flask** | SWF parsing, N2D ↔ SWF conversion, AS3 recompilation |

---

## 🚀 Quick Start

> Want to just *use* the app? Grab the latest portable ZIP from the [Releases](../../releases) page, unzip, and run `Next2Flash.exe`. No install needed.

If you want to run it from the repo without a full release build, you have three options:

### Option 1 — Desktop (Electron, recommended)
```powershell
.\Next2Flash-Desktop.bat
```
Launches Python server + Electron window together.

### Option 2 — Electron only (server already running)
```powershell
.\Next2Flash-Electron.bat
```

### Option 3 — Browser mode (no Electron)
```powershell
.\Next2Flash-Browser.bat
```
Opens the editor at `http://127.0.0.1:5000` in your default browser.

---

## 🎯 Features

- 🔁 **Full SWF round‑trip** — import a SWF, edit, export a new SWF that runs in Flash Player / Ruffle
- 🎨 **Visual editor** — timeline, layers, library, transform tools, color tools, filters
- 🖼️ **Bitmap pass‑through** — unedited bitmaps are written back byte‑identical (no re‑encode artifacts)
- 🆔 **Character ID preservation** — keeps original `swfCharId` values so existing AS3 references keep working
- 📜 **AS3 recompilation** — bundled Flex SDK + jlink JRE recompiles edited ActionScript 3
- 🌐 **Multi‑language UI** — 20+ localizations (English, Japanese, Korean, Chinese, Russian, …)
- 💾 **Native file dialogs** — proper open/save dialogs via Electron's `dialog` API
- 🖥️ **Standalone desktop app** — no Python install required for end users (PyInstaller‑built `server.exe`)

---

## 📖 Usage

### Importing a SWF
1. **File → Import SWF…** (or `Ctrl+I`)
2. Pick your `.swf`
3. Wait for the import to finish — characters appear in the library, root timeline on the stage

### Editing
- **Move/transform** — click a character on stage, drag handles
- **Timeline** — add/remove frames, drag keyframes between layers
- **Library** — double‑click a movie clip to enter its timeline
- **Save project** — `Ctrl+S` writes an `.n2f` project bundle (compressed JSON + assets)

### Exporting back to SWF
1. **File → Export SWF…**
2. Pick a destination
3. Next2Flash regenerates the SWF, recompiles AS3 if needed, and writes the new file

> 💡 **Tip:** if AS3 recompilation fails, the original DoABC bytecode is replayed verbatim, so the export still produces a runnable SWF.

---

## 🛠️ Building from Source

### Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Node.js | 18+ | JS build (gulp), Electron |
| Python | 3.9+ | Flask server, SWF pipeline |
| JDK 17+ (with `jlink` on PATH) | — | Only needed for release builds (bundles a JRE for AS3 recompile) |

### Install dependencies
```powershell
# JS deps
cd app;        npm install
cd ..\electron; npm install

# Python deps
pip install -r app\requirements.txt
```

### Dev workflow

Edit JS source under [app/src/javascript/](app/src/javascript), then rebuild the bundle:

```powershell
cd app
npm run build      # gulp: concat + minify → app/assets/js/next2d-tool.min.js
```

> ⚠️ **Always edit source files** (`app/src/...`). Never edit the built `app/assets/js/next2d-tool.min.js` or `app/index.html` directly — they're regenerated by gulp.

Then launch the app via any of the [Quick Start](#-quick-start) batch files.

### Release build (one‑shot)

```powershell
.\build-release.bat
```

What it does:
1. `pip install` Python deps
2. `gulp build` editor JS/CSS/HTML (production minified)
3. `PyInstaller` bundles `server.py` → `server.exe`
4. Smoke‑test the EXE (boots it, polls `/api/health` for up to 90 s)
5. `electron-builder` packages the Electron app
6. `jlink` builds a minimal JRE into `flex_sdk/jre/` (~70 MB)
7. Zips everything to `build/Next2Flash-win-x64.zip`

The unpacked app lives in `build/win-unpacked/`.

---

## 📁 Project Layout

```
Next2Flash/
├── app/                       Web editor + Python backend
│   ├── src/                   ← SOURCE (edit these)
│   │   ├── javascript/        Editor JS (compiled by gulp)
│   │   ├── html/              EJS templates → index.html
│   │   ├── stylesheet/        CSS source
│   │   └── languages/         Localization strings
│   ├── assets/                ← BUILD OUTPUT (do not edit)
│   ├── server.py              Flask HTTP server
│   ├── swf_to_n2d.py          SWF → N2D import
│   ├── compile_n2d.py         N2D → SWF export
│   ├── as3_decompiler/        AS3 bytecode → source
│   └── flex_sdk/              Flex SDK + bundled JRE (not committed)
├── electron/
│   ├── main.js                Electron main process
│   ├── preload.js             Renderer ↔ main bridge
│   └── splash.html
├── build-release.bat          Full release build
├── Next2Flash-Desktop.bat     Run dev build (Electron + server)
├── Next2Flash-Browser.bat     Run in browser
└── DEVELOPER_GUIDE.md         Deep‑dive architecture notes
```

For architecture, IPC channels, the undo/redo system, and the full SWF pipeline, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md).

---

## 🧪 Testing

```powershell
# Python unit tests
cd app
python -m pytest tests/ -v

# Headless browser smoke test
node tests/headless_import.js
```

---

## 🩺 Troubleshooting

<details>
<summary><strong>"Port 5000 already in use" on startup</strong></summary>

Another Next2Flash instance (or any other process) is holding the port.

```powershell
# Find and kill it
netstat -ano | findstr ":5000"
Stop-Process -Id <PID> -Force
```
</details>

<details>
<summary><strong>AS3 recompilation fails / "jlink not found"</strong></summary>

Install JDK 17+ and ensure `jlink` is on your PATH. Without it, the release build still works but the bundled JRE is skipped — end users will need their own Java install for AS3 recompile.

The exported SWF still works either way; if recompile fails, the original AS3 bytecode is replayed verbatim.
</details>

<details>
<summary><strong>Build script fails with <code>". was unexpected at this time."</code></strong></summary>

You're running an old `build-release.bat`. Pull the latest — the step 6 (jlink JRE) cmd parser bug was fixed in commit `8255230b`.
</details>

<details>
<summary><strong>"Cannot create symbolic link" during electron-builder</strong></summary>

This is a known winCodeSign quirk on Windows without admin privileges. The release script intentionally uses the `dir` target + PowerShell `Compress-Archive` to sidestep it — make sure you're running `build-release.bat`, not raw `electron-builder --win portable`.
</details>

<details>
<summary><strong>Clicking on a MovieClip does nothing in the editor</strong></summary>

Make sure you're on `main` at or after commit `8255230b` — an experimental delegated‑listener perf change in an earlier revision broke MovieClip click handling and has since been reverted.
</details>

---

## 📜 License

See [LICENSE](LICENSE). Built on top of the open‑source [Next2D NoCode Tool](https://next2d.app/) — see [app/LICENSE](app/LICENSE) for upstream attribution.

---

<div align="center">

**Next2Flash** · Built with ⚡ Electron, 🐍 Python, and 🎬 Next2D.

</div>
