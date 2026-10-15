---
title: First export
summary: Open a project, write a SWF, and build the desktop app.
order: 2
---

# First export

## Info

| First export |
| --- |
| Launch | `run.bat` |
| Project | `.n2d` |
| Export | `n2f compile` |
| Release | `publish.bat` |
| Related | Command line |

This is the short path from a project file to a SWF, and from the repo to the desktop app.

## Contents

1. [Open a project](#open-a-project)
2. [Write a SWF](#write-a-swf)
3. [Build the app](#build-the-app)
4. [References](#references)

## Open a project

Double-click `run.bat` at the repo root. The batch window closes. The server has no command window. File → Open Project opens a `.n2d` file. The editor does not open a FLA.

## Write a SWF

From the repo root, with a project file named `game.n2d`:

```
python app\n2f.py compile game.n2d -o game.swf
```

That is the same writer the editor Export button uses. SWF export lists what the SWF contains. `n2f patch` edits a SWF through JPEXS and is not what Export runs.

## Build the app

```
publish.bat
```

The first run downloads a private Python into `dist\python` when that folder is missing. Later runs reuse it. The app is `Next2Flash Release\Next2Flash.exe`, a small launcher. Electron, locales, and Python are in the `runtime` folder beside it. Python does not need to be installed, and the pack keeps the `en-US` locale.

## References

1. Command line — every `n2f` command.
2. SWF export — what `compile` writes.
3. Where things are — folders and the toolchain.
