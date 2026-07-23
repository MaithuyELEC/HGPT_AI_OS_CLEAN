#!/usr/bin/env python3
"""Normalize OpenSSL dylibs in the macOS PyInstaller app bundle."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_BUNDLE = ROOT / "dist" / "Lucid AI Studio.app"
ONEDIR_BUNDLE = ROOT / "dist" / "LUCID" / "_internal"
REQUIRED_SSL_SYMBOL = "_SSL_get0_group_name"


def run(args: list[str]) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def cryptography_openssl_paths() -> tuple[Path, Path]:
    code = (
        "import cryptography.hazmat.bindings._rust as r;"
        "print(r.__file__)"
    )
    rust_ext = Path(run([sys.executable, "-c", code]).strip())
    linked = run(["otool", "-L", str(rust_ext)])
    ssl_path = None
    crypto_path = None
    for line in linked.splitlines():
        dep = line.strip().split(" ", 1)[0]
        if dep.endswith("/libssl.3.dylib"):
            ssl_path = Path(dep)
        elif dep.endswith("/libcrypto.3.dylib"):
            crypto_path = Path(dep)
    if not ssl_path or not crypto_path:
        raise SystemExit("Could not find cryptography-linked OpenSSL dylibs.")
    if not ssl_path.exists() or not crypto_path.exists():
        raise SystemExit(
            f"cryptography links to missing OpenSSL dylibs: {ssl_path}, {crypto_path}"
        )
    return ssl_path, crypto_path


def verify_ssl_symbol(ssl_path: Path) -> None:
    symbols = run(["nm", "-gU", str(ssl_path)])
    if REQUIRED_SSL_SYMBOL not in symbols:
        raise SystemExit(f"{ssl_path} does not export {REQUIRED_SSL_SYMBOL}.")


def replace_dylibs(target_dir: Path, ssl_path: Path, crypto_path: Path) -> None:
    if not target_dir.exists():
        return
    target_dir.mkdir(parents=True, exist_ok=True)
    for source in (ssl_path, crypto_path):
        target = target_dir / source.name
        if target.exists() or target.is_symlink():
            target.unlink()
        shutil.copy2(source, target)
        os.chmod(target, 0o755)


def remove_top_level_resource_links(resources_dir: Path) -> None:
    for name in ("libssl.3.dylib", "libcrypto.3.dylib"):
        target = resources_dir / name
        if target.exists() or target.is_symlink():
            target.unlink()


def verify_bundle(frameworks_dir: Path) -> None:
    ssl = frameworks_dir / "libssl.3.dylib"
    crypto = frameworks_dir / "libcrypto.3.dylib"
    if not ssl.exists() or not crypto.exists():
        raise SystemExit("OpenSSL dylibs were not copied into Contents/Frameworks.")
    verify_ssl_symbol(ssl)

    rust_ext = frameworks_dir / "cryptography" / "hazmat" / "bindings" / "_rust.abi3.so"
    if rust_ext.exists():
        deps = run(["otool", "-L", str(rust_ext)])
        if "@rpath/libssl.3.dylib" not in deps or "@rpath/libcrypto.3.dylib" not in deps:
            raise SystemExit("cryptography is not linked through bundled @rpath OpenSSL.")


def main() -> int:
    ssl_path, crypto_path = cryptography_openssl_paths()
    verify_ssl_symbol(ssl_path)

    replace_dylibs(ONEDIR_BUNDLE, ssl_path, crypto_path)

    if APP_BUNDLE.exists():
        contents = APP_BUNDLE / "Contents"
        frameworks = contents / "Frameworks"
        replace_dylibs(frameworks, ssl_path, crypto_path)
        remove_top_level_resource_links(contents / "Resources")
        verify_bundle(frameworks)

    print(f"Bundled OpenSSL from {ssl_path.parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
