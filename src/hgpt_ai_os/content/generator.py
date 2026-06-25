from hgpt_ai_os.content_context.engine import ContentContextEngine
from hgpt_ai_os.content.factory.builder_factory import BuilderFactory


class ContentGenerator:

    def __init__(self):
        self.context_engine = ContentContextEngine()

    def generate(self, platform: str, topic: str, context: str = ""):
        ctx = self.context_engine.build(topic, context)
        builder = BuilderFactory.create(platform)
        return builder.build(content=ctx)

    def generate_facebook(self, topic, context=""):
        return self.generate("facebook", topic, context)

    def generate_tiktok(self, topic, context=""):
        return self.generate("tiktok", topic, context)

    def generate_image_prompt(self, topic, context=""):
        return self.generate("image", topic, context)

    def generate_video_prompt(self, topic, context=""):
        return self.generate("video", topic, context)

    def generate_hashtags(self):
        return """
#MaithuyELEC
#LucidAI
#HGPTSteel
#DigitalFactory
#SteelKnowledgeBase
"""

    def generate_checklist(self):
        return """
[ ] Facebook
[ ] TikTok
[ ] Image Prompt
[ ] Video Prompt
[ ] Hashtags
[ ] Review
[ ] Ready To Post
"""

    def generate_seo(self, topic, context=""):
        return f"""
TITLE

{topic}

DESCRIPTION

{context}
"""
