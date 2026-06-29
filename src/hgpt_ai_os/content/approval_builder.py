from hgpt_ai_os.content.template_engine import TemplateEngine


class ApprovalBuilder:

    def __init__(self):
        self.template = TemplateEngine()

    def build(self, *args, **kwargs):
        return self.template.render(
            "templates/approval/default.md",
            {},
        )
