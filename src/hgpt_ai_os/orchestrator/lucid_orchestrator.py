from hgpt_ai_os.planner.planner_engine import PlannerEngine


class LucidOrchestrator:

    def run(self):

        planner = PlannerEngine()

        task = planner.next_task()

        if not task:
            print("No TODO task.")
            return

        print("=" * 50)
        print("HGPT LUCID")
        print("=" * 50)
        print(f"Day      : {task['day']}")
        print(f"Topic    : {task['topic']}")
        print(f"Platform : {task['platform']}")
        print(f"Folder   : {task['folder']}")
        print("=" * 50)

        planner.update_status(task["row"], "RUNNING")

        print("Planner updated -> RUNNING")
