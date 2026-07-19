from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WARN_FILE = ROOT / "build" / "lucid" / "warn-lucid.txt"
CRITICAL_PATTERNS = re.compile(
    r"\b("
    r"asset|assets|resource|resources|icon|ico|icns|png|bmp|svg|branding|"
    r"LUCID\.(?:ico|icns|png)|app_logo|about_logo|splash|installer_"
    r")\b",
    re.IGNORECASE,
)


def _warning_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip().startswith(("missing module named", "excluded module named"))
    ]


def classify(path: Path) -> dict[str, list[str]]:
    warnings = _warning_lines(path)
    critical = [line for line in warnings if CRITICAL_PATTERNS.search(line)]
    non_critical = [line for line in warnings if line not in critical]
    return {"critical": critical, "non_critical": non_critical}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("warn_file", nargs="?", default=str(DEFAULT_WARN_FILE))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = Path(args.warn_file)
    result = classify(path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"PyInstaller warnings: {path}")
        print(f"Critical: {len(result['critical'])}")
        for line in result["critical"]:
            print(f"CRITICAL: {line}")
        print(f"Non-critical: {len(result['non_critical'])}")
        for line in result["non_critical"]:
            print(f"NON-CRITICAL: {line}")

    return 1 if result["critical"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
