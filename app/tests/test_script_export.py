"""Decompiled scripts are rewritten so mxmlc can compile them."""

import os
import shutil
import subprocess
import sys

from script_export import (
    fix_dictionary_clash,
    fix_embed_swf_alias_names,
    fix_flash_utils_star,
    fix_or_assign,
    hold_externs,
    prepare_compiler_sources,
    restore_externs,
)

N2F = [sys.executable, os.path.join(os.path.dirname(os.path.dirname(__file__)), "n2f.py")]


def test_or_assign_becomes_valid_as3():
    text, count = fix_or_assign("    lives ||= 1\n")
    assert count == 1
    assert "lives = lives ||" in text
    assert "||=" not in text


def test_flash_utils_star_becomes_explicit_imports():
    source = "package {\nimport flash.utils.*;\nvar n:int = getTimer();\n}\n"
    text, count = fix_flash_utils_star(source)
    assert count == 1
    assert "import flash.utils.*;" not in text
    assert "import flash.utils.getTimer;" in text


def test_flash_utils_star_qualifies_dictionary_next_to_a_custom_util_dictionary():
    source = (
        "package game.menus {\n"
        "import flash.utils.*;\n"
        "import com.example.util.Dictionary;\n"
        "var d:* = new Dictionary(true);\n"
        "}\n"
    )
    text, count = fix_flash_utils_star(source)
    assert count == 1
    assert "new flash.utils.Dictionary(true)" in text


def test_embed_with_swf_alias_extension_points_at_swf():
    text, count = fix_embed_swf_alias_names('[Embed(source="assets/menu.ssf", mimeType="application/octet-stream")]')
    assert count == 1
    assert 'source="assets/menu.swf"' in text


def test_dictionary_import_does_not_clash_with_a_star_import():
    source = (
        "package {\n"
        "   import com.example.util.*;\n"
        "   import flash.utils.Dictionary;\n"
        "   var memory:com.example.util.Dictionary = new Dictionary(String);\n"
        "}\n"
    )
    text, count = fix_dictionary_clash(source)
    assert count == 1
    assert "import flash.utils.Dictionary;" not in text
    assert "new Dictionary(String)" in text


def test_compiler_sources_drop_embeds_and_import_dictionary(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    skin = scripts / "Skin.as"
    skin.write_text(
        'package {\n   [Embed(source="/_assets/assets.swf", symbol="symbol1")]\n'
        "   public class Skin {}\n}\n",
        encoding="utf-8",
    )
    mgr = scripts / "Mgr.as"
    mgr.write_text(
        "package {\n   public class Mgr {\n      private var items:Dictionary;\n   }\n}\n",
        encoding="utf-8",
    )
    assert prepare_compiler_sources(scripts) == 2
    assert "[Embed(" not in skin.read_text(encoding="utf-8")
    assert "import flash.utils.Dictionary;" in mgr.read_text(encoding="utf-8")


def test_externs_folder_survives_a_cleared_export(tmp_path):
    dest = tmp_path / "out"
    externs = dest / "externs"
    externs.mkdir(parents=True)
    (externs / "engine1.swc").write_bytes(b"compiler-swc")
    (externs / "link-report.xml").write_text("keep", encoding="utf-8")
    held = hold_externs(dest)
    if dest.exists():
        for child in dest.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    restore_externs(dest, held)
    assert (externs / "engine1.swc").read_bytes() == b"compiler-swc"
    assert (externs / "link-report.xml").read_text(encoding="utf-8") == "keep"


def test_asconfig_starts(tmp_path):
    project = tmp_path / "asconfig.json"
    project.write_text("{}\n", encoding="utf-8")
    proc = subprocess.run(
        N2F + ["asconfig", "--project", str(project)],
        capture_output=True,
        text=True,
    )
    combined = proc.stdout + proc.stderr
    assert "NoClassDefFoundError" not in combined
    assert "JsonProcessingException" not in combined
