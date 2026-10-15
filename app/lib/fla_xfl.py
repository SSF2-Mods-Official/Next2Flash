"""FLA and XFL projects.

A .fla file is a zip of an XFL folder. The editor cache is
bin/next2flash.n2d inside that zip. JPEXS FFDec writes the XFL body
from a SWF when `n2f fla` runs. The editor's `n2f compile` does not
read this file.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET

log = logging.getLogger(__name__)

CACHE_REL = os.path.join("bin", "next2flash.n2d")
SOURCE_NAME = "source.json"
STAMP_NAME = ".fla-stamp"
PARSE_VERSION = "5"
PARSE_MARKER = ".xfl-parse-version"
XFL_NS = "http://ns.adobe.com/xfl/2008/"


class FlaError(Exception):
    pass


def export_swf_to_fla(swf_path: str, fla_path: str) -> int:
    """Write a CS6 FLA for a SWF. FFDec builds the XFL. The editor cache is stored inside."""
    swf_path = os.path.abspath(swf_path)
    fla_path = os.path.abspath(fla_path)
    if not os.path.isfile(swf_path):
        print(f"Error: file not found: {swf_path}", flush=True)
        return 1

    log.info("[fla] input=%s", swf_path)
    os.makedirs(os.path.dirname(fla_path) or ".", exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="n2f-fla-") as tmp:
        n2d_path = os.path.join(tmp, "cache.n2d")
        _write_n2d_from_swf(swf_path, n2d_path)
        if _pack_fla(swf_path, n2d_path, fla_path, tmp) != 0:
            return 1

    log.info("[fla] ffdec=ok cache=bin/next2flash.n2d wrote=%s", fla_path)
    print(f"DONE: {fla_path} ({os.path.getsize(fla_path):,} bytes)", flush=True)
    return 0


def materialize(path: str) -> str:
    """Return a work folder that contains project.n2d for a FLA, XFL, or existing project."""
    path = os.path.abspath(path)
    if os.path.isfile(path):
        ext = os.path.splitext(path)[1].lower()
        if ext == ".fla":
            return _materialize_fla(path)
        if ext == ".xfl":
            return _ensure_cache(os.path.dirname(path), kind="xfl", source=os.path.dirname(path))
        if ext == ".n2d":
            return _materialize_n2d_file(path)
        raise FlaError(f"Not a FLA or XFL file: {path}")
    if not os.path.isdir(path):
        raise FlaError(f"Project not found: {path}")
    link = _read_source(path)
    if link and link.get("kind") == "fla" and os.path.isfile(os.path.join(path, "project.n2d")):
        log.info("[fla] open kind=fla work=%s", path)
        return path
    if os.path.isfile(os.path.join(path, "DOMDocument.xml")):
        return _ensure_cache(path, kind="xfl", source=path)
    if os.path.isfile(os.path.join(path, "project.n2d")):
        return path
    raise FlaError(f"No DOMDocument.xml or project cache in {path}")


def resolve_compile_path(path: str) -> str:
    """Return the .n2d file or project folder compile_n2d already accepts."""
    path = os.path.abspath(path)
    ext = os.path.splitext(path)[1].lower()
    if os.path.isfile(path) and ext == ".n2d":
        return path
    if os.path.isdir(path) and os.path.isfile(os.path.join(path, "project.n2d")) and not os.path.isfile(os.path.join(path, "DOMDocument.xml")):
        return path
    work = materialize(path)
    return work


def sync_project(work_dir: str) -> None:
    """Copy the editor cache back into the FLA or XFL and refresh the stage size."""
    link = _read_source(work_dir)
    n2d_path = os.path.join(work_dir, "project.n2d")
    if not link or not os.path.isfile(n2d_path):
        return
    _update_dom_stage(work_dir, n2d_path)
    cache = os.path.join(work_dir, CACHE_REL)
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    shutil.copyfile(n2d_path, cache)
    if link.get("kind") == "fla" and link.get("source"):
        _zip_xfl(work_dir, link["source"])
        log.info("[fla] sync kind=fla wrote=%s", link["source"])
    else:
        log.info("[fla] sync kind=%s wrote=%s", link.get("kind"), work_dir)


def attach_swf(work_dir: str, swf_path: str) -> str:
    """After a SWF import, write a sibling .fla and remember it on the work folder."""
    work_dir = os.path.abspath(work_dir)
    name = os.path.basename(work_dir.rstrip("\\/"))
    fla_path = os.path.join(os.path.dirname(work_dir), name + ".fla")
    n2d_path = os.path.join(work_dir, "project.n2d")
    if not os.path.isfile(n2d_path):
        raise FlaError(f"No project cache in {work_dir}")
    with tempfile.TemporaryDirectory(prefix="n2f-fla-") as tmp:
        if _pack_fla(swf_path, n2d_path, fla_path, tmp) != 0:
            raise FlaError(f"FFDec did not write {fla_path}")
    _extract_zip(fla_path, work_dir)
    if os.path.isfile(os.path.join(work_dir, CACHE_REL)):
        shutil.copyfile(os.path.join(work_dir, CACHE_REL), n2d_path)
    _write_source(work_dir, kind="fla", source=fla_path)
    _write_stamp(work_dir, fla_path)
    log.info("[fla] attach wrote=%s", fla_path)
    return fla_path


def mark_xfl(work_dir: str, stage: dict | None = None) -> None:
    """Make a project folder an XFL folder with a DOMDocument."""
    stage = stage or {}
    dom = os.path.join(work_dir, "DOMDocument.xml")
    if not os.path.isfile(dom):
        _write_dom(dom, stage)
    _write_source(work_dir, kind="xfl", source=os.path.abspath(work_dir))
    log.info("[fla] mark kind=xfl wrote=%s", work_dir)


def xfl_to_n2d(xfl_dir: str, source_file: str | None = None) -> dict:
    """Build an editor project from DOMDocument.xml, library symbols, media, and .as files."""
    dom_path = os.path.join(xfl_dir, "DOMDocument.xml")
    if not os.path.isfile(dom_path):
        raise FlaError(f"DOMDocument.xml not found in {xfl_dir}")
    root = ET.parse(dom_path).getroot()
    name = os.path.basename(xfl_dir.rstrip("\\/")) or "project"
    if source_file and not os.path.isdir(source_file):
        stem = os.path.splitext(os.path.basename(source_file))[0]
        if stem:
            name = stem
    width = int(float(root.attrib.get("width", "550") or 550))
    height = int(float(root.attrib.get("height", "400") or 400))
    fps = float(root.attrib.get("frameRate", "24") or 24)
    bg = root.attrib.get("backgroundColor") or "#333333"
    if not bg.startswith("#"):
        bg = "#" + bg
    index = _index_files(xfl_dir)

    libraries = []
    by_path = {}
    folder_ids = {}
    next_id = 1
    counts = {"folder": 0, "bitmap": 0, "sound": 0, "shape": 0, "frameScripts": 0}

    def add(entry, key=None):
        nonlocal next_id
        entry["id"] = next_id
        libraries.append(entry)
        if key:
            by_path[key] = next_id
        next_id += 1
        return entry["id"]

    def ensure_folders(full_name):
        parts = [part for part in full_name.replace("\\", "/").split("/") if part]
        if len(parts) <= 1:
            return 0, parts[-1] if parts else full_name
        parent = 0
        acc = []
        for part in parts[:-1]:
            acc.append(part)
            key = "/".join(acc)
            if key not in folder_ids:
                folder_ids[key] = add({
                    "name": part,
                    "type": "folder",
                    "symbol": "",
                    "folderId": parent,
                    "mode": "close",
                })
                counts["folder"] += 1
            parent = folder_ids[key]
        return parent, parts[-1]

    for item in _walk(root, "DOMBitmapItem"):
        full_name = item.attrib.get("name") or "Bitmap"
        folder_id, leaf = ensure_folders(full_name)
        href = item.attrib.get("href") or ""
        media = _lookup(index, "LIBRARY/" + href, href, leaf)
        if media and media.lower().endswith(".dat"):
            media = _lookup(index, "LIBRARY/" + href, href)
        width_px, height_px, buffer = _load_bitmap(media)
        if not width_px:
            width_px = int(float(item.attrib.get("frameRight", "0") or 0) / 20) or width_px
            height_px = int(float(item.attrib.get("frameBottom", "0") or 0) / 20) or height_px
        compression = item.attrib.get("compressionType") or "photo"
        add({
            "name": leaf,
            "type": "bitmap",
            "symbol": _linkage(item),
            "folderId": folder_id,
            "width": width_px,
            "height": height_px,
            "imageType": "image/png",
            "buffer": buffer,
            "rawBitmapFormat": 5,
            "rawTagType": 36 if compression == "lossless" else 35,
            "jpegQuality": int(float(item.attrib.get("quality", "80") or 80)),
        }, full_name)
        counts["bitmap"] += 1

    for item in _walk(root, "DOMSoundItem"):
        full_name = item.attrib.get("name") or "Sound"
        folder_id, leaf = ensure_folders(full_name)
        href = item.attrib.get("href") or item.attrib.get("soundDataHRef") or ""
        media = _lookup(index, "LIBRARY/" + href, href, os.path.basename(href))
        raw = b""
        fmt = "unknown"
        if media and os.path.isfile(media) and not media.lower().endswith(".dat"):
            with open(media, "rb") as handle:
                raw = handle.read()
            fmt = os.path.splitext(media)[1].lstrip(".").lower() or "unknown"
        add({
            "name": leaf,
            "type": "sound",
            "symbol": _linkage(item),
            "folderId": folder_id,
            "buffer": raw,
            "soundFormat": fmt,
            "volume": 100,
            "loopCount": 0,
        }, full_name)
        counts["sound"] += 1

    symbol_nodes = []
    seen_symbols = set()
    for inc in _walk(root, "Include"):
        href = (inc.attrib.get("href") or "").replace("\\", "/")
        symbol_path = _lookup(index, "LIBRARY/" + href, href)
        if symbol_path and os.path.isfile(symbol_path):
            symbol_nodes.append(ET.parse(symbol_path).getroot())
    for item in _walk(root, "DOMSymbolItem"):
        symbol_nodes.append(item)

    symbol_layers = []
    for node in symbol_nodes:
        full_name = node.attrib.get("name") or ""
        if not full_name or full_name in seen_symbols or full_name in by_path:
            continue
        seen_symbols.add(full_name)
        folder_id, leaf = ensure_folders(full_name)
        symbol_layers.append((full_name, node))
        add({
            "name": leaf,
            "type": "container",
            "symbol": _linkage(node),
            "folderId": folder_id,
            "totalFrame": 1,
            "currentFrame": 1,
            "leftFrame": 1,
            "layers": [],
            "labels": [],
            "sounds": [],
            "actions": [],
        }, full_name)

    place_id = next_id

    def place_id_next():
        nonlocal place_id
        place_id += 1
        return place_id

    def add_shape(shape_name, recodes, bounds):
        counts["shape"] += 1
        return add({
            "name": shape_name,
            "type": "shape",
            "symbol": "",
            "folderId": 0,
            "bitmapId": 0,
            "inBitmap": False,
            "recodes": recodes,
            "bounds": bounds,
        })

    texts_folder = {"id": 0}

    def add_text(label, fields):
        if not texts_folder["id"]:
            texts_folder["id"] = add({
                "name": "texts",
                "type": "folder",
                "symbol": "",
                "folderId": 0,
                "mode": "close",
            })
            counts["folder"] += 1
        counts["text"] = counts.get("text", 0) + 1
        entry = {
            "name": label,
            "type": "text",
            "symbol": "",
            "folderId": texts_folder["id"],
        }
        entry.update(fields)
        return add(entry)

    for full_name, node in symbol_layers:
        lib = next(entry for entry in libraries if entry["id"] == by_path[full_name])
        layers, frames, actions, labels = _layers_from_timeline(
            node, by_path, place_id_next, add_shape, add_text)
        lib["layers"] = layers
        lib["totalFrame"] = frames
        lib["actions"] = actions
        lib["labels"] = labels
        counts["frameScripts"] += len(actions)

    main_layers, main_frames, main_actions, main_labels = _layers_from_timeline(
        root, by_path, place_id_next, add_shape, add_text)
    if not main_layers:
        main_layers = [_empty_layer("Layer 1")]
        main_frames = 1
    counts["frameScripts"] += len(main_actions)
    occupied = [
        int(char.get("startFrame") or 1)
        for layer in main_layers
        for char in (layer.get("characters") or [])
    ]
    libraries.insert(0, {
        "id": 0,
        "name": "main",
        "type": "container",
        "symbol": "",
        "folderId": 0,
        "totalFrame": main_frames,
        "currentFrame": min(occupied) if occupied else 1,
        "leftFrame": 1,
        "layers": main_layers,
        "labels": main_labels,
        "sounds": [],
        "actions": main_actions,
    })

    scripts = _read_scripts(xfl_dir)
    scripts.extend(_read_classpath_scripts(root, source_file or xfl_dir, scripts))
    log.info(
        "[fla] xfl libs=%d folders=%d bitmaps=%d sounds=%d shapes=%d scripts=%d frameScripts=%d stage=%sx%s fps=%s",
        len(libraries), counts["folder"], counts["bitmap"], counts["sound"],
        counts["shape"], len(scripts), counts["frameScripts"], width, height, fps,
    )
    return {
        "version": 1,
        "name": name,
        "characterId": place_id + 1,
        "stage": {
            "width": width,
            "height": height,
            "fps": fps,
            "bgColor": bg,
            "lock": False,
        },
        "libraries": libraries,
        "plugins": [],
        "scripts": scripts,
        "setting": {
            "timelineHeight": 280,
            "controllerWidth": 360,
            "ruler": False,
            "rulerX": [],
            "rulerY": [],
        },
    }


def _pack_fla(swf_path: str, n2d_path: str, fla_path: str, tmp: str) -> int:
    xfl_dir = os.path.join(tmp, "xfl")
    os.makedirs(xfl_dir, exist_ok=True)
    ffdec_status = _ffdec_export_fla(swf_path, xfl_dir)
    if ffdec_status != "ok" or not os.path.isfile(os.path.join(xfl_dir, "DOMDocument.xml")):
        print("FFDec did not write a FLA.", flush=True)
        log.info("[fla] ffdec=%s wrote=", ffdec_status)
        return 1
    bin_dir = os.path.join(xfl_dir, "bin")
    os.makedirs(bin_dir, exist_ok=True)
    shutil.copyfile(n2d_path, os.path.join(bin_dir, "next2flash.n2d"))
    _zip_xfl(xfl_dir, fla_path)
    log.info("[fla] ffdec=ok cache=bin/next2flash.n2d wrote=%s", fla_path)
    return 0


def _write_n2d_from_swf(swf_path: str, n2d_path: str) -> None:
    import swf_to_n2d as mod

    name = os.path.splitext(os.path.basename(swf_path))[0]
    with open(swf_path, "rb") as handle:
        swf_data = handle.read()
    header, tags = mod.parse_swf(swf_data)
    builder = mod.N2DBuilder(header, name=name)
    builder.catalog_swf_tags(tags)
    scripts, frame_scripts = mod.decompile_all_scripts(builder.global_raw_tags)
    builder.frame_scripts = frame_scripts
    if scripts:
        builder.scripts.extend(scripts)
    builder.build_all()
    builder.build_main_timeline(tags)
    mod.save_n2d(builder.to_n2d_json(), n2d_path)


def _ffdec_export_fla(swf_path: str, xfl_dir: str) -> str:
    from toolchain_home import ffdec_jar, java_exe

    java = java_exe()
    jar = ffdec_jar()
    if not java or not jar:
        log.info("[fla] ffdec=missing")
        return "missing"
    out = os.path.join(xfl_dir, "_ffdec")
    os.makedirs(out, exist_ok=True)
    cmd = [
        java, "-Djava.awt.headless=true", "-jar", jar,
        "-config", "export.fla.version=CS6",
        "-export", "fla", out, swf_path,
    ]
    log.info("[fla] ffdec_cmd export fla")
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        cmd = [java, "-Djava.awt.headless=true", "-jar", jar, "-export", "fla", out, swf_path]
        completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        err = (completed.stderr or completed.stdout or "").strip()
        print(err or "FFDec export failed", flush=True)
        log.info("[fla] ffdec=fail code=%s", completed.returncode)
        return "fail"
    if not _absorb_ffdec_output(out, xfl_dir):
        log.info("[fla] ffdec=empty")
        return "empty"
    log.info("[fla] ffdec=ok")
    return "ok"


def _absorb_ffdec_output(out_dir: str, xfl_dir: str) -> bool:
    dom = _find_named(out_dir, "DOMDocument.xml")
    if dom:
        root = os.path.dirname(dom)
        _copy_tree_into(root, xfl_dir)
        return True
    for dirpath, _dirs, files in os.walk(out_dir):
        for filename in files:
            if filename.lower().endswith(".fla"):
                _extract_zip(os.path.join(dirpath, filename), xfl_dir)
                return os.path.isfile(os.path.join(xfl_dir, "DOMDocument.xml"))
    return False


def _materialize_fla(fla_path: str) -> str:
    work = os.path.join(_cache_root(), _work_name(fla_path))
    stamp = _read_stamp(work)
    current = str(os.path.getmtime(fla_path))
    if stamp != current or not os.path.isfile(os.path.join(work, "project.n2d")):
        if os.path.isdir(work):
            shutil.rmtree(work)
        os.makedirs(work, exist_ok=True)
        _extract_zip(fla_path, work)
        _write_stamp(work, fla_path)
    return _ensure_cache(work, kind="fla", source=fla_path)


def _materialize_n2d_file(n2d_path: str) -> str:
    work = os.path.join(_cache_root(), _work_name(n2d_path))
    os.makedirs(work, exist_ok=True)
    target = os.path.join(work, "project.n2d")
    if not os.path.isfile(target) or os.path.getmtime(n2d_path) > os.path.getmtime(target):
        shutil.copyfile(n2d_path, target)
    _write_source(work, kind="n2d", source=n2d_path)
    return work


def _ensure_cache(work: str, kind: str, source: str) -> str:
    n2d_path = os.path.join(work, "project.n2d")
    cache = os.path.join(work, CACHE_REL)
    dom = os.path.join(work, "DOMDocument.xml")
    marker = os.path.join(work, PARSE_MARKER)
    parsed = ""
    if os.path.isfile(marker):
        with open(marker, "r", encoding="utf-8") as handle:
            parsed = handle.read().strip()
    if os.path.isfile(cache) and not os.path.isfile(n2d_path):
        os.makedirs(work, exist_ok=True)
        shutil.copyfile(cache, n2d_path)
        _write_parse_marker(work)
    elif os.path.isfile(dom) and parsed != PARSE_VERSION:
        import swf_to_n2d as mod
        mod.save_n2d(xfl_to_n2d(work, source_file=source), n2d_path)
        _write_parse_marker(work)
    elif not os.path.isfile(n2d_path) and os.path.isfile(dom):
        import swf_to_n2d as mod
        mod.save_n2d(xfl_to_n2d(work, source_file=source), n2d_path)
        _write_parse_marker(work)
    _write_source(work, kind=kind, source=source)
    log.info("[fla] open kind=%s work=%s", kind, work)
    return work


def _update_dom_stage(work_dir: str, n2d_path: str) -> None:
    data = _read_n2d(n2d_path)
    stage = data.get("stage") or {}
    dom = os.path.join(work_dir, "DOMDocument.xml")
    if not os.path.isfile(dom):
        _write_dom(dom, stage)
        return
    tree = ET.parse(dom)
    root = tree.getroot()
    if stage.get("width"):
        root.set("width", str(int(stage["width"])))
    if stage.get("height"):
        root.set("height", str(int(stage["height"])))
    if stage.get("fps"):
        root.set("frameRate", str(stage["fps"]))
    if stage.get("bgColor"):
        root.set("backgroundColor", str(stage["bgColor"]))
    tree.write(dom, encoding="utf-8", xml_declaration=True)


def _write_dom(path: str, stage: dict) -> None:
    width = int(stage.get("width") or 550)
    height = int(stage.get("height") or 400)
    fps = stage.get("fps") or 24
    bg = stage.get("bgColor") or "#333333"
    root = ET.Element(f"{{{XFL_NS}}}DOMDocument", {
        "width": str(width),
        "height": str(height),
        "frameRate": str(fps),
        "backgroundColor": str(bg),
        "currentTimeline": "1",
        "xflVersion": "2.1",
    })
    ET.SubElement(root, f"{{{XFL_NS}}}timelines")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def _tag(node) -> str:
    return node.tag.split("}")[-1]


def _linkage(node) -> str:
    if node.attrib.get("linkageExportForAS") == "false":
        return ""
    return node.attrib.get("linkageClassName") or ""


def _index_files(xfl_dir: str) -> dict:
    index = {"_base": {}}
    for dirpath, _dirs, files in os.walk(xfl_dir):
        for filename in files:
            full = os.path.join(dirpath, filename)
            rel = os.path.relpath(full, xfl_dir).replace("\\", "/")
            index[rel] = full
            index["_base"].setdefault(filename, []).append(full)
    return index


def _lookup(index: dict, *keys):
    for key in keys:
        if not key:
            continue
        norm = key.replace("\\", "/").lstrip("/")
        if norm in index:
            return index[norm]
        hits = index.get("_base", {}).get(os.path.basename(norm), [])
        images = [hit for hit in hits if not hit.lower().endswith(".dat")]
        if len(images) == 1:
            return images[0]
        if len(hits) == 1:
            return hits[0]
    return None


def _write_parse_marker(work: str) -> None:
    with open(os.path.join(work, PARSE_MARKER), "w", encoding="utf-8") as handle:
        handle.write(PARSE_VERSION)


def _read_classpath_scripts(root, source_file: str, existing: list) -> list:
    raw = root.attrib.get("as3SourcePath") or ""
    if not raw:
        return []
    base = source_file
    if not os.path.isdir(base):
        base = os.path.dirname(base)
    seen = {item.get("path") for item in existing}
    scripts = []
    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        folder = os.path.abspath(os.path.normpath(os.path.join(base, part)))
        if not os.path.isdir(folder):
            log.info("[fla] classpath missing %s", folder)
            continue
        for dirpath, dirs, files in os.walk(folder):
            dirs[:] = [name for name in dirs if name not in {".git", "bin"}]
            for filename in files:
                if not filename.lower().endswith(".as"):
                    continue
                full = os.path.join(dirpath, filename)
                rel = os.path.relpath(full, base).replace("\\", "/")
                if rel in seen:
                    continue
                seen.add(rel)
                with open(full, "r", encoding="utf-8", errors="replace") as handle:
                    source = handle.read()
                scripts.append({"name": filename, "path": rel, "source": source})
    log.info("[fla] classpath scripts=%d root=%s", len(scripts), base)
    return scripts


def _direct_named(node, wrapper: str, child: str):
    boxes = [item for item in list(node) if _tag(item) == wrapper]
    if boxes:
        return [item for box in boxes for item in list(box) if _tag(item) == child]
    return [item for item in list(node) if _tag(item) == child]


def _frame_script(frame) -> str:
    chunks = []
    for node in _walk(frame, "script"):
        text = "".join(node.itertext()).strip()
        if text:
            chunks.append(text)
    return "\n".join(chunks)


def _placement(place_id, inst, lib_id, start, end, matrix=None) -> dict:
    return {
        "id": place_id,
        "name": inst.attrib.get("name") or "",
        "libraryId": lib_id,
        "startFrame": start,
        "endFrame": end,
        "tween": [],
        "places": [{
            "frame": start,
            "depth": 0,
            "blendMode": "normal",
            "filter": [],
            "matrix": matrix if matrix is not None else _direct_matrix(inst),
            "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
        }],
    }


def _reverse_contours(cmds: list) -> list:
    """Turn a fillStyle0 contour around so the fill sits on the right."""
    contours = []
    current = []
    for cmd in cmds:
        if cmd[0] == "M" and current:
            contours.append(current)
            current = [cmd]
        else:
            current.append(cmd)
    if current:
        contours.append(current)
    reversed_cmds = []
    for contour in contours:
        cursor = None
        segments = []
        for cmd in contour:
            if cmd[0] == "M":
                cursor = (cmd[1], cmd[2])
            elif cmd[0] == "L" and cursor is not None:
                segments.append(("L", cursor, (cmd[1], cmd[2])))
                cursor = (cmd[1], cmd[2])
            elif cmd[0] == "Q" and cursor is not None:
                segments.append(("Q", cursor, (cmd[1], cmd[2]), (cmd[3], cmd[4])))
                cursor = (cmd[3], cmd[4])
        if not segments:
            reversed_cmds.extend(contour)
            continue
        end = segments[-1][-1]
        reversed_cmds.append(("M", end[0], end[1]))
        for seg in reversed(segments):
            if seg[0] == "L":
                reversed_cmds.append(("L", seg[1][0], seg[1][1]))
            else:
                control = seg[2]
                start = seg[1]
                reversed_cmds.append(("Q", control[0], control[1], start[0], start[1]))
    return reversed_cmds


def _text_item(node) -> dict:
    characters = []
    face = "Arial"
    size = 12
    color = "#000000"
    align = "left"
    for run in _walk(node, "DOMTextRun"):
        for child in list(run):
            if _tag(child) == "characters" and child.text:
                characters.append(child.text)
    for attrs in _walk(node, "DOMTextAttrs"):
        face = attrs.attrib.get("face") or face
        size = float(attrs.attrib.get("size") or size)
        color = attrs.attrib.get("fillColor") or color
        align = attrs.attrib.get("alignment") or align
        break
    kind = _tag(node)
    if kind == "DOMInputText":
        input_type = "input"
    elif kind == "DOMDynamicText":
        input_type = "dynamic"
    else:
        input_type = "static"
    width = float(node.attrib.get("width") or 100)
    height = float(node.attrib.get("height") or 20)
    rgb = _hex_rgb(color)
    return {
        "text": "".join(characters),
        "font": face,
        "size": size,
        "color": (rgb[0] << 16) | (rgb[1] << 8) | rgb[2],
        "align": align,
        "inputType": input_type,
        "html": node.attrib.get("renderAsHTML") == "true",
        "bounds": {"xMin": 0, "yMin": 0, "xMax": width, "yMax": height},
    }


def _shape_recodes(shape) -> tuple:
    from swf_constants import (
        CMD_BEGIN_PATH, CMD_MOVE_TO, CMD_LINE_TO, CMD_CURVE_TO,
        CMD_STROKE_STYLE, CMD_FILL_STYLE, CMD_END_STROKE, CMD_END_FILL,
    )
    strokes = {}
    for style in _walk(shape, "SolidStroke"):
        parent = None
        for node in _walk(shape, "StrokeStyle"):
            if style in list(node.iter()):
                parent = node
                break
        index = int((parent.attrib.get("index") if parent is not None else "1") or 1)
        color = "#000000"
        for solid in _walk(style, "SolidColor"):
            color = solid.attrib.get("color") or color
            break
        strokes[index] = (float(style.attrib.get("weight") or 1), _hex_rgb(color))
    fills = {}
    for style in _walk(shape, "FillStyle"):
        index = int(style.attrib.get("index") or 1)
        for solid in _walk(style, "SolidColor"):
            fills[index] = _hex_rgb(solid.attrib.get("color") or "#000000")
            break
    recodes = []
    xs = []
    ys = []
    for edge in _walk(shape, "Edge"):
        stroke_i = int(edge.attrib.get("strokeStyle") or 0)
        fill0 = int(edge.attrib.get("fillStyle0") or 0)
        fill1 = int(edge.attrib.get("fillStyle1") or 0)
        fill_i = fill1 or fill0
        cmds = _parse_edges(edge.attrib.get("edges") or "")
        if fill0 and not fill1:
            cmds = _reverse_contours(cmds)
        if not cmds:
            continue
        if stroke_i and stroke_i in strokes:
            weight, rgb = strokes[stroke_i]
            recodes.extend([
                CMD_STROKE_STYLE, weight, "none", "round", 3,
                rgb[0], rgb[1], rgb[2], 255,
            ])
        if fill_i and fill_i in fills:
            rgb = fills[fill_i]
            recodes.extend([CMD_FILL_STYLE, rgb[0], rgb[1], rgb[2], 255])
        recodes.append(CMD_BEGIN_PATH)
        for kind, *pts in cmds:
            xs.extend(pts[0::2])
            ys.extend(pts[1::2])
            if kind == "M":
                recodes.extend([CMD_MOVE_TO, pts[0], pts[1]])
            elif kind == "L":
                recodes.extend([CMD_LINE_TO, pts[0], pts[1]])
            elif kind == "Q":
                recodes.extend([CMD_CURVE_TO, pts[0], pts[1], pts[2], pts[3]])
        if stroke_i:
            recodes.append(CMD_END_STROKE)
        if fill_i:
            recodes.append(CMD_END_FILL)
    if xs and ys:
        bounds = {"xMin": min(xs), "yMin": min(ys), "xMax": max(xs), "yMax": max(ys)}
    else:
        bounds = {"xMin": 0, "yMin": 0, "xMax": 1, "yMax": 1}
    return recodes, bounds


def _parse_edges(text: str) -> list:
    import re
    tokens = re.findall(r"[!|\[\]]|-?\d+(?:\.\d+)?", text)
    scale = 20.0 if "!" in text else 1.0
    cmds = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in {"!", "|"} and i + 2 < len(tokens) and tokens[i + 1] not in {"!", "|", "[", "]"}:
            kind = "M" if token == "!" else "L"
            cmds.append((kind, float(tokens[i + 1]) / scale, float(tokens[i + 2]) / scale))
            i += 3
        elif token == "[" and i + 4 < len(tokens):
            nums = []
            j = i + 1
            while j < len(tokens) and tokens[j] not in {"!", "|", "[", "]"} and len(nums) < 4:
                nums.append(float(tokens[j]) / scale)
                j += 1
            if len(nums) == 4:
                cmds.append(("Q", nums[0], nums[1], nums[2], nums[3]))
            i = j
        else:
            i += 1
    return cmds


def _hex_rgb(color: str) -> tuple:
    color = color.lstrip("#")
    if len(color) < 6:
        return (0, 0, 0)
    return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))


def _layers_from_timeline(node, names: dict, place_id_next, add_shape, add_text) -> tuple:
    timeline = None
    for item in _walk(node, "DOMTimeline"):
        timeline = item
        break
    if timeline is None:
        return [], 1, [], []
    layers = []
    actions = []
    labels = []
    max_frame = 1
    shape_n = 0
    for layer_node in _direct_named(timeline, "layers", "DOMLayer"):
        characters = []
        for frame in _direct_named(layer_node, "frames", "DOMFrame"):
            index = int(frame.attrib.get("index", "0") or 0)
            duration = int(frame.attrib.get("duration", "1") or 1)
            start = index + 1
            # endFrame is exclusive. A one-frame span is startFrame=1, endFrame=2.
            end = start + max(duration, 1)
            max_frame = max(max_frame, end - 1)
            label = frame.attrib.get("name") or ""
            if label:
                labels.append({"frame": start, "name": label})
            script = _frame_script(frame)
            if script:
                actions.append({"frame": start, "action": script})
            def visit(element, inherited):
                nonlocal shape_n
                tag = _tag(element)
                here = _compose_matrix(inherited, _direct_matrix(element))
                if tag in {"DOMSymbolInstance", "DOMBitmapInstance"}:
                    lib_name = element.attrib.get("libraryItemName") or ""
                    lib_id = names.get(lib_name)
                    if lib_id is not None:
                        characters.append(_placement(place_id_next(), element, lib_id, start, end, here))
                    return
                if tag == "DOMShape":
                    shape_n += 1
                    recodes, bounds = _shape_recodes(element)
                    lib_id = add_shape(f"Shape {shape_n}", recodes, bounds)
                    characters.append(_placement(place_id_next(), element, lib_id, start, end, here))
                    return
                if tag in {"DOMStaticText", "DOMDynamicText", "DOMInputText"}:
                    fields = _text_item(element)
                    label = fields["text"] or "Text"
                    lib_id = add_text(label[:40], fields)
                    characters.append(_placement(place_id_next(), element, lib_id, start, end, here))
                    return
                child_matrix = here if tag == "DOMGroup" else inherited
                for child in list(element):
                    visit(child, child_matrix)

            visit(frame, [1, 0, 0, 1, 0, 0])
        layer_name = layer_node.attrib.get("name") or f"Layer {len(layers) + 1}"
        layers.append({
            "name": layer_name,
            "swfDepth": len(layers) + 1,
            "light": False,
            "disable": False,
            "lock": layer_node.attrib.get("locked") == "true",
            "mode": 0,
            "maskId": None,
            "guideId": None,
            "color": layer_node.attrib.get("color") or "#6ea8fe",
            "characters": characters,
            "emptyCharacters": [],
        })
    if not layers:
        layers = [_empty_layer("Layer 1")]
    return layers, max_frame, actions, labels


def _empty_layer(name: str) -> dict:
    return {
        "name": name,
        "swfDepth": 1,
        "light": False,
        "disable": False,
        "lock": False,
        "mode": 0,
        "maskId": None,
        "guideId": None,
        "color": "#6ea8fe",
        "characters": [],
        "emptyCharacters": [],
    }


def _direct_matrix(node) -> list:
    """The element's own transform. A fill or gradient matrix is not this."""
    values = {"a": 1.0, "b": 0.0, "c": 0.0, "d": 1.0, "tx": 0.0, "ty": 0.0}
    for child in list(node):
        if _tag(child) != "matrix":
            continue
        for item in list(child):
            if _tag(item) != "Matrix":
                continue
            for key in values:
                if key in item.attrib:
                    values[key] = float(item.attrib[key])
            return [values["a"], values["b"], values["c"], values["d"], values["tx"], values["ty"]]
    return [1, 0, 0, 1, 0, 0]


