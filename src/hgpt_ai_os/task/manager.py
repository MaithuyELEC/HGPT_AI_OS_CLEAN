from .task import Task


class TaskManager:

    def __init__(self):
        self.tasks = []

    def create(self, name: str):

        task = Task.create(name)

        self.tasks.append(task)

        return task

    def list(self):

        return self.tasks