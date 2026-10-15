# FFDec warm worker (GPLv3)

Small long-lived Java process that calls JPEXS FFDec's
`CommandLineArgumentParser.parseArguments` in a loop so callers can
reuse one JVM across many CLI operations.

- **License:** GNU GPL v3 (same as FFDec). Source is in `src/`.
- **Depends on:** bundled `../ffdec/ffdec.jar` + `../ffdec/lib/*`.
- **Build:** `.\build.ps1` (requires `javac` on PATH, or bundled JDK).
- **Main class:** `next2flash.ffdec.FfdecWorker`.

Protocol: see `FfdecWorker.java` header comment. A command line may carry
`-Dn2f.<name>=<value>` tokens; they are set as system properties before the
FFDec command runs.

Custom commands (handled in-process, not by stock FFDec CLI):

- `-identdump in.swf out.xml` — ABC string pool + SymbolClass names as a tiny plan XML
- `-identrewrite in.swf out.swf pairs.txt` — apply identifier/exact rewrites in memory and save
- `-untypestance in.swf out.swf` — retype stage instance slots typed as `*_fla.*` timeline classes to `flash.display.MovieClip`
- `-placeedit in.swf edits.txt` — add, move, or remove keyframe placements
