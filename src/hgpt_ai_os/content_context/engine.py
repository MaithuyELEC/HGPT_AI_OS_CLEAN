from hgpt_ai_os.content.hook_selector import HookSelector
from hgpt_ai_os.content.knowledge_loader import KnowledgeLoader
from .models import ContentContext


class ContentContextEngine:

    def __init__(self):
        self.selector = HookSelector()
        self.loader = KnowledgeLoader()

    def _load_or_default(self, file, default):
        text = self.loader.load(file)
        return text.strip() if text.strip() else default

    def build(self, topic: str, context: str = "") -> ContentContext:

        problem = context.strip() if context.strip() else (
            f"Trong quá trình {topic}, nếu chỉ xử lý hiện tượng "
            "mà không tìm nguyên nhân gốc thì lỗi sẽ tiếp tục tái diễn."
        )

        return ContentContext(
            title=topic,
            hook=self.selector.select(topic),
            problem=problem,
            analysis=self.loader.load("facebook/framework.md"),
            solution=self._load_or_default(
                "facebook/solution.md",
                "Chuẩn hóa quy trình, SOP và Knowledge Base."
            ),
            lesson=self._load_or_default(
                "facebook/lesson.md",
                "Đừng chỉ sửa lỗi. Hãy sửa quy trình tạo ra lỗi."
            ),
            action=self.loader.load("facebook/cta.md"),
hashtags=self.loader.load("hashtags/default.txt").splitlines(),

image_prompt=f"""Create an ultra realistic industrial engineering photo.

Topic:
{topic}

Knowledge:
{problem}
""",

video_prompt=f"""Create a 30-second industrial cinematic video.

Topic:
{topic}

Knowledge:
{problem}
""",
)
