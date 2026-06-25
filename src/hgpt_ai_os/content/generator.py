class ContentGenerator:

    def generate_facebook(self, topic, context=""):
        return f"""
HOOK

{topic}

KNOWLEDGE

{context}

LESSON

Do not fix the mistake.
Fix the process that created the mistake.

CTA

What do you think?

#MaithuyELEC
#LucidAI
#HGPTSteel
#DigitalFactory
"""

    def generate_tiktok(self, topic, context=""):
        return f"""
HOOK

{topic}

CONTENT

{context}

CTA

Follow MaithuyELEC.
"""

    def generate_image_prompt(self, topic, context=""):
        return f"""
Ultra realistic industrial photography.

Topic:
{topic}

Knowledge:
{context}

Style:
Clean steel factory.
"""

    def generate_video_prompt(self, topic, context=""):
        return f"""
Create a 30 second cinematic video.

Topic:
{topic}

Knowledge:
{context}

Ending:
HGPT Digital Factory.
"""

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