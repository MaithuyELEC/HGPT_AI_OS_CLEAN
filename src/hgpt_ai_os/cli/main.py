import argparse

from hgpt_ai_os.cli.commands import (
    lucid_approve_day11,
    lucid_day11,
    lucid_status_day11,
    maintenance_run,
    marketing_day11,
    show_help,
    show_status,
    show_version,
    task_complete,
    task_create,
    task_list,
    task_run,
)


def main():
    parser = argparse.ArgumentParser(
        prog="hgpt",
        description="HGPT AI Operating System",
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("help")
    sub.add_parser("version")
    sub.add_parser("status")

    maintenance = sub.add_parser("maintenance")
    maintenance.add_argument("action", choices=["run"])

    task = sub.add_parser("task")
    task.add_argument("action", choices=["create", "list", "run", "complete"])
    task.add_argument("value", nargs="?")

    marketing = sub.add_parser("marketing")
    marketing.add_argument("action", choices=["day11"])

    lucid = sub.add_parser("lucid")
    lucid.add_argument("action", choices=["day11", "approve", "status"])
    lucid.add_argument("value", nargs="?")

    args = parser.parse_args()

    if args.command == "help":
        show_help()

    elif args.command == "version":
        show_version()

    elif args.command == "status":
        show_status()

    elif args.command == "maintenance":
        if args.action == "run":
            maintenance_run()

    elif args.command == "task":
        if args.action == "create":
            if not args.value:
                print("Task name is required.")
            else:
                task_create(args.value)

        elif args.action == "list":
            task_list()

        elif args.action == "run":
            if not args.value:
                print("Task ID is required.")
            else:
                task_run(args.value)

        elif args.action == "complete":
            if not args.value:
                print("Task ID is required.")
            else:
                task_complete(args.value)

    elif args.command == "marketing":
        if args.action == "day11":
            marketing_day11()

    elif args.command == "lucid":
        if args.action == "day11":
            lucid_day11()

        elif args.action == "status":
            lucid_status_day11()

        elif args.action == "approve":
            if args.value == "day11":
                lucid_approve_day11()
            else:
                print("Usage: hgpt lucid approve day11")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
