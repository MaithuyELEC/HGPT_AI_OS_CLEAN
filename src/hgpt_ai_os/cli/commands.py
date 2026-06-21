from hgpt_ai_os.runtime import Runtime
from hgpt_ai_os.kernel.kernel import HGPTKernel
from hgpt_ai_os.agents.maintenance.maintenance_agent import MaintenanceAgent
from hgpt_ai_os.task.manager import TaskManager

APP_NAME = "HGPT AI OS"
VERSION = "0.3.0"

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
