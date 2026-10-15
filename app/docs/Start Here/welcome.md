---
title: Welcome
summary: What Next2Flash is, and which page to read first.
order: 1
---

# Welcome

## Info

| Welcome |
| --- |
| App | Next2Flash |
| Launch | `run.bat` |
| Project file | `.n2d` |
| Wiki | Help → Wiki |
| Related | Where things are |

Next2Flash is a SWF editor. The project you save is a `.n2d` file. JPEXS stays on the command line. Where things are lists the folders and the `n2f` commands. A first export is on [First export](first-export.md).

## Contents

1. [What you can do today](#what-you-can-do-today)
2. [References](#references)

## What you can do today

Double-click `run.bat`. The batch window closes, and the server has no command window. The home screen opens a `.n2d` project. `publish.bat` writes `Next2Flash Release\Next2Flash.exe`, and that app includes its own Python. From a terminal, `python app\n2f.py` runs the same export without the window. The command list is on Command line.

`n2f compile` writes a new SWF from that `.n2d` file. `n2f fla` turns a SWF into a CS6 FLA, and `n2f patch` edits a SWF through JPEXS. The editor does not open the FLA and does not run `n2f patch`. What the FLA command can store is on FLA and XFL. Limits of the SWF are on SWF export.

## References

1. [First export](first-export.md) — open a project, write a SWF, and publish the app.
2. Where things are — folders and which command touches which path.
3. Command line — every `n2f` command and how a feature gets a fixture.
4. FLA and XFL — `n2f fla` writes a FLA. The editor does not open it.
5. SWF export — what the compiler writes, and what it does not.
6. Roadmap — what is still unsupported.
