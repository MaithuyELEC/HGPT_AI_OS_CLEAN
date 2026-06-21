import argparse

from hgpt_ai_os.cli.commands import (
    maintenance_run,
    show_help,
    show_status,
    show_version,
    task_create,
    task_list,
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

    task = sub.add_parser("task")
    task.add_argument("action", choices=["create", "list"])
    task.add_argument("name", nargs="?")

    maintenance = sub.add_parser("maintenance")

    maintenance.add_argument(
        "action",
        choices=["run"],
    )

    args = parser.parse_args()

    if args.command == "help":
        show_help()

    elif args.command == "version":
        show_version()

    elif args.command == "status":
        show_status()

    elif args.command == "task":

        if args.action == "create":
            if not args.name:
                print("Task name is required.")
            else:
                task_create(args.name)

        elif args.action == "list":
            task_list()

    elif args.command == "maintenance":

        if args.action == "run":
            maintenance_run()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
