from hgpt_ai_os.task.manager import TaskManager


manager = TaskManager()

manager.create("Scan Email")
manager.create("Generate Report")
manager.create("Check Database")

for task in manager.list():
    print(task)