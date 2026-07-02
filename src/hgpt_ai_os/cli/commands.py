from hgpt_ai_os.runtime import Runtime
from hgpt_ai_os.kernel.kernel import HGPTKernel
from hgpt_ai_os.agents.maintenance.maintenance_agent import MaintenanceAgent
from hgpt_ai_os.task.manager import TaskManager
from hgpt_ai_os.version import APP_VERSION

APP_NAME = "HGPT AI OS"
VERSION = APP_VERSION

_task_manager = TaskManager()


def show_help():
    print("""
HGPT AI OS

Commands:
  help
  version
  status
  maintenance run
  task create <name>
  task list
  task run <task_id>
  task complete <task_id>
""")


def show_version():
    runtime = Runtime()
    print(runtime.version())


def show_status():
    runtime = Runtime()
    status = runtime.status()

    print("Runtime Status:")

    for key, value in status.items():
        print(f"- {key}: {value}")


def maintenance_run():
    kernel = HGPTKernel()
    kernel.agents.register("maintenance", MaintenanceAgent())
    kernel.agents.run("maintenance")


def task_create(name: str):
    task = _task_manager.create(name)
    print(f"Task created: {task.id} | {task.name} | {task.status}")


def task_list():
    tasks = _task_manager.list()

    if not tasks:
        print("No tasks.")
        return

    for task in tasks:
        print(f"{task.id} | {task.name} | {task.status} | {task.created_at}")


def task_run(task_id: str):
    task = _task_manager.run(task_id)

    if not task:
        print("Task not found.")
        return

    print(f"Task running: {task.id} | {task.name} | {task.status}")


def task_complete(task_id: str):
    task = _task_manager.complete(task_id)

    if not task:
        print("Task not found.")
        return

    print(f"Task completed: {task.id} | {task.name} | {task.status}")


def marketing_day11():
    from hgpt_ai_os.agents.marketing.marketing_agent import MarketingAgent

    agent = MarketingAgent()
    output_dir = agent.create_day11_content()

    print(f"Marketing Day11 content created: {output_dir}")


def lucid_day11():
    from hgpt_ai_os.orchestrator.lucid_orchestrator import LucidOrchestrator

    agent = LucidOrchestrator()
    output_dir = agent.create_day11_pack()

    print(f"Lucid Day11 pack created: {output_dir}")
    print("Status: WAITING_APPROVAL")


def lucid_approve_day11():
    import json
    from datetime import datetime
    from pathlib import Path

    status_path = Path("outputs/marketing/day11/_approval_status.json")

    if not status_path.exists():
        print("Approval status file not found.")
        return

    status = json.loads(status_path.read_text(encoding="utf-8"))
    status["status"] = "APPROVED"
    status["approved_at"] = datetime.now().isoformat()
    status["approved_by"] = "MaithuyELEC"

    status_path.write_text(
        json.dumps(status, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("Lucid Day11 approved.")
    print("Status: APPROVED")


def lucid_status_day11():
    import json
    from pathlib import Path

    status_path = Path("outputs/marketing/day11/_approval_status.json")

    if not status_path.exists():
        print("No Lucid Day11 status found.")
        return

    status = json.loads(status_path.read_text(encoding="utf-8"))

    print("Lucid Day11 Status")
    print("==================")

    for key, value in status.items():
        print(f"{key}: {value}")


def lucid_ready_day11():
    import json
    import shutil
    from pathlib import Path

    base_dir = Path("outputs/marketing/day11")
    status_path = base_dir / "_approval_status.json"
    ready_dir = base_dir / "READY_TO_POST"

    if not status_path.exists():
        print("Approval status file not found.")
        return

    status = json.loads(status_path.read_text(encoding="utf-8"))

    if status.get("status") != "APPROVED":
        print("Day11 is not approved yet.")
        print("Run: hgpt lucid approve day11")
        return

    ready_dir.mkdir(parents=True, exist_ok=True)

    for file in base_dir.glob("*.docx"):
        shutil.copy(file, ready_dir / file.name)

    (ready_dir / "POSTING_INSTRUCTION.txt").write_text(
        "Day11 content is APPROVED and READY TO POST.\n\n"
        "1. Open facebook.docx\n"
        "2. Copy content to Facebook\n"
        "3. Open tiktok.docx\n"
        "4. Copy script/caption to TikTok\n"
        "5. Use image_prompt.docx for image generation\n"
        "6. Use video_prompt.docx for video generation\n",
        encoding="utf-8"
    )

    print(f"Ready-to-post package created: {ready_dir}")


def lucid_posted_day11():
    import json
    from datetime import datetime
    from pathlib import Path

    status_path = Path("outputs/marketing/day11/_approval_status.json")

    if not status_path.exists():
        print("Approval status file not found.")
        return

    status = json.loads(status_path.read_text(encoding="utf-8"))

    if status.get("status") != "APPROVED":
        print("Day11 is not approved yet.")
        return

    status["status"] = "POSTED"
    status["posted_at"] = datetime.now().isoformat()
    status["posted_by"] = "MaithuyELEC"

    status_path.write_text(
        json.dumps(status, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    log_dir = Path("outputs/marketing/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    with open(log_dir / "posting_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | Day11 | POSTED | MaithuyELEC\n")

    print("Lucid Day11 marked as POSTED.")
