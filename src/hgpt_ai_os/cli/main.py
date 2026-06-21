import argparse

from hgpt_ai_os.agents.maintenance.maintenance_agent import MaintenanceAgent
from hgpt_ai_os.kernel.kernel import HGPTKernel


def main():
    parser = argparse.ArgumentParser(
        prog="hgpt",
        description="HGPT AI Operating System"
    )

    sub = parser.add_subparsers(dest="command")

    maintenance = sub.add_parser("maintenance")
    maintenance.add_argument(
        "action",
        choices=["run"],
        help="Maintenance action"
    )

    args = parser.parse_args()

    kernel = HGPTKernel()

    kernel.agents.register(
        "maintenance",
        MaintenanceAgent()
    )

    if args.command == "maintenance":

        if args.action == "run":
            kernel.agents.run("maintenance")


if __name__ == "__main__":
    main()
