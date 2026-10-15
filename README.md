# Next2Flash

A Windows desktop editor and command-line toolchain for Flash/AIR (ActionScript 3) projects. Import a SWF, edit it on a timeline and stage, and export a working SWF again. Built on the open-source [Next2D](https://next2d.app/) editor.

<img width="1024" alt="Next2Flash start screen" src="https://github.com/user-attachments/assets/7cb58e20-1c8b-4bd7-a6d8-865fc909b503" />

> **Alpha software.** Expect bugs, keep backups of your files, and do not rely on a single `.n2d` as your only copy.

## What it does

- SWF to editable project (`.n2d` or a folder of PNG/WAV/AS files) and back to SWF
- Visual editor: timeline, layers, library, transform and color tools, filters
- AS3 decompile, and recompile with a bundled Flex/AIR lite SDK (`mxmlc`, `compc`, `asconfigc`)
- SWF to CS6 FLA export, and in-place SWF patching through JPEXS FFDec
- `n2f` command line for every operation, for scripts and other programs

## Install

Download the latest ZIP from [Releases](../../releases), unzip it, and run `Next2Flash.exe`. The release includes its own Python, JRE, FFDec, and Flex lite SDK.

### From source

Requirements: Windows, Node.js 18+, Python 3.9+.

```powershell
cd app; npm install
cd electron; npm install
cd ..\..
pip install -r app\requirements.txt
```

The Flash toolchain binaries are not in git. Put FFDec in `toolchain\ffdec`, a Java 17 runtime in `toolchain\jre`, and the Flex/AIR lite SDK in `toolchain\aflex_lite` (or set `N2F_TOOLCHAIN` to a folder with that layout). `python app\n2f.py toolchain` prints what was found.

## Quick start

Desktop app: run `run.bat`. Help → Wiki documents folders, commands, and export.

Command line:

```powershell
python app\n2f.py convert game.swf -o game.n2d        # SWF -> N2D
python app\n2f.py compile game.n2d -o game.swf        # N2D -> SWF
python app\n2f.py decompile game.swf --all -d out     # AS3 sources
python app\n2f.py asconfig --project asconfig.json    # compile an AS3 project
python app\n2f.py fla game.swf -o game.fla            # SWF -> CS6 FLA
python app\n2f.py --help
```

Build a release folder with `publish.bat`. Run tests with `cd app; python -m pytest tests`.

## License

MIT, see [LICENSE](LICENSE). The editor is based on the Next2D NoCode Tool ([app/LICENSE](app/LICENSE)). The FFDec worker in `toolchain/ffdec-worker` is GPLv3, like FFDec.