def _compose_matrix(parent, child) -> list:
    a = parent[0] * child[0] + parent[2] * child[1]
    b = parent[1] * child[0] + parent[3] * child[1]
    c = parent[0] * child[2] + parent[2] * child[3]
    d = parent[1] * child[2] + parent[3] * child[3]
    tx = parent[0] * child[4] + parent[2] * child[5] + parent[4]
    ty = parent[1] * child[4] + parent[3] * child[5] + parent[5]
    return [a, b, c, d, tx, ty]


def _matrix(inst) -> list:
    return _direct_matrix(inst)


def _read_scripts(xfl_dir: str) -> list:
    scripts = []
    for dirpath, dirs, files in os.walk(xfl_dir):
        dirs[:] = [name for name in dirs if name not in {"bin", ".git"}]
        for filename in files:
            if not filename.lower().endswith(".as"):
                continue
            full = os.path.join(dirpath, filename)
            rel = os.path.relpath(full, xfl_dir).replace("\\", "/")
            with open(full, "r", encoding="utf-8", errors="replace") as handle:
                source = handle.read()
            scripts.append({"name": filename, "path": rel, "source": source})
    return scripts


def _load_bitmap(path: str | None) -> tuple[int, int, str]:
    if not path or not os.path.isfile(path):
        return 0, 0, ""
    try:
        from PIL import Image
        import base64
        image = Image.open(path).convert("RGBA")
        raw = image.tobytes()
        return image.width, image.height, "b64:" + base64.b64encode(raw).decode("ascii")
    except Exception as exc:
        log.info("[fla] bitmap skip %s (%s)", path, exc)
        return 0, 0, ""


