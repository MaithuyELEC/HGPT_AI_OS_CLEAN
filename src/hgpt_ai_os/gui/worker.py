from __future__ import annotations

import io
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from PySide6.QtCore import QThread, Signal


class SignalStream(io.TextIOBase):
    def __init__(self, emit_func):
        super().__init__()
        self.emit_func = emit_func
        self.buffer = ""

    def write(self, text):
        if not text:
            return 0

        self.buffer += text

        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            if line.strip():
                self.emit_func(line)

        return len(text)

    def flush(self):
        if self.buffer.strip():
            self.emit_func(self.buffer.strip())
        self.buffer = ""


class ProductionWorker(QThread):
    log = Signal(str)
    finished = Signal(bool)

    def __init__(self, topic: str, parent=None):
        super().__init__(parent)
        self.topic = topic

    def run(self):
        try:
            from hgpt_ai_os import production

            

            stream = SignalStream(self.log.emit)

            with redirect_stdout(stream), redirect_stderr(stream):
                day = production.next_day()
                production.build_outputs(day, self.topic)

            stream.flush()
            self.finished.emit(True)

        except Exception:
            self.log.emit("STATUS : PRODUCTION FAILED")
            self.log.emit(traceback.format_exc())
            self.finished.emit(False)
