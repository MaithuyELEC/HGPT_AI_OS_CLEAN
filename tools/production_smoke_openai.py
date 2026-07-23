from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import subprocess
import sys
import traceback
from pathlib import Path


TOPIC = "Đường hàn SAW bị rỗ khí"
EXPECTED_DOCX = {
    "facebook.docx",
    "tiktok.docx",
    "image_prompt.docx",
    "video_prompt.docx",
    "seo.docx",
    "hashtags.docx",
    "approval_checklist.docx",
}
SECRET_PATTERN = re.compile(r"sk-[A-Za-z0-9_\-]{8,}")


def redact(text: str) -> str:
    return SECRET_PATTERN.sub("sk-REDACTED", text)


def status_line(label: str, ok: bool, detail: str = "") -> None:
    suffix = "PASS" if ok else "FAIL"
    if detail:
        print(f"{label}: {suffix} - {detail}")
    else:
        print(f"{label}: {suffix}")


def load_config():
    from hgpt_ai_os.settings import ConfigManager

    manager = ConfigManager()
    config = manager.load()
    return manager, config


def silence_diagnostics() -> None:
    try:
        import hgpt_ai_os.diagnostics as diagnostics
    except Exception:
        return

    def noop(*args, **kwargs):
        return None

    def passthrough(func):
        return func

    diagnostics.module_loaded = noop
    diagnostics.exact_source = noop
    diagnostics.trace_call = noop
    diagnostics.trace_enter = noop
    diagnostics.trace_exit = noop
    diagnostics.engine_loaded = noop
    diagnostics.fallback = noop
    diagnostics.instrument_runtime_tracing = noop
    diagnostics.trace_function = passthrough


def test_connection() -> bool:
    manager, _ = load_config()
    result = manager.test_connection()
    ok = bool(result.ok and result.message == "Connected")
    status_line(
        "Test Connection",
        ok,
        f"{result.message}; status={result.status}; provider={result.provider}; model={result.model}",
    )
    status_line("Connected", result.message == "Connected", result.status)
    return ok


def generate_once(label: str) -> bool:
    silence_diagnostics()
    from PySide6.QtWidgets import QApplication

    from hgpt_ai_os.gui.main_window import MainWindow
    from hgpt_ai_os.gui.production_service import ProductionService

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.topic.setEditText(TOPIC)

    validation = window.config_manager.validate()
    status_line(f"{label} config connected", validation.ok and validation.status == "Connected", validation.status)
    if not validation.ok:
        window.close()
        app.quit()
        return False

    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            result = ProductionService().run(TOPIC)
    except Exception:
        print(f"{label} runtime log:")
        print(redact(buffer.getvalue()))
        print(redact(traceback.format_exc()))
        window.close()
        app.quit()
        return False

    log = redact(buffer.getvalue())
    files = {path.name for path in result.generated_files}
    missing = sorted(EXPECTED_DOCX - files)
    ok = bool(result.success and not missing and result.output_dir and Path(result.output_dir).exists())
    status_line(f"{label} generate topic", ok, TOPIC)
    status_line(f"{label} generate all 7 DOCX", not missing and len(files) >= 7, ", ".join(sorted(files)))
    status_line(f"{label} runtime exceptions", ok, "none" if ok else "generation failed")
    print(f"{label} output_dir: {result.output_dir}")
    if not ok:
        print(f"{label} missing: {missing}")
        print(f"{label} runtime log:")
        print(log)

    window.close()
    app.quit()
    status_line(f"{label} close app", True)
    return ok


def child_session(label: str) -> int:
    try:
        ok = generate_once(label)
        manager, _ = load_config()
        available = bool(manager.api_key("openai"))
        status_line(f"{label} api key available after load", available)
        return 0 if ok and available else 1
    except Exception:
        print(redact(traceback.format_exc()))
        return 1


def run_child(label: str) -> bool:
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", "src")
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    command = [sys.executable, str(Path(__file__).resolve()), "--child-session", label]
    result = subprocess.run(command, cwd=Path(__file__).resolve().parents[1], env=env, text=True, capture_output=True)
    if result.stdout:
        print(redact(result.stdout), end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(redact(result.stderr), end="" if result.stderr.endswith("\n") else "\n")
    return result.returncode == 0


def parent() -> int:
    print("===== LUCID OPENAI PRODUCTION SMOKE =====")
    ok_connection = test_connection()
    ok_first = run_child("first")
    status_line("Reopen app", True)
    ok_second = run_child("second")
    manager, _ = load_config()
    key_available = bool(manager.api_key("openai"))
    status_line("API key still available after restart", key_available)
    overall = ok_connection and ok_first and ok_second and key_available
    status_line("OVERALL", overall)
    return 0 if overall else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child-session")
    args = parser.parse_args()
    if args.child_session:
        return child_session(args.child_session)
    return parent()


if __name__ == "__main__":
    raise SystemExit(main())
