"""Extern SWCs are a zip plus a link report, and a second write leaves them."""

import io
import zipfile

import os

from swf_externs import compile_sources_to_swc, def_id, link_report_xml, swc_bytes, write_externs


def test_swc_lists_the_class_and_stores_the_swf():
    blob = swc_bytes(b"FWS-library", ["com.example.Foo"])
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        catalog = zf.read("catalog.xml").decode("utf-8")
        assert zf.read("library.swf") == b"FWS-library"
    assert 'def id="com.example:Foo"' in catalog
    assert def_id("ScrollBar_thumbIcon") == "ScrollBar_thumbIcon"


def test_link_report_names_the_swc():
    xml = link_report_xml([("engine1.swc", ["com.example.Foo"])])
    assert 'script name="engine1.swc(com.example:Foo)"' in xml
    assert '<def id="com.example:Foo"/>' in xml


def test_write_externs_stores_the_compiled_swc(tmp_path, monkeypatch):
    game = tmp_path / "game.swf"
    lib = tmp_path / "lib.swf"
    game.write_bytes(b"FWS-game")
    lib.write_bytes(b"FWS-runtime")

    def classes(path):
        if path.name == "lib.swf":
            return {"com.example.Foo"}, set(), [("frame1", ["com.example.Foo"])]
        if path.name == "game.swf":
            return set(), {"com.example.Foo"}, []
        return set(), set(), []

    monkeypatch.setattr("swf_externs._classes_in_swf", classes)
    monkeypatch.setattr("swf_externs.compiler_swc", lambda path: b"PK-compiled")
    assert write_externs(str(game), str(tmp_path)) == 1
    blob = (tmp_path / "externs" / "lib.swc").read_bytes()
    assert blob == b"PK-compiled"
    assert b"FWS-runtime" not in blob


def test_compc_builds_a_swc_from_sources(tmp_path):
    from toolchain_home import aflex_lite_dir

    sdk = aflex_lite_dir()
    if not sdk or not os.path.isfile(os.path.join(sdk, "lib", "compc.jar")):
        return
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "Hello.as").write_text(
        "package {\npublic class Hello {\npublic function Hello() {}\n}\n}\n",
        encoding="utf-8",
    )
    out = tmp_path / "hello.swc"
    assert compile_sources_to_swc(scripts, out) == 0
    with zipfile.ZipFile(out) as zf:
        catalog = zf.read("catalog.xml").decode("utf-8")
    assert "Hello" in catalog


def test_existing_link_report_is_left_alone(tmp_path):
    externs = tmp_path / "externs"
    externs.mkdir()
    (externs / "lib.swc").write_bytes(b"already")
    (externs / "link-report.xml").write_text("keep", encoding="utf-8")
    assert write_externs(str(tmp_path / "missing.swf"), str(tmp_path)) == 0
    assert (externs / "link-report.xml").read_text(encoding="utf-8") == "keep"
    assert (externs / "lib.swc").read_bytes() == b"already"
