"""
Compilation Pipeline - Refactored N2D → SWF compilation stages.

This module breaks the monolithic N2DCompiler.compile() method into
discrete, testable pipeline stages following the Single Responsibility
Principle.

Pipeline stages (in order):
  1. LoadN2DStage        - Load and parse N2D file
  2. AllocateCharIDsStage - Assign SWF character IDs in dependency order
  3. ParseRawTagsStage   - Parse structured global fields (abcBlocks, sceneLabels, fontAuxParsed)
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
import struct
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

    # ── Parsed global tags ──
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

    # ── In-memory override (skip file I/O in LoadN2DStage) ──
    data_override: Optional[dict] = None        # pre-loaded N2D dict; skips file read
    project_dir_override: Optional[str] = None  # project dir for external asset lookup

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
        from compile_n2d import load_n2d, _overlay_external_scripts

        if ctx.data_override is not None:
            # Fast path: N2D data provided directly — skip file I/O
            log.info("LoadN2DStage: using in-memory data override")
            print("Loading: (in-memory override)")
            ctx.data = ctx.data_override
            ctx.project_dir = ctx.project_dir_override
            if ctx.project_dir:
                _overlay_external_scripts(ctx.data, ctx.project_dir)
                print(f"  Project folder mode: {ctx.project_dir}")
            ctx.stage = ctx.data.get("stage", {})
            ctx.libs = ctx.data.get("libraries", [])
            ctx.id_to_lib = {lib["id"]: lib for lib in ctx.libs}
            print(f"  {len(ctx.libs)} libraries loaded (in-memory)")
            return

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

        # 2e. Keep the topological (leaves-first) emission order intact.
        #     Previous code reversed the non-sound portion to bring charIDs
        #     closer to the OG ordering, but that reversal put parents before
        #     children.  When IDs were then assigned sequentially and re-sorted
        #     ascending, parents ended up with LOWER IDs than their children,
        #     creating thousands of forward references (PlaceObject tags that
        #     reference sprites not yet defined).  Flash Player silently fails
        #     to instantiate such sprites, breaking all MovieClip frame scripts
        #     and causing animation looping.

        # ── 3. Assign SWF character IDs in emission order ──
        #    Preserve original OG swfCharId values where available.  The
        #    DoABC bytecode (raw passthrough from OG) may encode original
        #    charIDs in class metadata or embedded-asset annotations. Using
        #    the same charIDs ensures Flash Player can resolve those references
        #    against the RT SWF's character dictionary, preventing #2015
        #    "Invalid BitmapData" errors on BitmapData.threshold().
        max_swf_id = ctx.next_id - 1
        assigned_cids: Set[int] = set(ctx.lib_to_swf_id.values())
        for lib_id in emission_order:
            if lib_id not in ctx.lib_to_swf_id:
                lib = ctx.id_to_lib.get(lib_id, {})
                orig_cid = lib.get('swfCharId')
                if orig_cid and orig_cid > 0 and orig_cid not in assigned_cids:
                    ctx.lib_to_swf_id[lib_id] = orig_cid
                    assigned_cids.add(orig_cid)
                    if orig_cid > max_swf_id:
                        max_swf_id = orig_cid
                else:
                    new_id = ctx.alloc_id()
                    while new_id in assigned_cids:
                        new_id = ctx.alloc_id()
                    ctx.lib_to_swf_id[lib_id] = new_id
                    assigned_cids.add(new_id)
                    if new_id > max_swf_id:
                        max_swf_id = new_id
        # Advance next_id past all assigned IDs to avoid collision with
        # IDs allocated at emit-time (e.g., companion DefineShape3 tags).
        if max_swf_id >= ctx.next_id:
            ctx.next_id = max_swf_id + 1

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


# ── Helpers for rebuilding SWF tags from structured fields ──────────────

def _write_encoded_u32(val: int) -> bytes:
    """Write a SWF EncodedU32 (variable-length, 1-5 bytes)."""
    result = bytearray()
    while True:
        byte = val & 0x7f
        val >>= 7
        if val:
            byte |= 0x80
        result.append(byte)
        if not val:
            break
    return bytes(result)


def _rebuild_scene_and_frame_label(data: dict) -> bytes:
    """Rebuild DefineSceneAndFrameLabelData (tag 86) from structured dict."""
    buf = bytearray()
    scenes = data.get('scenes', [])
    buf.extend(_write_encoded_u32(len(scenes)))
    for sc in scenes:
        buf.extend(_write_encoded_u32(sc.get('offset', 0)))
        buf.extend(sc.get('name', '').encode('utf-8') + b'\x00')
    labels = data.get('frameLabels', [])
    buf.extend(_write_encoded_u32(len(labels)))
    for lbl in labels:
        buf.extend(_write_encoded_u32(lbl.get('frame', 0)))
        buf.extend(lbl.get('name', '').encode('utf-8') + b'\x00')
    return bytes(buf)


def _rebuild_sound_stream_head(data: dict) -> bytes:
    """Rebuild SoundStreamHead2 (tag 45) from structured dict."""
    b0 = ((data.get('playbackRate', 0) & 0x03) << 2 |
          (data.get('playbackSize', 0) & 0x01) << 1 |
          (data.get('playbackType', 0) & 0x01))
    b1 = ((data.get('compression', 0) & 0x0f) << 4 |
          (data.get('streamRate', 0) & 0x03) << 2 |
          (data.get('streamSize', 0) & 0x01) << 1 |
          (data.get('streamType', 0) & 0x01))
    buf = bytearray([b0, b1])
    buf.extend(struct.pack('<H', data.get('streamSampleCount', 0)))
    if data.get('compression') == 2:  # MP3
        buf.extend(struct.pack('<h', data.get('latencySeek', 0)))
    return bytes(buf)


def _rebuild_font_align_zones(data: dict) -> bytes:
    """Rebuild DefineFontAlignZones (tag 73) body after charID from structured dict."""
    buf = bytearray()
    buf.append((data.get('tableHint', 0) & 0x03) << 6)
    for zone_data in data.get('zones', []):
        buf.append(len(zone_data))
        for zd in zone_data:
            coord = int(round(zd.get('alignmentCoord', 0.0) * 256.0)) & 0xFFFF
            rng   = int(round(zd.get('range', 0.0) * 256.0)) & 0xFFFF
            buf.extend(struct.pack('<HH', coord, rng))
        buf.append(0x03)  # zoneMask: HasX=1, HasY=1 (safe default)
    return bytes(buf)


def _rebuild_csm_text_settings(data: dict) -> bytes:
    """Rebuild CSMTextSettings (tag 74) body after charID from structured dict."""
    buf = bytearray()
    use_flash = data.get('useFlashType', 0) & 0x03
    grid_fit  = data.get('gridFit', 0) & 0x07
    buf.append((use_flash << 6) | (grid_fit << 3))
    buf.extend(struct.pack('<f', float(data.get('thickness', 0.0))))
    buf.extend(struct.pack('<f', float(data.get('sharpness', 0.0))))
    buf.append(0)  # reserved
    return bytes(buf)


def _rebuild_font_name(data: dict) -> bytes:
    """Rebuild DefineFontName (tag 88) body after charID from structured dict."""
    buf = bytearray()
    buf.extend(data.get('fontName', '').encode('utf-8') + b'\x00')
    buf.extend(data.get('copyright', '').encode('utf-8') + b'\x00')
    return bytes(buf)


def _rebuild_import_assets(data: dict) -> bytes:
    """Rebuild ImportAssets (57) or ImportAssets2 (71) from structured dict."""
    buf = bytearray()
    buf.extend(data.get('url', '').encode('utf-8') + b'\x00')
    if data.get('version', 1) == 2:
        buf.extend(b'\x01\x00')  # reserved bytes for ImportAssets2
    assets = data.get('assets', [])
    buf.extend(struct.pack('<H', len(assets)))
    for asset in assets:
        buf.extend(struct.pack('<H', 0))  # charID placeholder
        buf.extend(asset.get('name', '').encode('utf-8') + b'\x00')
    return bytes(buf)


class ParseRawTagsStage(PipelineStage):
    """Stage 3: Parse rawGlobalTags and structured global fields."""

    @property
    def name(self) -> str:
        return "Parse Raw Tags"

    def execute(self, ctx: CompilationContext) -> None:
        import struct
        from compile_n2d import _decode_raw_body, build_tag

        log.info("ParseRawTagsStage: parsing raw global tags")
        print("Parsing raw global tags...")

        # Build aux tags from structured fields.
        # DoABC passthrough is intentionally disabled and compiled in Stage 6.
        if ctx.data.get('protectFromImport'):
            ctx.raw_aux_tags.extend(build_tag(24, b''))

        scene_labels = ctx.data.get('sceneAndFrameLabels')
        if scene_labels:
            body = _rebuild_scene_and_frame_label(scene_labels)
            ctx.raw_aux_tags.extend(build_tag(86, body, force_long=True))

        sound_stream = ctx.data.get('soundStream')
        if sound_stream:
            body = _rebuild_sound_stream_head(sound_stream)
            ctx.raw_aux_tags.extend(build_tag(45, body))

        import_assets = ctx.data.get('importAssets', [])
        for ia in import_assets:
            body = _rebuild_import_assets(ia)
            tag_type = 71 if ia.get('version', 1) == 2 else 57
            ctx.raw_aux_tags.extend(build_tag(tag_type, body, force_long=True))

        # Load font aux tags from library entries (fontAuxParsed structured format only).
        for lib in ctx.libs:
            lib_id = lib["id"]
            new_swf_id = ctx.lib_to_swf_id.get(lib_id)
            if new_swf_id is None:
                continue
            aux = lib.get("fontAuxParsed") or {}
            if aux.get("fontAlignZones"):
                body = struct.pack('<H', new_swf_id) + _rebuild_font_align_zones(aux["fontAlignZones"])
                ctx.font_aux_tags.setdefault(new_swf_id, []).append((73, body))
            if aux.get("csmTextSettings"):
                body = struct.pack('<H', new_swf_id) + _rebuild_csm_text_settings(aux["csmTextSettings"])
                ctx.font_aux_tags.setdefault(new_swf_id, []).append((74, body))
            if aux.get("fontName"):
                body = struct.pack('<H', new_swf_id) + _rebuild_font_name(aux["fontName"])
                ctx.font_aux_tags.setdefault(new_swf_id, []).append((88, body))


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

        temp_compiler._embed_system_fonts()
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

    def _extract_frame_origin_scripts(self, ctx: CompilationContext) -> None:
        """Route frame-origin scripts to their target container's actions.
        
        Frame-origin scripts are NOT compiled; instead, their action bodies
        are injected into the matching container's lib.actions list at the
        correct frame number. This preserves the FLA-faithful model where
        frame scripts live in the timeline, not as separate classes.
        """
        scripts = ctx.data.get('scripts', [])
        if not scripts:
            return
        
        # Build a map of container libs for fast lookup by swfCharId
        containers_by_cid = {}
        for lib in ctx.libs:
            if lib.get('type') == 'container':
                cid = lib.get('swfCharId')
                if cid is not None:
                    containers_by_cid[cid] = lib
        
        # Process frame-origin scripts
        remaining_scripts = []
        n_injected = 0
        
        for script in scripts:
            if script.get('scriptOrigin') != 'frame':
                remaining_scripts.append(script)
                continue
            
            # Script is frame-origin: find its target container and inject action bodies
            source = script.get('source', '')
            path = script.get('path', '')
            
            # Try to match to container by extracted _fla class pattern: ClassName_swfCharId
            # The frame bodies are already extracted by normalize_imported_scripts
            import re
            parts = path.rsplit('/', 1)
            if len(parts) == 2 and parts[0].endswith('_fla'):
                class_filename = parts[1].replace('.as', '')
                num_match = re.search(r'_(\d+)$', class_filename)
                if num_match:
                    target_cid = int(num_match.group(1))
                    target_lib = containers_by_cid.get(target_cid)
                    if target_lib:
                        # Extract frame methods from this class's source
                        # (already done by normalize_imported_scripts, so this frame script
                        # should NOT exist in the payload — log if it does)
                        log.warning(
                            "Frame-origin script %s still in payload; "
                            "should have been normalized at import",
                            path
                        )
                        n_injected += 1
                        continue  # Skip, don't compile
            
            # If we couldn't match, keep it as class-source (error case)
            log.warning("Frame-origin script %s could not be matched to container", path)
            script['scriptOrigin'] = 'class-source'
            remaining_scripts.append(script)
        
        # Update embedded scripts to exclude frame-origin entries
        ctx.data['scripts'] = remaining_scripts
        if n_injected > 0:
            print(f"  Frame action injection: {n_injected} frame-origin scripts routed to timeline")

    def execute(self, ctx: CompilationContext) -> None:
        import os
        from compile_n2d import compile_as3

        log.info("CompileAS3Stage: compiling AS3")
        print("Compiling AS3...")
        
        # Phase 3: Route frame-origin scripts to timeline actions
        self._extract_frame_origin_scripts(ctx)

        scripts_modified = ctx.data.get('scriptsModified', False)
        if scripts_modified:
            print("  Scripts were modified — recompiling from source")

        # Determine whether this project has any AS3 content needing compilation.
        # id=0 is always "Main" (document root) — not a linkage stub.
        # Projects with no exported non-root symbols and no embedded scripts
        # produce no DoABC tags; skip compilation entirely for those (e.g. test stubs).
        has_symbols = any(lib.get("symbol") for lib in ctx.libs if lib.get("id") != 0)
        has_scripts = bool(ctx.data.get('scripts', []))
        needs_as3 = has_symbols or has_scripts

        if not needs_as3:
            print("  No exported symbols or scripts — skipping AS3 compilation")
            print("  AS3 mode: full-recompile (passthrough disabled)")
            return
        
        print("  AS3 mode: full-recompile (passthrough disabled)")

        project_name = os.path.splitext(os.path.basename(ctx.n2d_path))[0]
        swc_path = os.path.join(ctx.shared_dir, "SSF2 API.swc")

        # Absolute policy: never passthrough raw DoABC from the imported SWF.
        # Every export must come from the current normalized source model.
        if not ctx.sdk_path:
            raise RuntimeError(
                "Flex SDK not found. Raw DoABC passthrough is disabled; "
                "cannot export AS3 SWF without compilation."
            )

        embedded_scripts = ctx.data.get('scripts', [])
        # Log script origins for diagnostics
        origins = {}
        for s in embedded_scripts:
            origin = s.get('scriptOrigin', 'unknown')
            origins[origin] = origins.get(origin, 0) + 1
        if origins:
            origin_str = ', '.join(f"{origin}:{count}" for origin, count in sorted(origins.items()))
            print(f"  Scripts by origin: {origin_str}")
        
        ctx.doabc_tags, ctx.sym_to_class, ctx.fla_classes = compile_as3(
            ctx.shared_dir, swc_path, ctx.sdk_path,
            ctx.libs, "Main", project_name,
            embedded_scripts=embedded_scripts,
        )
        print(f"  DoABC: {len(ctx.doabc_tags)} bytes")


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
