from hgpt_ai_os.queue import TaskQueue, Worker


def main():
    q = TaskQueue()
    worker = Worker(q)

    q.put("Job 001 - Database Backup")
    q.put("Job 002 - Generate Report")

    print(worker.run_once())
    print(worker.run_once())
    print(worker.run_once())


if __name__ == "__main__":
    main()