from __future__ import annotations

import subprocess
import sys

from PySide6.QtCore import QThread, Signal


class ProductionWorker(QThread):
    log = Signal(str)
    finished = Signal(bool)

    def __init__(self, topic: str, parent=None):
        super().__init__(parent)
        self.topic = topic

    def run(self):
        cmd = [
            sys.executable,
            "-m",
            "hgpt_ai_os.production",
            "--topic",
            self.topic,
        ]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            assert process.stdout is not None

            for line in process.stdout:
                self.log.emit(line.rstrip())

            process.wait()

            self.finished.emit(process.returncode == 0)

        except Exception as e:
            self.log.emit(str(e))
            self.finished.emit(False)