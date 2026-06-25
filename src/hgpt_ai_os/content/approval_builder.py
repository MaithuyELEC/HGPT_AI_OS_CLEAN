from pathlib import Path


class ApprovalBuilder:

    def build(self, *args, **kwargs):
        return Path("templates/approval/default.md").read_text(encoding="utf-8")
