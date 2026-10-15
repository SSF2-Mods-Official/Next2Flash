"""Opened SWFs are patched through n2f patch. Untouched characters stay."""

import base64
import struct
import subprocess
import sys
import zlib
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

from swf_binary_io import BitWriter
from swf_constants import (
    TAG_DEFINE_BITS_LOSSLESS2,
    TAG_DEFINE_EDIT_TEXT,
    TAG_DEFINE_SHAPE,
    TAG_DEFINE_SOUND,
    TAG_DO_ACTION,
    TAG_END,
    TAG_SET_BACKGROUND_COLOR,
    TAG_SHOW_FRAME,
)
from swf_to_n2d import parse_swf
from swf_writer import build_swf_file, build_place_object2, build_tag, write_matrix, write_rect

N2F = [sys.executable, str(APP / "n2f.py")]

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="
)


def _run(args):
    proc = subprocess.run(
        N2F + args,
        cwd=str(APP),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return proc.stdout


def _shape_records():
    bw = BitWriter()
    bw.write_ub(1, 0)
    bw.write_ub(1, 0)
    bw.write_ub(1, 0)
    bw.write_ub(1, 1)
    bw.write_ub(1, 0)
    bw.write_ub(1, 1)
    bw.write_ub(5, 5)
    bw.write_sb(5, 0)
    bw.write_sb(5, 0)
    bw.write_ub(1, 1)
    for dx, dy in ((20, 0), (0, 20), (-20, 0), (0, -20)):
        bw.write_ub(1, 1)
        bw.write_ub(1, 1)
        bw.write_ub(4, 4)
        bw.write_ub(1, 1)
        bw.write_sb(6, dx)
        bw.write_sb(6, dy)
    for _ in range(6):
        bw.write_ub(1, 0)
    return bw.get_bytes()


def _lossless(char_id, red, green, blue):
    pixels = bytes([255, red, green, blue])
    body = struct.pack("<H", char_id) + bytes([5]) + struct.pack("<HH", 1, 1)
    body += zlib.compress(pixels)
    return build_tag(TAG_DEFINE_BITS_LOSSLESS2, body)


def _shape():
    body = struct.pack("<H", 1) + write_rect(0, 20, 0, 20)
    body += bytes([1, 0x00, 255, 0, 0, 0, 0x10]) + _shape_records()
    return build_tag(TAG_DEFINE_SHAPE, body)


def _sound():
    body = struct.pack("<H", 3) + bytes([0x36]) + struct.pack("<I", 1) + b"\x00\x00"
    return build_tag(TAG_DEFINE_SOUND, body)


def _text():
    body = struct.pack("<H", 4) + write_rect(0, 2000, 0, 400)
    body += bytes([0x80, 0x00]) + b"\x00" + b"Hi\x00"
    return build_tag(TAG_DEFINE_EDIT_TEXT, body)


def _wav():
    data = b"\xff\x7f" * 8
    fmt = struct.pack("<IHHIIHH", 16, 1, 1, 11025, 22050, 2, 16)
    chunk = b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVEfmt " + fmt
    return chunk + b"data" + struct.pack("<I", len(data)) + data


def _sample_swf(path: Path):
    place = build_place_object2(depth=1, character_id=2, matrix=write_matrix(tx=10, ty=10))
    tags = b"".join([
        build_tag(TAG_SET_BACKGROUND_COLOR, bytes([240, 240, 240])),
        _shape(),
        _lossless(2, 0, 0, 255),
        _lossless(99, 0, 255, 0),
        _sound(),
        _text(),
        build_tag(TAG_DO_ACTION, b"\x07\x00"),
        place,
        build_tag(TAG_SHOW_FRAME, b""),
        build_tag(TAG_END, b""),
    ])
    path.write_bytes(build_swf_file(64, 64, 12, 1, tags, version=9))


def _payload(data, char_id):
    _header, tags = parse_swf(data)
    found = []
    for tag in tags:
        if len(tag.data) >= 2 and struct.unpack_from("<H", tag.data, 0)[0] == char_id:
            found.append((tag.tag_type, tag.data))
    return found


def _assert_untouched(before, after):
    assert _payload(before, 99) == _payload(after, 99)


def test_patch_script_leaves_other_characters(tmp_path):
    swf = tmp_path / "opened.swf"
    _sample_swf(swf)
    exported = tmp_path / "scripts"
    _run(["ffdec", "--", "-export", "script", str(exported), str(swf)])
    files = list(exported.rglob("*.as"))
    assert files, "ffdec exported no script"
    original = files[0].read_text(encoding="utf-8")
    assert "stop" in original
    files[0].write_text(original.replace("stop", "play", 1), encoding="utf-8")
    output = tmp_path / "patched.swf"
    before = swf.read_bytes()
    text = _run(["patch", str(swf), "--scripts", str(exported), "-o", str(output)])
    assert "kind=script" in text
    after = output.read_bytes()
    _assert_untouched(before, after)
    actions = [tag.data for _header, tags in [parse_swf(after)] for tag in tags if tag.tag_type == TAG_DO_ACTION]
    assert actions and actions[0] != b"\x07\x00"


def test_patch_text_leaves_other_characters(tmp_path):
    swf = tmp_path / "opened.swf"
    _sample_swf(swf)
    texts = tmp_path / "textroot" / "texts"
    texts.mkdir(parents=True)
    (texts / "4.txt").write_text("Yo", encoding="utf-8")
    output = tmp_path / "patched.swf"
    before = swf.read_bytes()
    text = _run(["patch", str(swf), "--texts", str(texts.parent), "-o", str(output)])
    assert "kind=text" in text
    after = output.read_bytes()
    _assert_untouched(before, after)
    assert _payload(before, 4) != _payload(after, 4)


def test_patch_image_leaves_other_characters(tmp_path):
    swf = tmp_path / "opened.swf"
    _sample_swf(swf)
    images = tmp_path / "images"
    images.mkdir()
    (images / "2.png").write_bytes(PNG)
    output = tmp_path / "patched.swf"
    before = swf.read_bytes()
    text = _run(["patch", str(swf), "--images", str(images), "-o", str(output)])
    assert "kind=image" in text
    after = output.read_bytes()
    _assert_untouched(before, after)
    assert _payload(before, 2) != _payload(after, 2)


def test_patch_sound_leaves_other_characters(tmp_path):
    swf = tmp_path / "opened.swf"
    _sample_swf(swf)
    sounds = tmp_path / "sounds"
    sounds.mkdir()
    (sounds / "3.wav").write_bytes(_wav())
    output = tmp_path / "patched.swf"
    before = swf.read_bytes()
    text = _run(["patch", str(swf), "--sounds", str(sounds), "-o", str(output)])
    assert "kind=sound" in text
    after = output.read_bytes()
    _assert_untouched(before, after)
    assert _payload(before, 3) != _payload(after, 3)


def test_patch_shape_leaves_other_characters(tmp_path):
    swf = tmp_path / "opened.swf"
    _sample_swf(swf)
    shapes = tmp_path / "shapes"
    shapes.mkdir()
    (shapes / "1.png").write_bytes(PNG)
    output = tmp_path / "patched.swf"
    before = swf.read_bytes()
    text = _run(["patch", str(swf), "--shapes", str(shapes), "-o", str(output)])
    assert "kind=shape" in text
    after = output.read_bytes()
    _assert_untouched(before, after)
    assert _payload(before, 1) != _payload(after, 1)


def test_patch_place_leaves_other_characters(tmp_path):
    swf = tmp_path / "opened.swf"
    _sample_swf(swf)
    spec = tmp_path / "places.txt"
    spec.write_text("sprite 0\ntransform 1 1 40 15\n", encoding="utf-8")
    output = tmp_path / "patched.swf"
    before = swf.read_bytes()
    text = _run(["patch", str(swf), "--places", str(spec), "-o", str(output)])
    assert "kind=place" in text
    after = output.read_bytes()
    _assert_untouched(before, after)
    assert _payload(before, 1) == _payload(after, 1)
    _header, tags = parse_swf(after)
    from swf_constants import TAG_PLACE_OBJECT2
    from swf_to_n2d import parse_place_object2
    places = [tag.data for tag in tags if tag.tag_type == TAG_PLACE_OBJECT2]
    assert places
    parsed = parse_place_object2(places[0], 9)
    assert parsed["matrix"][4] == 40
    assert parsed["matrix"][5] == 15


def test_preview_frame_does_not_rewrite_swf(tmp_path):
    swf = tmp_path / "opened.swf"
    _sample_swf(swf)
    before = swf.read_bytes()
    png = tmp_path / "frame.png"
    text = _run(["patch", str(swf), "--frame", "1", "--png", str(png)])
    assert "sprite=0" in text and "frame=1" in text
    assert swf.read_bytes() == before
    assert png.read_bytes().startswith(b"\x89PNG")
