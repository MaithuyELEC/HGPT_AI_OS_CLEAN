import sys

from hgpt_ai_os.cli.commands import show_help, show_version, show_status


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1]

    if command == "help":
        show_help()
    elif command == "version":
        show_version()
    elif command == "status":
        show_status()
    else:
        print(f"Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()