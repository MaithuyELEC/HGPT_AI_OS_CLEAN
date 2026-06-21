from hgpt_ai_os.runtime import Runtime
from hgpt_ai_os.kernel.kernel import HGPTKernel
from hgpt_ai_os.agents.maintenance.maintenance_agent import MaintenanceAgent

APP_NAME = "HGPT AI OS"
VERSION = "0.3.0"


def show_help():
    print("""
HGPT AI OS

Commands:
  help
  version
  status
  maintenance run
""")


def show_version():
    runtime = Runtime()
    print(runtime.version())


def show_status():
    runtime = Runtime()

    print("Runtime Status:")

    for key, value in runtime.status().items():
        print(f"- {key}: {value}")


def maintenance_run():
    kernel = HGPTKernel()

    kernel.agents.register(
        "maintenance",
        MaintenanceAgent()
    )

    kernel.agents.run("maintenance")