def _find_media(xfl_dir: str, href: str, item_name: str) -> str | None:
    candidates = []
    if href:
        href = href.replace("\\", "/").split("?")[0]
        candidates.append(os.path.join(xfl_dir, href.replace("/", os.sep)))
        candidates.append(os.path.join(xfl_dir, "LIBRARY", os.path.basename(href)))
        candidates.append(os.path.join(xfl_dir, "bin", os.path.basename(href)))
    if item_name:
        for folder in (xfl_dir, os.path.join(xfl_dir, "LIBRARY"), os.path.join(xfl_dir, "bin")):
            for ext in (".png", ".jpg", ".jpeg", ".gif", ".xml"):
                candidates.append(os.path.join(folder, item_name + ext))
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    if href:
        found = _find_named(xfl_dir, os.path.basename(href))
        if found:
            return found
    return None


def _find_named(root: str, filename: str) -> str | None:
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if name == filename:
                return os.path.join(dirpath, name)
    return None


def _read_n2d(path: str) -> dict:
    import msgpack
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        if "project.msgpack" in names:
            return msgpack.unpackb(zf.read("project.msgpack"), raw=False)
        return json.loads(zf.read("project.json"))


def _zip_xfl(src_dir: str, fla_path: str) -> None:
    skip_names = {"project.n2d", SOURCE_NAME, STAMP_NAME, PARSE_MARKER}
    skip_dirs = {"bitmaps", "sounds", "__pycache__"}
    os.makedirs(os.path.dirname(fla_path) or ".", exist_ok=True)
    tmp = fla_path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirs, files in os.walk(src_dir):
            dirs[:] = [name for name in dirs if name not in skip_dirs]
            for filename in files:
                if filename in skip_names:
                    continue
                full = os.path.join(dirpath, filename)
                rel = os.path.relpath(full, src_dir).replace("\\", "/")
                zf.write(full, rel)
    os.replace(tmp, fla_path)


