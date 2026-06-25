from hgpt_ai_os.content.hook_selector import HookSelector
from hgpt_ai_os.content.knowledge_loader import KnowledgeLoader
from .models import ContentContext


class ContentContextEngine:

    def __init__(self):
        self.selector = HookSelector()
        self.loader = KnowledgeLoader()

    def build(self, topic: str, context: str = "") -> ContentContext:
        return ContentContext(
            title=topic,
            hook=self.selector.select(topic),
            problem=context,
            analysis=self.loader.load("facebook/framework.md"),
            solution="Chuẩn hóa quy trình, SOP và Knowledge Base.",
            lesson="Đừng chỉ sửa lỗi. Hãy sửa quy trình tạo ra lỗi.",
            action=self.loader.load("facebook/cta.md"),
            hashtags=self.loader.load("hashtags/default.txt").splitlines(),
        )
