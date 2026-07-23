from __future__ import annotations

from typing import Protocol

from hgpt_ai_os.content_brain.content_dna import VIDEO_DNA


class VideoTopic(Protocol):
    topic: str
    domain: str
    subject: str
    problem: str
    objects: tuple[str, ...]
    risks: tuple[str, ...]
    causes: tuple[str, ...]
    actions: tuple[str, ...]
    signs: tuple[str, ...]


def render_video_prompt(topic: VideoTopic) -> str:
    dna = VIDEO_DNA
    if _is_saw(topic.topic):
        return _render_saw_video_prompt(topic, dna)
    return "\n".join(
        [
            dna.prompt_heading,
            (
                f"Create one continuous 45-60 second cinematic industrial documentary shot about {topic.topic}. "
                f"The camera enters a Vietnamese steel workshop where {topic.signs[0]} is visible on {topic.objects[0]}. "
                f"A field engineer in full PPE pauses the operation, protects the work area, checks {_join(topic.objects[:4])}, "
                f"and explains through action that {topic.problem}. The motion continues naturally as the engineer performs {topic.actions[0]}, "
                f"compares evidence against {_join(topic.causes[:2])}, records the finding, and hands the area back only after the result is visibly confirmed. "
                "The film must feel like a premium industrial documentary: serious, human, technical, grounded in real factory evidence, with no numbered scene structure and no slideshow rhythm."
            ),
            "",
            dna.overlay_heading,
            "DUNG - DO - XU LY - XAC NHAN",
            f"Secondary caption: {_caption(topic.topic)}",
            "",
            dna.aspect_ratio_heading,
            "9:16 vertical for Reels and Shorts, with safe center framing for social cropping.",
            "",
            dna.camera_heading,
            (
                "Cinematic handheld-stable movement, slow push through steel columns, over-the-shoulder inspection angle, macro focus on evidence, "
                "controlled pullback to show engineer, equipment, and checklist in one frame."
            ),
            "",
            dna.lighting_heading,
            (
                "Practical high-bay factory light, focused inspection lamp on the defect, readable PPE and metal texture, controlled contrast, no theatrical neon."
            ),
            "",
            dna.color_heading,
            (
                "Natural industrial palette: painted steel, worn concrete, dark uniforms, yellow safety markings, red lockout tag, "
                "cool gray machinery, warm skin tones, and clean white checklist paper. Avoid one-color grading and oversaturated effects."
            ),
            "",
            dna.style_heading,
            (
                "Photorealistic field documentation, cinematic but grounded, handheld-stable movement, realistic factory ambience, "
                "subtle dust and ventilation, no fake sparks, no disaster imagery, no segmented scene list, no cartoon, no watermark, no unsafe body position, and no missing PPE."
            ),
        ]
    )


def _join(values: tuple[str, ...]) -> str:
    return ", ".join(values)


def _render_saw_video_prompt(topic: VideoTopic, dna) -> str:
    return "\n".join(
        [
            dna.prompt_heading,
            (
                "Create one coherent 30-second cinematic Gemini/Veo directing prompt in a premium steel-fabrication environment. "
                "Begin with an extreme macro shot of a visually perfect SAW weld bead on a large H-beam under factory lighting. "
                "Use a slow dolly move and rack focus from the smooth weld surface into a cutaway reveal of the internal weld metal, where hidden gas porosity is illuminated clearly. "
                "Show the pores as small trapped gas cavities inside the weld, then visualize stress concentration and crack-development risk with subtle engineering overlays, not unrealistic disaster imagery. "
                "Transition through the real causes: wet flux being handled incorrectly, rusty or contaminated steel surface, oxidized welding wire, unstable arc under flux, and incorrect current, voltage, or travel speed on the WPS parameter sheet. "
                "Then move into disciplined prevention in the shop: drying flux in an oven, cleaning steel before welding, checking welding wire condition, verifying WPS parameters, QA/QC inspection with UT/RT context, and stable SAW welding under a proper flux blanket. "
                "Finish with a clean, defect-free SAW weld bead under volumetric factory light and the message that quality comes from process, discipline, and responsibility. "
                "Visual style: photorealistic industrial documentary, macro close-up, controlled camera movement, rack focus, slow-motion sparks where appropriate, HDR, volumetric factory light, steel-blue and welding-orange palette, real PPE, real SAW equipment, no cartoon, no slideshow, no generic office scene, no unsafe action."
            ),
            "",
            dna.overlay_heading,
            "0–3s: 🚨 Đường hàn SAW bị rỗ khí!",
            "3–8s: Một lỗi nhỏ... Có thể khiến cả kết cấu phải sửa chữa.",
            "8–15s: Nguyên nhân: • Thuốc hàn ẩm • Thép bẩn • Dây hàn oxy hóa • Sai thông số hàn",
            "15–23s: Hậu quả: ❌ Không đạt UT ❌ Không đạt RT ❌ Giảm khả năng chịu lực ❌ Tăng chi phí sửa chữa",
            "23–30s: Chất lượng không đến từ may mắn. Chất lượng đến từ quy trình, kỷ luật và trách nhiệm.",
            "",
            dna.aspect_ratio_heading,
            "9:16 vertical for Reels, Shorts, and mobile-first social video; keep all key weld details centered for safe cropping.",
            "",
            dna.camera_heading,
            "Extreme macro lens, slow dolly movement, rack focus from weld surface to internal porosity, controlled cutaway reveal, final stable hero shot of defect-free weld.",
            "",
            dna.lighting_heading,
            "Volumetric factory light, welding-orange glow under flux, steel-blue ambient shop light, HDR highlights on weld bead and H-beam texture.",
            "",
            dna.color_heading,
            "Steel-blue, welding-orange, dark graphite, hot amber sparks, realistic metal gray, clean white inspection overlays.",
            "",
            dna.style_heading,
            "Premium photorealistic industrial documentary, high-detail steel texture, realistic PPE and SAW equipment, serious engineering tone, no cartoon, no slideshow, no exaggerated explosion, no generic office scene.",
        ]
    )


def _caption(topic: str) -> str:
    clean = " ".join((topic or "technical inspection").split())
    return clean[:58]


def _is_saw(topic: str) -> bool:
    return "saw" in _ascii(topic) and "ro khi" in _ascii(topic)


def _ascii(value: str) -> str:
    import re
    import unicodedata

    decomposed = unicodedata.normalize("NFD", (value or "").lower())
    no_marks = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    no_marks = no_marks.replace("đ", "d")
    return re.sub(r"[^a-z0-9]+", " ", no_marks).strip()
