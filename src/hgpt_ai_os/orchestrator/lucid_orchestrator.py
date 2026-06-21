import json
from datetime import datetime
from pathlib import Path

from hgpt_ai_os.agents.marketing.marketing_agent import MarketingAgent


class LucidOrchestrator:

    def create_day11_pack(self):
        marketing = MarketingAgent()
        output_dir = marketing.create_day11_content()

        status = {
            "module": "Lucid Marketing",
            "day": "Day11",
            "status": "WAITING_APPROVAL",
            "created_at": datetime.now().isoformat(),
            "output_dir": str(output_dir),
            "next_action": "MaithuyELEC review and approve"
        }

        status_path = Path(output_dir) / "_approval_status.json"
        status_path.write_text(
            json.dumps(status, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        return output_dir
