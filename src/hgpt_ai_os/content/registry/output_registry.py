class OutputRegistry:

    _mapping = {
        "facebook": "facebook.docx",
        "tiktok": "tiktok.docx",
        "image": "image_prompt.docx",
        "video": "video_prompt.docx",
    }

    @classmethod
    def filename(cls, platform: str) -> str:
        try:
            return cls._mapping[platform.lower()]
        except KeyError:
            raise ValueError(f"Unknown platform: {platform}")
