from hgpt_ai_os.content.facebook_builder import FacebookBuilder
from hgpt_ai_os.content.tiktok_builder import TikTokBuilder
from hgpt_ai_os.content.image_builder import ImageBuilder
from hgpt_ai_os.content.video_builder import VideoBuilder
from hgpt_ai_os.content.seo_builder import SeoBuilder
from hgpt_ai_os.content.hashtag_builder import HashtagBuilder
from hgpt_ai_os.content.approval_builder import ApprovalBuilder
from hgpt_ai_os.content.factory.topic_aware import TopicAwareBuiltInBuilder


class BuilderFactory:

    _builders = {
        "facebook": lambda: TopicAwareBuiltInBuilder("facebook"),
        "tiktok": lambda: TopicAwareBuiltInBuilder("tiktok"),
        "image": lambda: TopicAwareBuiltInBuilder("image"),
        "video": lambda: TopicAwareBuiltInBuilder("video"),
        "seo": lambda: TopicAwareBuiltInBuilder("seo"),
        "hashtags": lambda: TopicAwareBuiltInBuilder("hashtags"),
        "approval": lambda: TopicAwareBuiltInBuilder("approval"),
    }

    _legacy_builders = {
        "facebook": FacebookBuilder,
        "tiktok": TikTokBuilder,
        "image": ImageBuilder,
        "video": VideoBuilder,
        "seo": SeoBuilder,
        "hashtags": HashtagBuilder,
        "approval": ApprovalBuilder,
    }

    @classmethod
    def create(cls, platform: str):
        try:
            return cls._builders[platform.lower()]()
        except KeyError:
            raise ValueError(f"Unknown builder: {platform}")
