class Worker:
    def __init__(self, task_queue):
        self.task_queue = task_queue

    def run_once(self):
        if self.task_queue.empty():
            return None

        task = self.task_queue.get()
        return f"Processed: {task}"
