from pathlib import Path

from .project_builder import ProjectBuilder


class ProjectGenerator:

    def generate(self, name: str) -> Path:
        return ProjectBuilder(name).build()


if __name__ == "__main__":
    project = ProjectGenerator().generate("DemoFactory")
    print(project)
