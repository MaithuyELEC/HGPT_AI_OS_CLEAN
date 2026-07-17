from __future__ import annotations

import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ICNS = ASSETS / "LUCID.icns"
ICO = ASSETS / "LUCID.ico"
PNG = ASSETS / "LUCID.png"


def _ico_image_count(path: Path) -> int:
    data = path.read_bytes()[:6]
    reserved, icon_type, count = struct.unpack("<HHH", data)
    if reserved != 0 or icon_type != 1:
        raise ValueError("not a Windows icon file")
    return count


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in (PNG, ICNS, ICO) if not path.exists()]
    if missing:
        raise SystemExit(f"release icons missing: {', '.join(missing)}")

    if ICNS.read_bytes()[:4] != b"icns":
        raise SystemExit("assets/LUCID.icns is not a valid macOS icon file")

    if _ico_image_count(ICO) < 4:
        raise SystemExit("assets/LUCID.ico must contain multiple Windows icon sizes")

    print("release icons verified: assets/LUCID.png, assets/LUCID.icns, assets/LUCID.ico")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
