"""FLA and XFL open, save, and the editor cache inside the FLA."""

import base64
import os
import zipfile

import fla_xfl


PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def _write_xfl(folder):
    os.makedirs(os.path.join(folder, "LIBRARY"), exist_ok=True)
    os.makedirs(os.path.join(folder, "bin"), exist_ok=True)
    with open(os.path.join(folder, "bin", "dot.png"), "wb") as handle:
        handle.write(PNG)
    os.makedirs(os.path.join(folder, "scripts"), exist_ok=True)
    with open(os.path.join(folder, "scripts", "Hello.as"), "w", encoding="utf-8") as handle:
        handle.write("package { public class Hello {} }")
    with open(os.path.join(folder, "LIBRARY", "Clip.xml"), "w", encoding="utf-8") as handle:
        handle.write(
            '<?xml version="1.0"?>'
            '<DOMSymbolItem name="Clip" xmlns="http://ns.adobe.com/xfl/2008/">'
            "<timeline><DOMTimeline name=\"Clip\"><layers>"
            "<DOMLayer name=\"Layer 1\"><frames>"
            '<DOMFrame index="0" duration="1"/>'
            "</frames></DOMLayer></layers></DOMTimeline></timeline>"
            "</DOMSymbolItem>"
        )
    with open(os.path.join(folder, "DOMDocument.xml"), "w", encoding="utf-8") as handle:
        handle.write(
            '<?xml version="1.0"?>'
            '<DOMDocument xmlns="http://ns.adobe.com/xfl/2008/" width="320" height="240" '
            'frameRate="12" backgroundColor="#112233">'
            "<media><DOMBitmapItem name=\"Dot\" href=\"dot.png\" bitmapDataHRef=\"bin/dot.png\"/></media>"
            "<symbols><Include href=\"Clip.xml\"/></symbols>"
            "<timelines><DOMTimeline name=\"Scene 1\"><layers>"
            "<DOMLayer name=\"Dots\"><frames>"
            '<DOMFrame index="0" duration="4"><elements>'
            '<DOMSymbolInstance libraryItemName="Clip" name="hero">'
            "<matrix><Matrix a=\"1\" d=\"1\" tx=\"8\" ty=\"9\"/></matrix>"
            "</DOMSymbolInstance>"
            "</elements></DOMFrame>"
            "</frames></DOMLayer></layers></DOMTimeline></timelines>"
            "</DOMDocument>"
        )


def test_xfl_round_trip(tmp_path):
    xfl = tmp_path / "hero"
    _write_xfl(str(xfl))
    data = fla_xfl.xfl_to_n2d(str(xfl))
    assert data["stage"]["width"] == 320
    assert data["stage"]["height"] == 240
    assert data["stage"]["fps"] == 12
    names = {item["name"]: item for item in data["libraries"]}
    assert names["Dot"]["type"] == "bitmap"
    assert names["Dot"]["width"] == 1
    assert names["Clip"]["type"] == "container"
    assert any(item["path"].endswith("Hello.as") for item in data["scripts"])
    placed = names["main"]["layers"][0]["characters"][0]
    assert placed["libraryId"] == names["Clip"]["id"]
    assert placed["startFrame"] == 1
    assert placed["endFrame"] == 5
    assert placed["places"][0]["matrix"][4] == 8

    import swf_to_n2d as mod
    n2d_path = xfl / "project.n2d"
    mod.save_n2d(data, str(n2d_path))
    fla = tmp_path / "hero.fla"
    fla_xfl._zip_xfl(str(xfl), str(fla))
    # The cache the editor reads lives inside the FLA.
    os.makedirs(xfl / "bin", exist_ok=True)
    cache = xfl / "bin" / "next2flash.n2d"
    cache.write_bytes(n2d_path.read_bytes())
    fla_xfl._zip_xfl(str(xfl), str(fla))

    work = fla_xfl.materialize(str(fla))
    assert os.path.isfile(os.path.join(work, "project.n2d"))
    opened = fla_xfl._read_n2d(os.path.join(work, "project.n2d"))
    assert opened["stage"]["width"] == 320

    opened["stage"]["width"] = 400
    mod.save_n2d(opened, os.path.join(work, "project.n2d"))
    fla_xfl.sync_project(work)
    with zipfile.ZipFile(fla) as zf:
        assert "bin/next2flash.n2d" in zf.namelist()
        dom = zf.read("DOMDocument.xml").decode("utf-8")
    assert 'width="400"' in dom


