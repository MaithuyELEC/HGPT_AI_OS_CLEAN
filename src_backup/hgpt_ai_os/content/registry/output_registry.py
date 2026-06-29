class OutputRegistry:

    _mapping = {
        "facebook": "facebook.docx",
        "tiktok": "tiktok.docx",
        "image": "image_prompt.docx",
        "video": "video_prompt.docx",
        "seo": "seo.docx",
        "hashtags": "hashtags.docx",
        "approval": "approval_checklist.docx",
    }

    @classmethod
    def filename(cls, platform: str):
        try:
            return cls._mapping[platform.lower()]
        except KeyError:
            raise ValueError(f"Unknown platform: {platform}")
