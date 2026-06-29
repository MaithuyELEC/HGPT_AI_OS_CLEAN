from pathlib import Path
from .scaffold import ProjectScaffold


class ProjectBuilder:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.root = Path(project_name)

    def build(self):
        ProjectScaffold.build(self.project_name)
        return self.root


if __name__ == "__main__":
    ProjectBuilder("DemoProject").build()
    print("HGPT Builder PASS")
