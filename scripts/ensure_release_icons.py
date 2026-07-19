from __future__ import annotations

import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ICNS = ASSETS / "LUCID.icns"
ICO = ASSETS / "LUCID.ico"
PNG = ASSETS / "LUCID.png"
REQUIRED_SIZES = (16, 32, 48, 64, 128, 256, 512, 1024)
ICNS_CHUNKS = {
    16: b"icp4",
    32: b"icp5",
    48: b"ic48",
    64: b"icp6",
    128: b"ic07",
    256: b"ic08",
    512: b"ic09",
    1024: b"ic10",
}
ICNS_CHUNK_SIZES = {chunk: size for size, chunk in ICNS_CHUNKS.items()}


def _png_size(data: bytes) -> tuple[int, int]:
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("not a PNG image")
    return struct.unpack(">II", data[16:24])


def _resize_png(source: Path, target: Path, size: int) -> None:
    subprocess.run(
        ["sips", "-z", str(size), str(size), str(source), "--out", str(target)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _ico_image_count(path: Path) -> int:
    data = path.read_bytes()[:6]
    reserved, icon_type, count = struct.unpack("<HHH", data)
    if reserved != 0 or icon_type != 1:
        raise ValueError("not a Windows icon file")
    return count


def _ico_sizes(path: Path) -> set[int]:
    data = path.read_bytes()
    reserved, icon_type, count = struct.unpack("<HHH", data[:6])
    if reserved != 0 or icon_type != 1:
        raise ValueError("not a Windows icon file")

    sizes: set[int] = set()
    for index in range(count):
        offset = 6 + index * 16
        width, height, _colors, _reserved, _planes, _bit_count, size, image_offset = struct.unpack(
            "<BBBBHHII", data[offset : offset + 16]
        )
        image_data = data[image_offset : image_offset + size]
        png_width, png_height = _png_size(image_data)
        sizes.add(max(width or 256, height or 256, png_width, png_height))
    return sizes


def _write_ico(png_paths: dict[int, Path], target: Path) -> None:
    directory = bytearray()
    images = bytearray()
    image_offset = 6 + (16 * len(REQUIRED_SIZES))

    for size in REQUIRED_SIZES:
        image_data = png_paths[size].read_bytes()
        width_byte = 0 if size >= 256 else size
        directory.extend(
            struct.pack(
                "<BBBBHHII",
                width_byte,
                width_byte,
                0,
                0,
                1,
                32,
                len(image_data),
                image_offset,
            )
        )
        images.extend(image_data)
        image_offset += len(image_data)

    target.write_bytes(struct.pack("<HHH", 0, 1, len(REQUIRED_SIZES)) + directory + images)


def _write_icns(png_paths: dict[int, Path], target: Path) -> None:
    chunks = bytearray()
    for size in REQUIRED_SIZES:
        image_data = png_paths[size].read_bytes()
        chunk_type = ICNS_CHUNKS[size]
        chunks.extend(chunk_type)
        chunks.extend(struct.pack(">I", len(image_data) + 8))
        chunks.extend(image_data)
    target.write_bytes(b"icns" + struct.pack(">I", len(chunks) + 8) + chunks)


def _generate_icons() -> None:
    if not PNG.exists():
        raise SystemExit("release icon source missing: assets/LUCID.png")

    with tempfile.TemporaryDirectory(prefix="lucid-icons-") as tmp:
        tmp_path = Path(tmp)
        png_paths: dict[int, Path] = {}
        for size in REQUIRED_SIZES:
            target = tmp_path / f"LUCID_{size}.png"
            _resize_png(PNG, target, size)
            png_paths[size] = target

        _write_ico(png_paths, ICO)

        _write_icns(png_paths, ICNS)


def _icns_sizes(path: Path) -> set[int]:
    data = path.read_bytes()
    if data[:4] != b"icns":
        raise ValueError("not a macOS icon file")

    sizes: set[int] = set()
    offset = 8
    while offset + 8 <= len(data):
        chunk_type = data[offset : offset + 4]
        chunk_size = struct.unpack(">I", data[offset + 4 : offset + 8])[0]
        if chunk_size < 8:
            raise ValueError("invalid ICNS chunk")
        if chunk_type in ICNS_CHUNK_SIZES:
            image_data = data[offset + 8 : offset + chunk_size]
            png_size = max(_png_size(image_data))
            expected_size = ICNS_CHUNK_SIZES[chunk_type]
            if png_size == expected_size:
                sizes.add(expected_size)
        offset += chunk_size
    return sizes


def main() -> int:
    if not ICNS.exists() or not ICO.exists():
        _generate_icons()

    missing = [str(path.relative_to(ROOT)) for path in (PNG, ICNS, ICO) if not path.exists()]
    if missing:
        raise SystemExit(f"release icons missing: {', '.join(missing)}")

    if ICNS.read_bytes()[:4] != b"icns":
        raise SystemExit("assets/LUCID.icns is not a valid macOS icon file")

    ico_sizes = _ico_sizes(ICO)
    if not set(REQUIRED_SIZES).issubset(ico_sizes):
        _generate_icons()
        ico_sizes = _ico_sizes(ICO)
    missing_ico = sorted(set(REQUIRED_SIZES) - ico_sizes)
    if missing_ico:
        raise SystemExit(f"assets/LUCID.ico missing icon sizes: {missing_ico}")

    icns_sizes = _icns_sizes(ICNS)
    missing_icns = sorted(set(REQUIRED_SIZES) - icns_sizes)
    if missing_icns:
        _generate_icons()
        icns_sizes = _icns_sizes(ICNS)
        missing_icns = sorted(set(REQUIRED_SIZES) - icns_sizes)
    if missing_icns:
        raise SystemExit(f"assets/LUCID.icns missing icon sizes: {missing_icns}")

    print(
        "release icons verified: "
        f"ICO={sorted(ico_sizes)} ICNS={sorted(icns_sizes)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
