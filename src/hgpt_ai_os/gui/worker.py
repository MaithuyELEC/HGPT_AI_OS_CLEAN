from __future__ import annotations

import io
import traceback
from contextlib import redirect_stderr, redirect_stdout

from PySide6.QtCore import QThread, Signal

from hgpt_ai_os.core.production_result import ProductionResult

from .production_service import ProductionService


class SignalStream(io.TextIOBase):
    def __init__(self, emit_func, line_callback=None):
        super().__init__()
        self.emit_func = emit_func
        self.line_callback = line_callback
        self.buffer = ""

    def write(self, text):
        if not text:
            return 0

        self.buffer += text

        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            if line.strip():
                if self.line_callback is not None:
                    self.line_callback(line)
                self.emit_func(line)

        return len(text)

    def flush(self):
        if self.buffer.strip():
            if self.line_callback is not None:
                self.line_callback(self.buffer.strip())
            self.emit_func(self.buffer.strip())
        self.buffer = ""


class ProductionWorker(QThread):
    log = Signal(str)
    finished = Signal(object)

    def __init__(self, topic: str, parent=None):
        super().__init__(parent)
        self.topic = topic

    def run(self):
        service = ProductionService()

        try:
            stream = SignalStream(self.log.emit, service.capture_metadata)

            with redirect_stdout(stream), redirect_stderr(stream):
                result = service.run(self.topic)

            stream.flush()
            self.finished.emit(result)

        except Exception:
            self.log.emit("STATUS : PRODUCTION FAILED")
            self.log.emit(traceback.format_exc())
            self.finished.emit(service.failed_result())
