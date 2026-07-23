from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FacebookDNA:
    title_prefix: str = "🚨"
    hook_heading: str = "Powerful emotional Hook"
    explanation_heading: str = "Short technical explanation"
    causes_heading: str = "Root Causes"
    consequences_heading: str = "Consequences"
    actions_heading: str = "Preventive Actions"
    quote_heading: str = "Professional Quote"
    cta_heading: str = "Call To Action"
    hashtags_heading: str = "Industrial Hashtags"

    @property
    def signature(self) -> tuple[str, ...]:
        return (
            self.title_prefix,
            self.hook_heading,
            self.explanation_heading,
            self.causes_heading,
            self.consequences_heading,
            self.actions_heading,
            self.quote_heading,
            self.cta_heading,
            self.hashtags_heading,
        )


@dataclass(frozen=True)
class ImageDNA:
    prompt_1_heading: str = "Prompt 1"
    prompt_1_role: str = "(Hook Image)"
    prompt_2_heading: str = "Prompt 2"
    prompt_2_role: str = "(Engineering Infographic)"
    prompt_3_heading: str = "Prompt 3"
    prompt_3_role: str = "(Facebook Thumbnail)"
    overlay_heading: str = "Text Overlay"

    @property
    def signature(self) -> tuple[str, ...]:
        return (
            self.prompt_1_heading,
            self.prompt_1_role,
            self.prompt_2_heading,
            self.prompt_2_role,
            self.prompt_3_heading,
            self.prompt_3_role,
            self.overlay_heading,
        )


@dataclass(frozen=True)
class VideoDNA:
    prompt_heading: str = "Cinematic Industrial Documentary Prompt"
    overlay_heading: str = "Video Text Overlay"
    aspect_ratio_heading: str = "Aspect Ratio"
    camera_heading: str = "Camera"
    lighting_heading: str = "Lighting"
    color_heading: str = "Color"
    style_heading: str = "Style"

    @property
    def signature(self) -> tuple[str, ...]:
        return (
            self.prompt_heading,
            self.overlay_heading,
            self.aspect_ratio_heading,
            self.camera_heading,
            self.lighting_heading,
            self.color_heading,
            self.style_heading,
        )


FACEBOOK_DNA = FacebookDNA()
IMAGE_DNA = ImageDNA()
VIDEO_DNA = VideoDNA()
