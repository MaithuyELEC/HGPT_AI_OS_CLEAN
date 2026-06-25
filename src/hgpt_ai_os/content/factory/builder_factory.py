from hgpt_ai_os.content.facebook_builder import FacebookBuilder
from hgpt_ai_os.content.tiktok_builder import TikTokBuilder
from hgpt_ai_os.content.image_builder import ImageBuilder
from hgpt_ai_os.content.video_builder import VideoBuilder


class BuilderFactory:

    _builders = {
        "facebook": FacebookBuilder,
        "tiktok": TikTokBuilder,
        "image": ImageBuilder,
        "video": VideoBuilder,
    }

    @classmethod
    def create(cls, platform: str):
        try:
            return cls._builders[platform.lower()]()
        except KeyError:
            raise ValueError(f"Unknown builder: {platform}")
