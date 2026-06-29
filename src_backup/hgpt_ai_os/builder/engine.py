"""
HGPT AI OS Builder Engine

BuilderEngine là lớp điều phối tầng Builder.
Hiện tại nó sử dụng ProjectGenerator để tạo project.
Các pipeline Planner / Knowledge / Workflow / Agent
sẽ được tích hợp ở Sprint tiếp theo.
"""

from pathlib import Path

from .generator import ProjectGenerator


class BuilderEngine:
    """Production Builder Engine"""

    def __init__(self):
        self.generator = ProjectGenerator()

    def build(self, project_name: str) -> Path:
        """
        Build a new HGPT project.

        Args:
            project_name: Name of project.

        Returns:
            Path to generated project.
        """
        return self.generator.generate(project_name)


if __name__ == "__main__":
    project = BuilderEngine().build("DemoFactory")
    print(f"Builder PASS -> {project}")
