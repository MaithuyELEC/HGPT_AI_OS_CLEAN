# RECURSION_FIX_REPORT

## Root cause

Runtime tracing wrapped GUI stdout plumbing. During generation, stdout/stderr are redirected through `SignalStream`; `_runtime_trace_event()` then used `print()`, which wrote back into the redirected stream. Because `SignalStream.write()` / `SignalStream.flush()` were also instrumented, the trace path could re-enter itself:

`wrapper() -> _runtime_trace_event() -> print() -> SignalStream.flush()/write() -> wrapper() -> _runtime_trace_event()`

## Files modified

- `src/hgpt_ai_os/diagnostics.py`
  - Added a thread-local tracing guard.
  - Changed `_runtime_trace_event()` to return immediately while tracing is already active.
  - Changed runtime ENTER/EXIT trace emission to write through `sys.__stdout__` instead of `print()`, bypassing redirected/wrapped stdout.
  - Made wrapped functions call through directly when the thread-local tracing guard is active.
  - Added support for `__runtime_trace_exempt__` functions.

- `src/hgpt_ai_os/gui/worker.py`
  - Marked `SignalStream.write()` and `SignalStream.flush()` as runtime-trace exempt so stdout transport never invokes runtime tracing.

No architecture changes were made. Runtime tracing, diagnostics, and wrappers remain enabled.

## Verification

- Syntax check:
  - `PYTHONPATH=src python3 -m py_compile src/hgpt_ai_os/diagnostics.py src/hgpt_ai_os/gui/worker.py`
  - Result: passed.

- GUI generation verification:
  - Command shape used: `PATH=.venv/bin:$PATH QT_QPA_PLATFORM=offscreen PYTHONPATH=src python3 ...`
  - Reason: the system `python3` lacks `PySide6`; the repo venv provides the application GUI dependency while still invoking `python3`.
  - Topic: `Cầu trục 7.5T bị đứt cáp`
  - Result: `VERIFICATION_STATUS: success=True`
  - Generated files: 7 DOCX files under `/Users/macos/Documents/LUCID/outputs/marketing/Day1025/`

- Recursion check:
  - `RecursionError`: not present.
  - `SignalStream.write`: not traced.
  - `SignalStream.flush`: not traced.

- Required trace markers still present:
  - `ENTER`: present in runtime trace output.
  - `EXIT`: present in runtime trace output.
  - `selected_playbook`: present.
  - `selected_profile`: present.
  - `selected_builder`: present.
  - `writer_selected`: present.
  - `writer_class`: present.
  - `engineering_sections_generated`: present.
  - `DOCX save completed`: present.
