RT:OG 1:1 Decomp/Recomp Gameplan (Black Mage)
Generated: 2026-04-18

Goal
- Achieve script-level parity between OG and RT while keeping the established pipeline flow:
  decompile -> normalize -> external scripts/stubs -> mxmlc recompile -> SWF -> decompile compare.
- No raw DoABC passthrough.

Current Measured Status (fresh SWF-level compare)
- OG scripts: 779
- RT scripts: 780
- Only in OG: 0
- Only in RT: 1 (ColorMatrix.as)
- Identical shared scripts: 53
- Whitespace-only: 0
- Real non-whitespace differences: 726
- ItemSettings.as present in RT: YES

Executed Fixes (completed)
1) Removed SSF2 API SWC dependency from compile path.
- compile_n2d.py: removed SWC library-path and SWC-based filtering.
- compilation_pipeline.py: removed SWC path wiring.

2) Enforced single-definition behavior for generated stubs.
- compile_n2d.py: prune embedded classes that collide with generated stubs.

3) Fixed missing ItemSettings.as in RT output.
- compile_n2d.py: include top-level embedded classes in mxmlc include config.
- Result: ItemSettings.as now appears in freshly decompiled RT.

4) Reduced frame-stub decompile drift.
- compile_n2d.py: changed generated frame method names from frame_N to frameN.
- compile_n2d.py: changed frame addFrameScript emission to one multi-arg call style.
- Result: identical scripts improved from 26 to 53, real diffs reduced from 753 to 726.

5) Made broad framework forcing opt-in.
- compile_n2d.py: include all framework classes only when N2F_INCLUDE_ALL_FRAMEWORK_CLASSES=1.
- Default now relies on transitive references.

Remaining Gap (root causes)
- Bytecode drift from recompilation/stub synthesis still causes large source-level changes when decompiled.
- Stub-generated classes still differ from OG decompiler output in variable declaration/initialization structure and function body form.
- At least one extra class remains in RT output (ColorMatrix.as), likely due transitive references in current source graph.

Next Execution Phases
Phase A - Missing/extra class parity
- Add symbol-level include filtering based on OG SymbolClass order/class set.
- Emit only classes present in OG class set for this character package unless explicitly required by runtime.
- Verify: Only-OG=0 and Only-RT=0.

Phase B - Stub emission parity pack
- Update stub generator to match OG decompile patterns:
  - import set minimization for generated stubs.
  - var declaration placement rules.
  - constructor/body ordering rules.
- Verify: identical count rises significantly in symbol-stub-heavy classes.

Phase C - Frame action canonicalization
- Normalize frame action extraction/emission pipeline to preserve ordering and merged script boundaries exactly.
- Verify with targeted files: black_mage.as, Main.as, BlackMageExt.as, SSF2CharacterExt.as.

Phase D - Automated parity gate
- Add a script to compare OG/RT SWF-decompiled scripts and fail build when:
  - missing/extra classes exist
  - real diff count exceeds threshold.

Operational Note
- Re-run command for parity measurement after each phase:
  python _recompile_blackmage.py
  then SWF-level script compare via swf_to_n2d.decompile_all_scripts.
