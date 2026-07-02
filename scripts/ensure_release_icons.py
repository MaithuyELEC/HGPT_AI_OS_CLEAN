from __future__ import annotations

import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ICNS = ASSETS / "LUCID.icns"
ICO = ASSETS / "LUCID.ico"


def _copy_pyinstaller_icns() -> bool:
    for path in sys.path:
        candidate = (
            Path(path)
            / "PyInstaller"
            / "bootloader"
            / "images"
            / "icon-windowed.icns"
        )
        if candidate.exists():
            ICNS.write_bytes(candidate.read_bytes())
            return True
    return False


def _write_ico() -> None:
    size = 32
    pixels = bytearray()
    for y in range(size):
        for x in range(size):
            border = x in (0, size - 1) or y in (0, size - 1)
            diagonal = x == y or x == size - y - 1
            if border or diagonal:
                pixels += bytes((255, 255, 255, 255))
            else:
                pixels += bytes((27, 38, 59, 255))

    xor = bytes(pixels)
    and_mask = b"\x00" * (size * size // 8)
    bitmap_header = struct.pack(
        "<IIIHHIIIIII",
        40,
        size,
        size * 2,
        1,
        32,
        0,
        len(xor) + len(and_mask),
        0,
        0,
        0,
        0,
    )
    image = bitmap_header + xor + and_mask
    header = struct.pack("<HHH", 0, 1, 1)
    directory = struct.pack(
        "<BBBBHHII",
        size,
        size,
        0,
        0,
        1,
        32,
        len(image),
        len(header) + 16,
    )
    ICO.write_bytes(header + directory + image)


def main() -> int:
    ASSETS.mkdir(exist_ok=True)
    if not ICNS.exists():
        _copy_pyinstaller_icns()
    if not ICO.exists():
        _write_ico()
    if not ICNS.exists():
        print("WARNING: assets/LUCID.icns not found; macOS build will use PyInstaller default.")
    if not ICO.exists():
        print("WARNING: assets/LUCID.ico not found; Windows build will use PyInstaller default.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