def test_library_folders_and_bitmap_png(tmp_path):
    xfl = tmp_path / "proj"
    os.makedirs(xfl / "LIBRARY" / "Animations" / "A" / "Sprites", exist_ok=True)
    png = xfl / "LIBRARY" / "Animations" / "A" / "Sprites" / "a0.png"
    png.write_bytes(PNG)
    dat = xfl / "bin"
    os.makedirs(dat, exist_ok=True)
    (dat / "M 1 1.dat").write_bytes(b"not an image")
    (xfl / "DOMDocument.xml").write_text(
        '<?xml version="1.0"?>'
        '<DOMDocument xmlns="http://ns.adobe.com/xfl/2008/" width="100" height="80" frameRate="30.5">'
        '<media><DOMBitmapItem name="Animations/A/Sprites/a0.png" href="Animations/A/Sprites/a0.png" '
        'bitmapDataHRef="M 1 1.dat" linkageClassName="HowFast_a0" linkageExportForAS="true" '
        'compressionType="lossless" frameRight="20" frameBottom="20"/>'
        '<DOMBitmapItem name="photo.png" href="Animations/A/Sprites/a0.png" '
        'frameRight="20" frameBottom="20"/></media>'
        '<timelines><DOMTimeline name="Scene 1"><layers><DOMLayer name="Art"><frames>'
        '<DOMFrame index="0" duration="2"><elements>'
        '<DOMBitmapInstance libraryItemName="Animations/A/Sprites/a0.png"/>'
        '</elements></DOMFrame></frames></DOMLayer></layers></DOMTimeline></timelines>'
        '</DOMDocument>',
        encoding="utf-8",
    )
    data = fla_xfl.xfl_to_n2d(str(xfl))
    by_name = {}
    for item in data["libraries"]:
        by_name.setdefault(item["name"], []).append(item)
    folders = [item["name"] for item in data["libraries"] if item["type"] == "folder"]
    assert folders == ["Animations", "A", "Sprites"]
    bitmap = by_name["a0.png"][0]
    assert bitmap["type"] == "bitmap"
    assert bitmap["symbol"] == "HowFast_a0"
    assert bitmap["buffer"].startswith("b64:")
    assert bitmap["rawTagType"] == 36
    assert by_name["photo.png"][0]["rawTagType"] == 35
    assert bitmap["width"] == 1
    assert bitmap["folderId"] == by_name["Sprites"][0]["id"]
    placed = by_name["main"][0]["layers"][0]["characters"]
    assert placed[0]["libraryId"] == bitmap["id"]


def test_frame_script_and_classpath(tmp_path):
    fla_dir = tmp_path / "FLA"
    os.makedirs(fla_dir / "common", exist_ok=True)
    (fla_dir / "Main.as").write_text("package { public class Main {} }", encoding="utf-8")
    (fla_dir / "common" / "Helper.as").write_text("package { public class Helper {} }", encoding="utf-8")
    xfl = fla_dir / "unpacked"
    os.makedirs(xfl / "LIBRARY", exist_ok=True)
    (xfl / "LIBRARY" / "Clip.xml").write_text(
        '<?xml version="1.0"?>'
        '<DOMSymbolItem xmlns="http://ns.adobe.com/xfl/2008/" name="Animations/A/A" '
        'linkageClassName="HowFast" linkageExportForAS="true">'
        '<timeline><DOMTimeline name="A"><layers><DOMLayer name="Actions"><frames>'
        '<DOMFrame index="0" duration="3"><Actionscript><script><![CDATA[this.self = this;]]></script></Actionscript>'
        '<elements/></DOMFrame></frames></DOMLayer></layers></DOMTimeline></timeline>'
        '</DOMSymbolItem>',
        encoding="utf-8",
    )
    (xfl / "DOMDocument.xml").write_text(
        '<?xml version="1.0"?>'
        '<DOMDocument xmlns="http://ns.adobe.com/xfl/2008/" as3SourcePath=".;common" '
        'width="10" height="10" frameRate="30">'
        '<symbols><Include href="Clip.xml"/></symbols>'
        '<timelines><DOMTimeline name="Scene 1"><layers><DOMLayer name="L"><frames>'
        '<DOMFrame index="0"><elements>'
        '<DOMSymbolInstance libraryItemName="Animations/A/A"/>'
        '</elements></DOMFrame></frames></DOMLayer></layers></DOMTimeline></timelines>'
        '</DOMDocument>',
        encoding="utf-8",
    )
    data = fla_xfl.xfl_to_n2d(str(xfl), source_file=str(fla_dir / "HowFast.fla"))
    paths = {item["path"] for item in data["scripts"]}
    assert "Main.as" in paths
    assert "common/Helper.as" in paths
    clip = next(item for item in data["libraries"] if item["type"] == "container" and item["name"] == "A")
    assert clip["symbol"] == "HowFast"
    assert clip["folderId"] != 0
    assert clip["actions"][0]["action"] == "this.self = this;"
    assert clip["actions"][0]["frame"] == 1