def _extract_zip(zip_path: str, dest: str) -> None:
    os.makedirs(dest, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            rel = info.filename.replace("\\", "/")
            if rel.startswith("/") or ".." in rel.split("/"):
                continue
            target = os.path.join(dest, rel.replace("/", os.sep))
            if info.is_dir() or rel.endswith("/"):
                os.makedirs(target, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with zf.open(info) as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)


def _copy_tree_into(src: str, dest: str) -> None:
    for dirpath, _dirs, files in os.walk(src):
        for filename in files:
            full = os.path.join(dirpath, filename)
            rel = os.path.relpath(full, src)
            target = os.path.join(dest, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copyfile(full, target)


def _cache_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(here) if os.path.basename(here) == "lib" else here
    root = os.path.join(app_dir, "converted", "_fla")
    os.makedirs(root, exist_ok=True)
    return root


def _work_name(path: str) -> str:
    stem = os.path.splitext(os.path.basename(path))[0]
    digest = hashlib.sha1(os.path.abspath(path).encode("utf-8")).hexdigest()[:8]
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in stem) or "project"
    return f"{safe}-{digest}"


def _write_source(work: str, kind: str, source: str) -> None:
    os.makedirs(work, exist_ok=True)
    payload = {"kind": kind, "source": os.path.abspath(source)}
    with open(os.path.join(work, SOURCE_NAME), "w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def _read_source(work: str) -> dict | None:
    path = os.path.join(work, SOURCE_NAME)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_stamp(work: str, fla_path: str) -> None:
    with open(os.path.join(work, STAMP_NAME), "w", encoding="utf-8") as handle:
        handle.write(str(os.path.getmtime(fla_path)))


def _read_stamp(work: str) -> str:
    path = os.path.join(work, STAMP_NAME)
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read().strip()


def _walk(node, name: str):
    for item in node.iter():
        if item.tag.split("}")[-1] == name:
            yield item

