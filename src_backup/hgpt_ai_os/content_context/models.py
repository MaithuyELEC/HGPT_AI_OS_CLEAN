from dataclasses import dataclass, field


@dataclass(slots=True)
class ContentContext:
    title: str = ""
    hook: str = ""
    problem: str = ""
    analysis: list[str] = field(default_factory=list)
    solution: str = ""
    lesson: str = ""
    action: str = ""

    hashtags: list[str] = field(default_factory=list)

    image_prompt: str = ""
    video_prompt: str = ""

    metadata: dict = field(default_factory=dict)
