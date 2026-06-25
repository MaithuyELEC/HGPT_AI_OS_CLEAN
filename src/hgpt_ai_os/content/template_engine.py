from pathlib import Path


class TemplateEngine:

    def render(self, template_file: str, values: dict):

        template = Path(template_file).read_text(encoding="utf-8")

        for key, value in values.items():

            if isinstance(value, list):
                value = "\n".join(map(str, value))
            elif value is None:
                value = ""
            else:
                value = str(value)

            template = template.replace(f"{{{{{key}}}}}", value)

        return template
