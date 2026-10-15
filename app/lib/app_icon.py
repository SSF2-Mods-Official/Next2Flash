"""Turn app/icon.png into the Windows exe icon."""

from __future__ import annotations

import ctypes
import struct
import sys
from ctypes import wintypes
from pathlib import Path

_ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)
_RT_ICON = 3
_RT_GROUP_ICON = 14
_LANG = 1033


def write_ico(png_path: str, ico_path: str) -> None:
    from PIL import Image

    image = Image.open(png_path).convert("RGBA")
    side = max(image.size)
    if image.size != (side, side):
        canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        canvas.paste(image, ((side - image.size[0]) // 2, (side - image.size[1]) // 2))
        image = canvas
    sizes = [(s, s) for s in _ICO_SIZES if s <= side]
    if not sizes:
        sizes = [(side, side)]
    Path(ico_path).parent.mkdir(parents=True, exist_ok=True)
    image.save(ico_path, format="ICO", sizes=sizes)


def _resource_id(value: int):
    return ctypes.cast(ctypes.c_void_p(value), wintypes.LPCWSTR)


def _ico_images(ico_path: str) -> list[tuple[bytes, bytes]]:
    data = Path(ico_path).read_bytes()
    _reserved, kind, count = struct.unpack_from("<HHH", data, 0)
    if kind != 1 or count < 1:
        raise ValueError(f"{ico_path} is not an icon file")
    images = []
    for index in range(count):
        entry = data[6 + index * 16: 6 + (index + 1) * 16]
        _width, _height, _colors, _reserved, _planes, _bits, size, offset = struct.unpack(
            "<BBBBHHII", entry
        )
        images.append((entry[:12], data[offset:offset + size]))
    return images


def set_windows_exe_icon(exe_path: str, ico_path: str) -> None:
    images = _ico_images(ico_path)
    group = bytearray(struct.pack("<HHH", 0, 1, len(images)))
    payloads = []
    for index, (header, blob) in enumerate(images, start=1):
        group.extend(header)
        group.extend(struct.pack("<H", index))
        payloads.append(blob)

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    begin = kernel32.BeginUpdateResourceW
    begin.argtypes = [wintypes.LPCWSTR, wintypes.BOOL]
    begin.restype = wintypes.HANDLE
    update = kernel32.UpdateResourceW
    update.argtypes = [
        wintypes.HANDLE,
        wintypes.LPCWSTR,
        wintypes.LPCWSTR,
        wintypes.WORD,
        wintypes.LPVOID,
        wintypes.DWORD,
    ]
    update.restype = wintypes.BOOL
    end = kernel32.EndUpdateResourceW
    end.argtypes = [wintypes.HANDLE, wintypes.BOOL]
    end.restype = wintypes.BOOL

    handle = begin(str(exe_path), False)
    if not handle:
        raise OSError(f"Could not open {exe_path} to set the icon")
    buffers = [ctypes.create_string_buffer(blob) for blob in payloads]
    buffers.append(ctypes.create_string_buffer(bytes(group)))
    try:
        for index, buf in enumerate(buffers[:-1], start=1):
            if not update(handle, _resource_id(_RT_ICON), _resource_id(index), _LANG, buf, len(buf) - 1):
                raise OSError(f"Could not write icon image {index}")
        group_buf = buffers[-1]
        if not update(
            handle,
            _resource_id(_RT_GROUP_ICON),
            _resource_id(1),
            _LANG,
            group_buf,
            len(group_buf) - 1,
        ):
            raise OSError("Could not write the icon group")
    except Exception:
        end(handle, True)
        raise
    if not end(handle, False):
        raise OSError(f"Could not save the icon into {exe_path}")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: app_icon.py icon.png out.ico [app.exe ...]", file=sys.stderr)
        return 1
    png, ico, *exes = argv
    write_ico(png, ico)
    for exe in exes:
        set_windows_exe_icon(exe, ico)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
