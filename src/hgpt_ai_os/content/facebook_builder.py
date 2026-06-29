from hgpt_ai_os.content.template_engine import TemplateEngine
from hgpt_ai_os.content_context.engine import ContentContextEngine
from hgpt_ai_os.content_context.models import ContentContext


class FacebookBuilder:

    def __init__(self):
        self.template = TemplateEngine()
        self.context_engine = ContentContextEngine()

    def build(self, topic="", context="", content: ContentContext | None = None):

        if content is None:
            content = self.context_engine.build(topic, context)

        return self.template.render(
            "templates/facebook/default.md",
            {
                "HOOK": content.hook,
                "TOPIC": content.title,
                "PROBLEM": content.problem,
                "ANALYSIS": content.analysis,
                "SOLUTION": content.solution,
                "LESSON": content.lesson,
                "CTA": content.action,
                "HASHTAGS": " ".join(content.hashtags),
            },
        )
