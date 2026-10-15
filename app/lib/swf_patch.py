"""Patch an opened SWF with JPEXS instead of writing a new file."""

from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

SOURCE_NAME = "source-swf.json"


def remember_source_swf(project_dir: str, swf_path: str) -> str:
    """Store the opened SWF path beside project.n2d."""
    path = os.path.abspath(swf_path)
    os.makedirs(project_dir, exist_ok=True)
    dest = os.path.join(project_dir, SOURCE_NAME)
    with open(dest, "w", encoding="utf-8") as handle:
        json.dump({"swfPath": path}, handle)
    log.info("[patch] swf=%s kind=source", path)
    return path


def source_swf_path(project_dir: str) -> Optional[str]:
    """Return the opened SWF path, or None when this project was not opened from a SWF."""
    if not project_dir:
        return None
    dest = os.path.join(project_dir, SOURCE_NAME)
    if not os.path.isfile(dest):
        return None
    try:
        with open(dest, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    path = data.get("swfPath") if isinstance(data, dict) else None
    if not path or not os.path.isfile(path):
        return None
    return os.path.abspath(path)


def keep_opened_swf(project_dir: str, output_path: str) -> Optional[str]:
    """Copy the opened SWF. Returns the output path, or None when there is no opened SWF."""
    source = source_swf_path(project_dir)
    if not source:
        return None
    if os.path.abspath(source) != os.path.abspath(output_path):
        parent = os.path.dirname(os.path.abspath(output_path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        shutil.copyfile(source, output_path)
    log.info("[patch] swf=%s kind=keep", source)
    return output_path


def export_opened_swf(
    source: str,
    output_path: str,
    script_patches=None,
    text_patches=None,
    place_edits=None,
    project_dir: Optional[str] = None,
    sprite: int = 0,
) -> str:
    """Apply editor patches to a copy of the opened SWF and write that file."""
    scripts = _overlay_script_patches(source, script_patches)
    texts = _text_dir(text_patches)
    images = _subdir(project_dir, "patch", "images")
    sounds = _subdir(project_dir, "patch", "sounds")
    shapes = _subdir(project_dir, "patch", "shapes")
    places = place_edits or []
    if project_dir and not places:
        places = _places_file(project_dir)
    return patch_opened_swf(
        source,
        output_path,
        scripts=scripts,
        texts=texts,
        images=images,
        sounds=sounds,
        shapes=shapes,
        places=places,
        sprite=sprite,
    )


def patch_opened_swf(
    source: str,
    output_path: str,
    scripts: Optional[str] = None,
    texts: Optional[str] = None,
    images: Optional[str] = None,
    sounds: Optional[str] = None,
    shapes: Optional[str] = None,
    places=None,
    sprite: int = 0,
) -> str:
    """Patch one opened SWF. Each folder is a JPEXS import directory."""
    parent = os.path.dirname(os.path.abspath(output_path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(suffix=".swf", dir=parent or None)
    os.close(fd)
    shutil.copyfile(source, tmp_name)
    try:
        if scripts:
            _ffdec_import("importscript", tmp_name, scripts)
            log.info("[patch] swf=%s kind=script", output_path)
        if texts:
            _ffdec_import("importtext", tmp_name, texts)
            log.info("[patch] swf=%s kind=text", output_path)
        if images:
            _ffdec_import("importimages", tmp_name, images)
            log.info("[patch] swf=%s kind=image", output_path)
        if sounds:
            _ffdec_import("importsounds", tmp_name, sounds)
            log.info("[patch] swf=%s kind=sound", output_path)
        if shapes:
            _ffdec_import("importshapes", tmp_name, shapes)
            log.info("[patch] swf=%s kind=shape", output_path)
        if places:
            _placeedit(tmp_name, places, sprite)
            log.info("[patch] swf=%s kind=place", output_path)
        if not any((scripts, texts, images, sounds, shapes, places)):
            log.info("[patch] swf=%s kind=keep", output_path)
        os.replace(tmp_name, output_path)
    except Exception:
        if os.path.isfile(tmp_name):
            os.remove(tmp_name)
        raise
    return output_path


def render_frame(swf_path: str, frame: int, sprite: int, out_png: str) -> str:
    """Render one timeline frame with JPEXS and write a PNG."""
    frame = int(frame)
    sprite = int(sprite)
    kind = "frame" if sprite == 0 else "sprite"
    with tempfile.TemporaryDirectory() as folder:
        _ffdec([
            "-select", f"{sprite}:{frame}",
            "-export", kind, folder, swf_path,
        ])
        pngs = sorted(Path(folder).rglob("*.png"))
        if not pngs:
            raise RuntimeError(f"JPEXS wrote no PNG for sprite {sprite} frame {frame}")
        parent = os.path.dirname(os.path.abspath(out_png))
        if parent:
            os.makedirs(parent, exist_ok=True)
        shutil.copyfile(pngs[0], out_png)
    log.info("[preview] sprite=%s frame=%s wrote=%s", sprite, frame, out_png)
    return out_png


def _ffdec_import(command: str, swf_path: str, folder: str) -> None:
    _ffdec(["-" + command, swf_path, swf_path, folder])


def _ffdec(args: list) -> None:
    from toolchain_home import aflex_lite_dir, run_ffdec

    config = ["autoDeobfuscate=0"]
    sdk = aflex_lite_dir()
    if sdk:
        config.append("useFlexAs3Compiler=1")
        config.append("flexSdkLocation=" + sdk.replace("\\", "/"))
    else:
        config.append("useFlexAs3Compiler=0")
    code = run_ffdec(["-config", ",".join(config), *args])
    if code != 0:
        raise RuntimeError("ffdec exited " + str(code) + " for " + " ".join(args))


def _placeedit(swf_path: str, places, sprite: int) -> None:
    from toolchain_home import run_ffdec

    if isinstance(places, (str, os.PathLike)):
        spec = str(places)
        owned = False
    else:
        fd, spec = tempfile.mkstemp(suffix=".places.txt")
        os.close(fd)
        owned = True
        lines = [f"sprite {int(sprite)}"]
        for op in places:
            kind = op.get("op") or op.get("kind")
            frame = int(op["frame"])
            depth = int(op["depth"])
            tx = op.get("translateX", 0)
            ty = op.get("translateY", 0)
            if kind in ("transform", "move"):
                lines.append(f"transform {frame} {depth} {tx} {ty}")
            elif kind == "remove":
                lines.append(f"remove {frame} {depth}")
            elif kind == "add":
                lines.append(
                    f"add {frame} {depth} {int(op['character'])} {tx} {ty}"
                )
            else:
                raise ValueError("unknown place op " + str(kind))
        Path(spec).write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        code = run_ffdec(["-placeedit", swf_path, spec])
        if code != 0:
            raise RuntimeError("placeedit exited " + str(code))
    finally:
        if owned and os.path.isfile(spec):
            os.remove(spec)


def _overlay_script_patches(swf_path: str, script_patches) -> Optional[str]:
    """Export scripts, then replace the files whose names match the editor patches."""
    scripts = script_patches
    if isinstance(script_patches, dict):
        if not script_patches.get("scriptsModified"):
            return None
        scripts = script_patches.get("scripts") or []
    if not isinstance(scripts, list) or not scripts:
        return None
    folder = tempfile.mkdtemp(prefix="n2f-scripts-")
    _ffdec(["-export", "script", folder, swf_path])
    files = list(Path(folder).rglob("*.as"))
    wrote = 0
    for item in scripts:
        if not isinstance(item, dict):
            continue
        source = item.get("source")
        if not isinstance(source, str):
            continue
        name = os.path.basename(str(item.get("path") or item.get("name") or "").replace("\\", "/"))
        targets = [path for path in files if name and path.name.lower() == name.lower()]
        if not targets and len(files) == 1:
            targets = files
        if not targets and name:
            target = Path(folder, name if name.endswith(".as") else name + ".as")
            target.write_text(source, encoding="utf-8")
            wrote += 1
            continue
        for target in targets:
            target.write_text(source, encoding="utf-8")
            wrote += 1
    if wrote == 0:
        shutil.rmtree(folder, ignore_errors=True)
        return None
    return folder


def _text_dir(text_patches) -> Optional[str]:
    if not text_patches:
        return None
    folder = tempfile.mkdtemp(prefix="n2f-text-")
    texts = Path(folder, "texts")
    texts.mkdir()
    wrote = 0
    for item in text_patches:
        if not isinstance(item, dict):
            continue
        cid = item.get("swfCharId")
        if cid is None:
            continue
        text = item.get("text")
        if text is None:
            text = item.get("initialText", "")
        Path(texts, f"{int(cid)}.txt").write_text(str(text), encoding="utf-8")
        wrote += 1
    if wrote == 0:
        shutil.rmtree(folder, ignore_errors=True)
        return None
    return folder


def _subdir(project_dir: Optional[str], *parts: str) -> Optional[str]:
    if not project_dir:
        return None
    path = os.path.join(project_dir, *parts)
    if os.path.isdir(path) and any(os.scandir(path)):
        return path
    return None


def _places_file(project_dir: str):
    path = os.path.join(project_dir, "patch", "places.txt")
    if os.path.isfile(path):
        return path
    return None
