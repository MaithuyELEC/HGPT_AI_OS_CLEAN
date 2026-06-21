import argparse

from hgpt_ai_os.cli.commands import (
    maintenance_run,
    show_help,
    show_status,
    show_version,
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

    elif args.command == "maintenance":

        if args.action == "run":
            maintenance_run()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
