"""
Compilation Pipeline - Refactored N2D → SWF compilation stages.

This module breaks the monolithic N2DCompiler.compile() method into
discrete, testable pipeline stages following the Single Responsibility
Principle.

Pipeline stages (in order):
  1. LoadN2DStage        - Load and parse N2D file
  2. AllocateCharIDsStage - Assign SWF character IDs in dependency order
  3. ParseRawTagsStage   - Parse rawGlobalTags and fontAuxTags
  4. DefineAssetsStage   - Generate definition tags for all assets
  5. BuildTimelineStage  - Build root timeline with PlaceObject/RemoveObject
  6. CompileAS3Stage     - Compile ActionScript 3.0 bytecode
  7. AssembleSWFStage    - Assemble final SWF file
  8. WriteOutputStage    - Write SWF to disk

Each stage receives a CompilationContext (dataclass) and either modifies
it in place or returns modified context.  The CompilationPipeline
coordinates stage execution, error handling, and rollback.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from profiler import Profiler

log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════
#                           CONTEXT DATACLASS
# ══════════════════════════════════════════════════════════════════════

@dataclass
class CompilationContext:
    """
    Shared state container passed through all pipeline stages.

    This dataclass holds all intermediate compilation data:
      - Input parameters (n2d_path, shared_dir, output_path, sdk_path)
      - Loaded N2D data (data, stage, libs, id_to_lib)
      - ID mappings (lib_to_swf_id, lib_to_char_idx, char_idx_to_swf_id)
      - Generated tags (definition_tags, root_timeline_tags, doabc_tags)
      - AS3 compilation artifacts (sym_to_class, fla_classes)
      - Final output (swf_bytes)
    """
    # ── Input parameters ──
    n2d_path: str
    shared_dir: str
    output_path: str
    sdk_path: Optional[str] = None

    # ── Loaded N2D data ──
    data: dict = field(default_factory=dict)
    stage: dict = field(default_factory=dict)
    libs: List[dict] = field(default_factory=list)
    id_to_lib: Dict[int, dict] = field(default_factory=dict)
    project_dir: Optional[str] = None  # set if loading from project folder

    # ── SWF character ID allocation ──
    next_id: int = 1
    lib_to_swf_id: Dict[int, int] = field(default_factory=dict)  # n2d lib id → SWF char ID
    lib_to_char_idx: Dict[int, int] = field(default_factory=dict)  # n2d lib id → char array index
    char_idx_to_swf_id: Dict[int, int] = field(default_factory=dict)  # char array index → SWF char ID
    emission_order: List[int] = field(default_factory=list)  # lib IDs in emission order
    deferred_lib_ids: List[int] = field(default_factory=list)  # root timeline defs
    deferred_swf_ids: Set[int] = field(default_factory=set)
    bitmap_char_ids: Set[int] = field(default_factory=set)  # bitmap SWF IDs for PO3
    orig_to_new_id: Dict[int, int] = field(default_factory=dict)  # swfCharId → new SWF ID

    # ── Parsed raw tags ──
    raw_doabc_tags: bytearray = field(default_factory=bytearray)
    raw_aux_tags: bytearray = field(default_factory=bytearray)
    raw_aux_map: Dict[int, bytes] = field(default_factory=dict)
    font_aux_tags: Dict[int, List[Tuple[int, bytes]]] = field(default_factory=dict)

    # ── Generated tags ──
    definition_tags: bytearray = field(default_factory=bytearray)
    root_timeline_tags: bytes = b""

    # ── AS3 compilation ──
    doabc_tags: bytes = b""
    sym_to_class: Dict[str, str] = field(default_factory=dict)
    fla_classes: Dict[int, str] = field(default_factory=dict)

    # ── Final output ──
    swf_bytes: bytes = b""

    # ── Progress reporting ──
    progress_callback: Optional[Callable[[str, int], None]] = None
    start_time: float = field(default_factory=time.time)

    def alloc_id(self) -> int:
        """Allocate a new SWF character ID."""
        cid = self.next_id
        self.next_id += 1
        return cid


# ══════════════════════════════════════════════════════════════════════
#                          PIPELINE STAGE BASE
# ══════════════════════════════════════════════════════════════════════

class PipelineStage(ABC):
    """
    Abstract base class for all compilation pipeline stages.

    Each stage implements:
      - execute(ctx): Perform stage-specific work on CompilationContext
      - rollback(ctx): Undo stage effects if later stages fail
      - name: Human-readable stage name for logging/progress
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable stage name."""
        pass

    @abstractmethod
    def execute(self, ctx: CompilationContext) -> None:
        """
        Execute this stage's work on the context.

        Args:
            ctx: Shared compilation context (modified in place)

        Raises:
            Exception: If stage fails (triggers rollback)
        """
        pass

    def rollback(self, ctx: CompilationContext) -> None:
        """
        Undo this stage's effects (optional).

        Default implementation does nothing. Override for stages that
        need cleanup (e.g., delete temp files, revert state).

        Args:
            ctx: Shared compilation context
        """
        pass


# ══════════════════════════════════════════════════════════════════════
#                         CONCRETE STAGES
# ══════════════════════════════════════════════════════════════════════

class LoadN2DStage(PipelineStage):
    """Stage 1: Load and parse N2D file."""

    @property
    def name(self) -> str:
        return "Load N2D"

    def execute(self, ctx: CompilationContext) -> None:
        from compile_n2d import load_n2d

        log.info("LoadN2DStage: loading %s", ctx.n2d_path)
        print(f"Loading: {ctx.n2d_path}")

        ctx.data, ctx.project_dir = load_n2d(ctx.n2d_path)
        if ctx.project_dir:
            print(f"  Project folder mode: {ctx.project_dir}")

        ctx.stage = ctx.data.get("stage", {})
        ctx.libs = ctx.data.get("libraries", [])
        ctx.id_to_lib = {lib["id"]: lib for lib in ctx.libs}
        print(f"  {len(ctx.libs)} libraries loaded")


class AllocateCharIDsStage(PipelineStage):
    """Stage 2: Assign SWF character IDs and build emission order."""

    @property
    def name(self) -> str:
        return "Allocate Char IDs"

    def execute(self, ctx: CompilationContext) -> None:
        log.info("AllocateCharIDsStage: assigning IDs to %d libs", len(ctx.libs))
        print("Assigning character IDs...")

        # ── 1. Assign character array indices (sequential, main=0) ──
        char_idx = 0
        ctx.lib_to_char_idx[0] = char_idx
        char_idx += 1

        for lib in ctx.libs:
            if lib["id"] == 0 or lib["type"] == "folder":
                continue
            ctx.lib_to_char_idx[lib["id"]] = char_idx
            char_idx += 1

        # ── 2. Determine dependency-ordered emission sequence ──
        emission_order: List[int] = []
        emitted: Set[int] = set()

        containers: Set[int] = set()
        all_non_folder: Dict[int, dict] = {}
        for lib in ctx.libs:
            if lib["type"] == "folder" or lib["id"] == 0:
                continue
            all_non_folder[lib["id"]] = lib
            if lib["type"] == "container":
                containers.add(lib["id"])

        # 2a. Sounds first
        for lib in ctx.libs:
            if lib["type"] == "sound" and lib["id"] != 0:
                emission_order.append(lib["id"])
                emitted.add(lib["id"])

        # 2b. Build full dependency graph for containers
        container_all_deps: Dict[int, List[int]] = {}
        for lib in ctx.libs:
            if lib["type"] != "container" or lib["id"] == 0:
                continue
            deps: List[int] = []
            for layer in lib.get("layers", []):
                for char in layer.get("characters", []):
                    ref = char["libraryId"]
                    if ref in all_non_folder and ref != lib["id"]:
                        deps.append(ref)
            container_all_deps[lib["id"]] = deps

        # Main timeline deps
        main_lib = ctx.id_to_lib.get(0)
        main_deps: List[int] = []
        if main_lib:
            for layer in main_lib.get("layers", []):
                for char in layer.get("characters", []):
                    ref = char["libraryId"]
                    if ref in all_non_folder:
                        main_deps.append(ref)

        # 2c. Walk containers in dependency order (topological, leaves first)
        from compile_n2d import N2DCompiler

        # We need to instantiate a temporary compiler to call _container_order
        # (FIXME: This should be refactored into a standalone helper function)
        temp_compiler = N2DCompiler.__new__(N2DCompiler)
        temp_compiler.libs = ctx.libs
        temp_compiler.id_to_lib = ctx.id_to_lib
        topo_order = temp_compiler._container_order()

        def _emit_deps(lib_id: int, _visiting: set = None):
            """Recursively emit all dependencies of a container."""
            if lib_id in emitted:
                return
            if _visiting is None:
                _visiting = set()
            if lib_id in _visiting:
                return  # cycle
            _visiting.add(lib_id)
            if lib_id in containers:
                for dep in container_all_deps.get(lib_id, []):
                    _emit_deps(dep, _visiting)
                emission_order.append(lib_id)
                emitted.add(lib_id)
            else:
                if lib_id not in emitted:
                    emission_order.append(lib_id)
                    emitted.add(lib_id)
            _visiting.discard(lib_id)

        for cid in topo_order:
            _emit_deps(cid)

        for dep in main_deps:
            _emit_deps(dep)

        # 2d. Any remaining unreferenced assets
        for lib_id in all_non_folder:
            if lib_id not in emitted:
                emission_order.append(lib_id)
                emitted.add(lib_id)

        # 2e. Reverse the non-sound portion
        sound_part = [lid for lid in emission_order
                      if all_non_folder[lid]["type"] == "sound"]
        non_sound_part = [lid for lid in emission_order
                          if all_non_folder[lid]["type"] != "sound"]
        non_sound_part.reverse()
        emission_order = sound_part + non_sound_part

        # ── 3. Assign SWF character IDs in emission order ──
        for lib_id in emission_order:
            if lib_id not in ctx.lib_to_swf_id:
                ctx.lib_to_swf_id[lib_id] = ctx.alloc_id()

        # ── 3b. Re-sort emission order by SWF character ID ascending ──
        emission_order.sort(key=lambda lid: ctx.lib_to_swf_id.get(lid, 0))

        # ── 3c. Defer root-timeline definitions ──
        root_def_ids = set(ctx.data.get('rootTimelineDefIds', []))
        deferred_lib_ids: List[int] = []
        deferred_swf_ids: Set[int] = set()
        if root_def_ids:
            deferred = []
            remaining = []
            for lid in emission_order:
                lib = ctx.id_to_lib.get(lid, {})
                orig_cid = lib.get("swfCharId")
                if orig_cid is not None and orig_cid in root_def_ids:
                    deferred.append(lid)
                    deferred_swf_ids.add(ctx.lib_to_swf_id.get(lid, 0))
                else:
                    remaining.append(lid)
            emission_order = remaining
            deferred_lib_ids = deferred

        ctx.emission_order = emission_order
        ctx.deferred_lib_ids = deferred_lib_ids
        ctx.deferred_swf_ids = deferred_swf_ids

        # ── 4. Build char_idx → swf_id mapping ──
        for lib_id, char_idx in ctx.lib_to_char_idx.items():
            if lib_id in ctx.lib_to_swf_id:
                ctx.char_idx_to_swf_id[char_idx] = ctx.lib_to_swf_id[lib_id]

        # ── 5. Build bitmap char IDs set ──
        for lib in ctx.libs:
            if lib["type"] == "bitmap" and lib["id"] in ctx.lib_to_swf_id:
                ctx.bitmap_char_ids.add(ctx.lib_to_swf_id[lib["id"]])

        # ── 6. Build original swfCharId → new swf_id mapping ──
        for lib in ctx.libs:
            orig_cid = lib.get("swfCharId")
            lid = lib["id"]
            new_id = ctx.lib_to_swf_id.get(lid)
            if orig_cid is not None and new_id is not None:
                ctx.orig_to_new_id[orig_cid] = new_id


class ParseRawTagsStage(PipelineStage):
    """Stage 3: Parse rawGlobalTags and fontAuxTags."""

    @property
    def name(self) -> str:
        return "Parse Raw Tags"

    def execute(self, ctx: CompilationContext) -> None:
        import struct
        from compile_n2d import _decode_raw_body, build_tag

        log.info("ParseRawTagsStage: parsing raw global tags")
        print("Parsing raw global tags...")

        raw_global = ctx.data.get("rawGlobalTags", [])
        for rgt in raw_global:
            tag_type = rgt["tagType"]
            body = _decode_raw_body(rgt["body"])
            if tag_type in (72, 82):  # DoABC, DoABC2
                ctx.raw_doabc_tags.extend(build_tag(tag_type, body))
            elif tag_type == 76:  # SymbolClass
                ctx.raw_aux_map[76] = body
            elif tag_type in (73, 74, 88):  # FontAlignZones, CSMTextSettings, FontName
                ref_cid = struct.unpack_from('<H', body, 0)[0] if len(body) >= 2 else 0
                target_lib_id = None
                for lib in ctx.libs:
                    if lib.get('swfCharId') == ref_cid:
                        target_lib_id = lib['id']
                        break
                new_swf_id = ctx.lib_to_swf_id.get(target_lib_id) if target_lib_id is not None else None
                if new_swf_id is not None and len(body) >= 2:
                    body = struct.pack('<H', new_swf_id) + body[2:]
                    ctx.font_aux_tags.setdefault(new_swf_id, []).append((tag_type, body))
                else:
                    log.warning('Font aux tag %d references unknown charId %d — skipped', tag_type, ref_cid)
            elif tag_type in (24, 45, 86):  # Protect, SoundStreamHead2, SceneAndFrameLabel
                ctx.raw_aux_tags.extend(build_tag(tag_type, body, force_long=(tag_type == 86)))
            elif tag_type in (57, 71):  # ImportAssets, ImportAssets2
                ctx.raw_aux_tags.extend(build_tag(tag_type, body, force_long=True))

        # Load font aux tags from library entries
        for lib in ctx.libs:
            if not lib.get("fontAuxTags"):
                continue
            lib_id = lib["id"]
            new_swf_id = ctx.lib_to_swf_id.get(lib_id)
            if new_swf_id is None:
                continue
            for fat in lib["fontAuxTags"]:
                tag_type = fat["tagType"]
                body = _decode_raw_body(fat["body"])
                if len(body) >= 2:
                    body = struct.pack('<H', new_swf_id) + body[2:]
                if new_swf_id not in ctx.font_aux_tags:
                    ctx.font_aux_tags.setdefault(new_swf_id, []).append((tag_type, body))


class DefineAssetsStage(PipelineStage):
    """Stage 4: Generate definition tags for all assets."""

    @property
    def name(self) -> str:
        return "Define Assets"

    def execute(self, ctx: CompilationContext) -> None:
        from compile_n2d import N2DCompiler

        log.info("DefineAssetsStage: defining %d assets", len(ctx.emission_order))
        print("Defining assets (dependency order)...")

        # We need to temporarily reconstruct an N2DCompiler instance
        # with our context data to call _define_all_assets
        # (FIXME: Refactor _define_all_assets into standalone helper functions)
        temp_compiler = N2DCompiler.__new__(N2DCompiler)
        temp_compiler.n2d_path = ctx.n2d_path
        temp_compiler.shared_dir = ctx.shared_dir
        temp_compiler.output_path = ctx.output_path
        temp_compiler.sdk_path = ctx.sdk_path
        temp_compiler.data = ctx.data
        temp_compiler.stage = ctx.stage
        temp_compiler.libs = ctx.libs
        temp_compiler.id_to_lib = ctx.id_to_lib
        temp_compiler._next_id = ctx.next_id
        temp_compiler._lib_to_swf_id = ctx.lib_to_swf_id
        temp_compiler._lib_to_char_idx = ctx.lib_to_char_idx
        temp_compiler._char_idx_to_swf_id = ctx.char_idx_to_swf_id
        temp_compiler._emission_order = ctx.emission_order
        temp_compiler._deferred_lib_ids = ctx.deferred_lib_ids
        temp_compiler._deferred_swf_ids = ctx.deferred_swf_ids
        temp_compiler._bitmap_char_ids = ctx.bitmap_char_ids
        temp_compiler._font_aux_tags = ctx.font_aux_tags
        temp_compiler._definition_tags = ctx.definition_tags
        temp_compiler._project_dir = ctx.project_dir
        temp_compiler._orig_to_new_id = ctx.orig_to_new_id

        temp_compiler._define_all_assets()

        # Copy back modified state
        ctx.definition_tags = temp_compiler._definition_tags
        ctx.next_id = temp_compiler._next_id


class BuildTimelineStage(PipelineStage):
    """Stage 5: Build root timeline with PlaceObject/RemoveObject tags."""

    @property
    def name(self) -> str:
        return "Build Timeline"

    def execute(self, ctx: CompilationContext) -> None:
        from compile_n2d import N2DCompiler

        log.info("BuildTimelineStage: building root timeline")
        print("Building root timeline...")

        temp_compiler = N2DCompiler.__new__(N2DCompiler)
        temp_compiler.data = ctx.data
        temp_compiler.stage = ctx.stage
        temp_compiler.libs = ctx.libs
        temp_compiler.id_to_lib = ctx.id_to_lib
        temp_compiler._lib_to_swf_id = ctx.lib_to_swf_id
        temp_compiler._lib_to_char_idx = ctx.lib_to_char_idx
        temp_compiler._bitmap_char_ids = ctx.bitmap_char_ids
        temp_compiler._deferred_lib_ids = ctx.deferred_lib_ids
        temp_compiler._deferred_swf_ids = ctx.deferred_swf_ids
        temp_compiler._font_aux_tags = ctx.font_aux_tags
        temp_compiler._definition_tags = bytearray()  # empty for deferred defs
        temp_compiler._project_dir = ctx.project_dir
        temp_compiler._orig_to_new_id = ctx.orig_to_new_id
        temp_compiler._char_idx_to_swf_id = ctx.char_idx_to_swf_id

        ctx.root_timeline_tags = temp_compiler._build_root_timeline()


class CompileAS3Stage(PipelineStage):
    """Stage 6: Compile ActionScript 3.0 bytecode."""

    @property
    def name(self) -> str:
        return "Compile AS3"

    def execute(self, ctx: CompilationContext) -> None:
        import os
        from compile_n2d import compile_as3

        log.info("CompileAS3Stage: compiling AS3")
        print("Compiling AS3...")

        scripts_modified = ctx.data.get('scriptsModified', False)
        use_raw_doabc = bool(ctx.raw_doabc_tags) and not scripts_modified

        if scripts_modified and ctx.raw_doabc_tags:
            print("  Scripts were modified — will recompile from source")

        if use_raw_doabc:
            ctx.doabc_tags = bytes(ctx.raw_doabc_tags)
            print(f"  Using raw DoABC from original: {len(ctx.doabc_tags)} bytes")
            for lib in ctx.libs:
                sym = lib.get("symbol", "")
                if sym:
                    ctx.sym_to_class[sym] = sym
        else:
            project_name = os.path.splitext(os.path.basename(ctx.n2d_path))[0]
            swc_path = os.path.join(ctx.shared_dir, "SSF2 API.swc")
            if ctx.sdk_path:
                try:
                    embedded_scripts = ctx.data.get('scripts', [])
                    ctx.doabc_tags, ctx.sym_to_class, ctx.fla_classes = compile_as3(
                        ctx.shared_dir, swc_path, ctx.sdk_path,
                        ctx.libs, "Main", project_name,
                        embedded_scripts=embedded_scripts,
                    )
                    print(f"  DoABC: {len(ctx.doabc_tags)} bytes")
                except Exception as e:
                    print(f"  AS3 compilation failed: {e}")
                    import traceback
                    traceback.print_exc()
                    if ctx.raw_doabc_tags:
                        ctx.doabc_tags = bytes(ctx.raw_doabc_tags)
                        print("  Falling back to raw DoABC from original")
                        for lib in ctx.libs:
                            sym = lib.get("symbol", "")
                            if sym:
                                ctx.sym_to_class[sym] = sym
                    else:
                        print("  Continuing without AS3 bytecode...")
            else:
                if scripts_modified:
                    print("  WARNING: Scripts were modified but no Flex SDK found")
                    if ctx.raw_doabc_tags:
                        ctx.doabc_tags = bytes(ctx.raw_doabc_tags)
                        for lib in ctx.libs:
                            sym = lib.get("symbol", "")
                            if sym:
                                ctx.sym_to_class[sym] = sym
                else:
                    print("  WARNING: No Flex SDK found — skipping AS3 compilation")


class AssembleSWFStage(PipelineStage):
    """Stage 7: Assemble final SWF file."""

    @property
    def name(self) -> str:
        return "Assemble SWF"

    def execute(self, ctx: CompilationContext) -> None:
        from compile_n2d import N2DCompiler

        log.info("AssembleSWFStage: assembling SWF")
        print("Assembling SWF...")

        temp_compiler = N2DCompiler.__new__(N2DCompiler)
        temp_compiler.data = ctx.data
        temp_compiler.stage = ctx.stage
        temp_compiler.libs = ctx.libs
        temp_compiler.id_to_lib = ctx.id_to_lib
        temp_compiler._lib_to_swf_id = ctx.lib_to_swf_id
        temp_compiler._lib_to_char_idx = ctx.lib_to_char_idx
        temp_compiler._char_idx_to_swf_id = ctx.char_idx_to_swf_id
        temp_compiler._definition_tags = ctx.definition_tags

        ctx.swf_bytes = temp_compiler._assemble_swf(
            ctx.root_timeline_tags,
            ctx.doabc_tags,
            ctx.sym_to_class,
            ctx.fla_classes,
            raw_aux_tags=bytes(ctx.raw_aux_tags),
            raw_aux_map=ctx.raw_aux_map
        )


class WriteOutputStage(PipelineStage):
    """Stage 8: Write SWF to disk."""

    @property
    def name(self) -> str:
        return "Write Output"

    def execute(self, ctx: CompilationContext) -> None:
        log.info("WriteOutputStage: writing %d bytes to %s", len(ctx.swf_bytes), ctx.output_path)
        with open(ctx.output_path, "wb") as f:
            f.write(ctx.swf_bytes)

        elapsed = time.time() - ctx.start_time
        print(f"Done! {len(ctx.swf_bytes):,} bytes -> {ctx.output_path} ({elapsed:.1f}s)")


# ══════════════════════════════════════════════════════════════════════
#                       COMPILATION PIPELINE
# ══════════════════════════════════════════════════════════════════════

class CompilationPipeline:
    """
    Manages execution of compilation pipeline stages.

    Features:
      - Sequential stage execution
      - Progress reporting
      - Error handling + rollback
      - Stage registration
    """

    def __init__(self):
        self.stages: List[PipelineStage] = []

    def add_stage(self, stage: PipelineStage) -> None:
        """Register a pipeline stage."""
        self.stages.append(stage)

    def execute(self, ctx: CompilationContext) -> CompilationContext:
        """
        Execute all registered pipeline stages.

        Args:
            ctx: Compilation context

        Returns:
            Modified context after all stages complete

        Raises:
            Exception: If any stage fails (after rollback)
        """
        log.info("CompilationPipeline.execute: %d stages", len(self.stages))
        completed_stages: List[PipelineStage] = []

        Profiler.start_session("n2d-export")
        Profiler.count("pipeline_stages", len(self.stages))

        try:
            for i, stage in enumerate(self.stages, start=1):
                log.info("Pipeline stage %d/%d: %s", i, len(self.stages), stage.name)
                if ctx.progress_callback:
                    ctx.progress_callback(stage.name, int((i - 1) / len(self.stages) * 100))

                with Profiler.timer(f"stage:{stage.name}"):
                    stage.execute(ctx)
                completed_stages.append(stage)

            if ctx.progress_callback:
                ctx.progress_callback("Complete", 100)

            # Record output stats
            if ctx.swf_bytes:
                Profiler.size("output_swf", len(ctx.swf_bytes))
            Profiler.count("libraries", len(ctx.libs) if ctx.libs else 0)
            Profiler.count("definition_tags", len(ctx.definition_tags) if ctx.definition_tags else 0)

            report = Profiler.end_session("n2d-export")
            if report:
                print(Profiler.format_report(report))

            return ctx

        except Exception as e:
            log.error("Pipeline failed at stage %s: %s", stage.name, e)
            print(f"ERROR: Pipeline failed at stage '{stage.name}': {e}")

            # Rollback completed stages in reverse order
            print("Rolling back completed stages...")
            for stage in reversed(completed_stages):
                try:
                    stage.rollback(ctx)
                except Exception as rollback_err:
                    log.error("Rollback failed for stage %s: %s", stage.name, rollback_err)

            raise


# ══════════════════════════════════════════════════════════════════════
#                            FACTORY
# ══════════════════════════════════════════════════════════════════════

def create_default_pipeline() -> CompilationPipeline:
    """
    Create a pipeline with all standard stages registered.

    Returns:
        CompilationPipeline ready for execution
    """
    pipeline = CompilationPipeline()
    pipeline.add_stage(LoadN2DStage())
    pipeline.add_stage(AllocateCharIDsStage())
    pipeline.add_stage(ParseRawTagsStage())
    pipeline.add_stage(DefineAssetsStage())
    pipeline.add_stage(BuildTimelineStage())
    pipeline.add_stage(CompileAS3Stage())
    pipeline.add_stage(AssembleSWFStage())
    pipeline.add_stage(WriteOutputStage())
    return pipeline
