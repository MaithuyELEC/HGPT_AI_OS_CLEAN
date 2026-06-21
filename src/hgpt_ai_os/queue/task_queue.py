from collections import deque


class TaskQueue:
    def __init__(self):
        self.queue = deque()

    def put(self, task):
        self.queue.append(task)

    def get(self):
        return self.queue.popleft()

    def empty(self):
        return len(self.queue) == 0
