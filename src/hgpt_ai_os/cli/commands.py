from hgpt_ai_os.runtime import Runtime
APP_NAME = "HGPT AI OS"
VERSION = "0.3.0"


def show_help():
    print("""
HGPT AI OS

Commands:
  help       Show help
  version    Show version
  status     Show system status
""")


def show_version():
    runtime = Runtime()
    print(runtime.version())


def show_status():
    runtime = Runtime()
    status = runtime.status()

    print("Runtime Status:")

    for key, value in status.items():
        print(f"- {key}: {value}")