def test_shape_edges():
    text = (
        '<DOMShape><strokes><StrokeStyle index="1"><SolidStroke weight="2">'
        '<fill><SolidColor color="#00ff00"/></fill></SolidStroke></StrokeStyle></strokes>'
        '<edges><Edge strokeStyle="1" edges="!20 40|60 40|60 80|20 80|20 40"/></edges></DOMShape>'
    )
    import xml.etree.ElementTree as ET
    shape = ET.fromstring(text)
    recodes, bounds = fla_xfl._shape_recodes(shape)
    assert recodes
    assert bounds["xMax"] == 3


def test_shape_matrix_ignores_fill_and_text_is_placed(tmp_path):
    xfl = tmp_path / "proj"
    (xfl / "LIBRARY").mkdir(parents=True)
    (xfl / "DOMDocument.xml").write_text(
        '<?xml version="1.0"?>'
        '<DOMDocument xmlns="http://ns.adobe.com/xfl/2008/" width="100" height="80" frameRate="12">'
        '<timelines><DOMTimeline name="Scene 1"><layers><DOMLayer name="Art"><frames>'
        '<DOMFrame index="0"><elements>'
        '<DOMGroup><matrix><Matrix tx="10" ty="0"/></matrix><members>'
        '<DOMShape>'
        '<matrix><Matrix tx="3" ty="4"/></matrix>'
        '<fills><FillStyle index="1"><SolidColor color="#ff0000"/>'
        '<matrix><Matrix a="20" d="20"/></matrix></FillStyle></fills>'
        '<edges><Edge fillStyle0="1" edges="!0 0|20 0|20 20|0 20|0 0"/></edges>'
        '</DOMShape>'
        '<DOMDynamicText name="title" width="40" height="12">'
        '<matrix><Matrix tx="1" ty="2"/></matrix>'
        '<textRuns><DOMTextRun><characters>Fire</characters>'
        '<textAttrs><DOMTextAttrs face="Arial" size="12" fillColor="#ffffff" alignment="left"/>'
        '</textAttrs></DOMTextRun></textRuns>'
        '</DOMDynamicText>'
        '</members></DOMGroup>'
        '</elements></DOMFrame></frames></DOMLayer></layers></DOMTimeline></timelines>'
        '</DOMDocument>',
        encoding="utf-8",
    )
    data = fla_xfl.xfl_to_n2d(str(xfl))
    by_type = {}
    for item in data["libraries"]:
        by_type.setdefault(item["type"], []).append(item)
    shape = by_type["shape"][0]
    assert shape["bounds"]["xMax"] == 1
    text = by_type["text"][0]
    assert text["text"] == "Fire"
    assert text["folderId"] == by_type["folder"][0]["id"]
    placed = by_type["container"][0]["layers"][0]["characters"]
    shape_place = next(item for item in placed if item["libraryId"] == shape["id"])
    text_place = next(item for item in placed if item["libraryId"] == text["id"])
    assert shape_place["places"][0]["matrix"][4] == 13
    assert text_place["places"][0]["matrix"][4] == 11
    from shape_converter import parse_next2d_shape_buffer
    _fills, _lines, paths = parse_next2d_shape_buffer(shape["recodes"])
    assert paths[0].edges[1].y == 1


def test_one_frame_span_publishes():
    from compile_n2d import to_publish
    container = {
        "id": 0,
        "layers": [{
            "disable": False,
            "mode": 0,
            "characters": [{
                "libraryId": 5,
                "name": "hero",
                "startFrame": 1,
                "endFrame": 2,
                "places": [{
                    "frame": 1,
                    "depth": 0,
                    "matrix": [1, 0, 0, 1, 0, 0],
                    "colorTransform": [1, 1, 1, 1, 0, 0, 0, 0],
                    "blendMode": "normal",
                    "filter": [],
                }],
            }],
        }],
    }
    published = to_publish(container, {5: 1})
    assert len(published["dictionary"]) == 1
    assert len(published["placeObjects"]) == 1


def test_swf_export_fla_keeps_cache(tmp_path):
    swf = tmp_path / "mini.swf"
    swf.write_bytes(bytes.fromhex(
        "465753091C0000007800055F00000FA000000C01004302FFFFFF40000000"
    ))
    fla = tmp_path / "mini.fla"
    assert fla_xfl.export_swf_to_fla(str(swf), str(fla)) == 0
    with zipfile.ZipFile(fla) as zf:
        assert "DOMDocument.xml" in zf.namelist()
        assert "bin/next2flash.n2d" in zf.namelist()
