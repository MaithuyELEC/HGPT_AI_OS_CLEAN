from __future__ import annotations

import base64
import hashlib
import json
import os
import platform
import subprocess
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


SERVICE_NAME = "Lucid AI Studio"


class SecureSecretStore:
    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir

    def get(self, provider: str) -> str:
        key = _normalize_provider(provider)
        return self._system_get(key) or self._fallback_get(key)

    def set(self, provider: str, secret: str) -> None:
        key = _normalize_provider(provider)
        value = secret.strip()
        if not value:
            self.delete(key)
            return
        if not self._system_set(key, value):
            self._fallback_set(key, value)

    def delete(self, provider: str) -> None:
        key = _normalize_provider(provider)
        self._system_delete(key)
        self._fallback_delete(key)

    def has(self, provider: str) -> bool:
        return bool(self.get(provider))

    def backend(self) -> str:
        system = platform.system().lower()
        if system == "darwin":
            return "macOS Keychain"
        if system == "windows":
            return "Windows Credential Manager"
        return "Encrypted local fallback"

    def _account(self, provider: str) -> str:
        return f"{SERVICE_NAME}:{provider}"

    def _system_get(self, provider: str) -> str:
        if not self._use_system_store():
            return ""
        system = platform.system().lower()
        if system == "darwin":
            return self._mac_get(provider)
        if system == "windows":
            return self._windows_get(provider)
        return ""

    def _system_set(self, provider: str, secret: str) -> bool:
        if not self._use_system_store():
            return False
        system = platform.system().lower()
        if system == "darwin":
            return self._mac_set(provider, secret)
        if system == "windows":
            return self._windows_set(provider, secret)
        return False

    def _system_delete(self, provider: str) -> None:
        if not self._use_system_store():
            return
        system = platform.system().lower()
        if system == "darwin":
            self._mac_delete(provider)
        elif system == "windows":
            self._windows_delete(provider)

    def _mac_get(self, provider: str) -> str:
        try:
            result = subprocess.run(
                [
                    "security",
                    "find-generic-password",
                    "-s",
                    SERVICE_NAME,
                    "-a",
                    self._account(provider),
                    "-w",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError:
            return ""
        return result.stdout.strip() if result.returncode == 0 else ""

    def _mac_set(self, provider: str, secret: str) -> bool:
        self._mac_delete(provider)
        try:
            result = subprocess.run(
                [
                    "security",
                    "add-generic-password",
                    "-U",
                    "-s",
                    SERVICE_NAME,
                    "-a",
                    self._account(provider),
                    "-w",
                    secret,
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError:
            return False
        return result.returncode == 0

    def _mac_delete(self, provider: str) -> None:
        try:
            subprocess.run(
                [
                    "security",
                    "delete-generic-password",
                    "-s",
                    SERVICE_NAME,
                    "-a",
                    self._account(provider),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError:
            pass

    def _windows_get(self, provider: str) -> str:
        try:
            import ctypes
            from ctypes import wintypes
        except ImportError:
            return ""

        class CREDENTIAL(ctypes.Structure):
            _fields_ = [
                ("Flags", wintypes.DWORD),
                ("Type", wintypes.DWORD),
                ("TargetName", wintypes.LPWSTR),
                ("Comment", wintypes.LPWSTR),
                ("LastWritten", wintypes.FILETIME),
                ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)),
                ("Persist", wintypes.DWORD),
                ("AttributeCount", wintypes.DWORD),
                ("Attributes", wintypes.LPVOID),
                ("TargetAlias", wintypes.LPWSTR),
                ("UserName", wintypes.LPWSTR),
            ]

        credential = ctypes.POINTER(CREDENTIAL)()
        if not ctypes.windll.advapi32.CredReadW(
            self._account(provider),
            1,
            0,
            ctypes.byref(credential),
        ):
            return ""
        try:
            blob = ctypes.string_at(
                credential.contents.CredentialBlob,
                credential.contents.CredentialBlobSize,
            )
            return blob.decode("utf-16-le").rstrip("\x00")
        finally:
            ctypes.windll.advapi32.CredFree(credential)

    def _windows_set(self, provider: str, secret: str) -> bool:
        try:
            import ctypes
            from ctypes import wintypes
        except ImportError:
            return False

        class CREDENTIAL(ctypes.Structure):
            _fields_ = [
                ("Flags", wintypes.DWORD),
                ("Type", wintypes.DWORD),
                ("TargetName", wintypes.LPWSTR),
                ("Comment", wintypes.LPWSTR),
                ("LastWritten", wintypes.FILETIME),
                ("CredentialBlobSize", wintypes.DWORD),
                ("CredentialBlob", wintypes.LPBYTE),
                ("Persist", wintypes.DWORD),
                ("AttributeCount", wintypes.DWORD),
                ("Attributes", wintypes.LPVOID),
                ("TargetAlias", wintypes.LPWSTR),
                ("UserName", wintypes.LPWSTR),
            ]

        encoded = secret.encode("utf-16-le")
        blob = ctypes.create_string_buffer(encoded)
        credential = CREDENTIAL()
        credential.Type = 1
        credential.TargetName = self._account(provider)
        credential.CredentialBlobSize = len(encoded)
        credential.CredentialBlob = ctypes.cast(blob, wintypes.LPBYTE)
        credential.Persist = 2
        credential.UserName = SERVICE_NAME
        return bool(ctypes.windll.advapi32.CredWriteW(ctypes.byref(credential), 0))

    def _windows_delete(self, provider: str) -> None:
        try:
            import ctypes
        except ImportError:
            return
        ctypes.windll.advapi32.CredDeleteW(self._account(provider), 1, 0)

    def _fallback_path(self) -> Path:
        if self.config_dir is not None:
            return self.config_dir / "secrets.enc"
        return Path.home() / "Documents" / "LUCID" / "secrets.enc"

    def _use_system_store(self) -> bool:
        system = platform.system().lower()
        if system == "darwin" and os.getenv("USERPROFILE"):
            return False
        return system in {"darwin", "windows"}

    def _fallback_get(self, provider: str) -> str:
        data = self._fallback_read()
        return str(data.get(provider, "")).strip()

    def _fallback_set(self, provider: str, secret: str) -> None:
        data = self._fallback_read()
        data[provider] = secret.strip()
        self._fallback_write(data)

    def _fallback_delete(self, provider: str) -> None:
        data = self._fallback_read()
        if provider in data:
            del data[provider]
            self._fallback_write(data)

    def _fallback_read(self) -> dict[str, str]:
        path = self._fallback_path()
        if not path.exists():
            return {}
        try:
            encrypted = path.read_bytes()
            raw = self._fernet().decrypt(encrypted)
            data = json.loads(raw.decode("utf-8"))
        except (OSError, InvalidToken, json.JSONDecodeError, UnicodeDecodeError):
            return {}
        return data if isinstance(data, dict) else {}

    def _fallback_write(self, data: dict[str, str]) -> None:
        path = self._fallback_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(data, indent=2).encode("utf-8")
        path.write_bytes(self._fernet().encrypt(raw))

    def _fernet(self) -> Fernet:
        seed = "|".join(
            (
                SERVICE_NAME,
                platform.node(),
                os.getenv("USERPROFILE") or str(Path.home()),
            )
        )
        digest = hashlib.sha256(seed.encode("utf-8")).digest()
        return Fernet(base64.urlsafe_b64encode(digest))


def _normalize_provider(provider: str) -> str:
    return (provider or "").strip().lower() or "openai"
