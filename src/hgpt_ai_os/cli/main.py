import argparse

from hgpt_ai_os.builder.generator import ProjectGenerator
from hgpt_ai_os.workflows.marketing.workflow import MarketingWorkflow


def main():
    parser = argparse.ArgumentParser(prog="hgpt")
    sub = parser.add_subparsers(dest="command")

    build = sub.add_parser("build")
    build_sub = build.add_subparsers(dest="type")

    project = build_sub.add_parser("project")
    project.add_argument("name")

    marketing = build_sub.add_parser("marketing")
    marketing.add_argument("day")

    args = parser.parse_args()

    if args.command == "build":

        if args.type == "project":
            ProjectGenerator().generate(args.name)
            print(f"✅ Project '{args.name}' created")

        elif args.type == "marketing":
            MarketingWorkflow().run(args.day)
            print(f"✅ Marketing package '{args.day}' created")


if __name__ == "__main__":
    main()
