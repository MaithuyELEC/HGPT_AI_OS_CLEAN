from __future__ import annotations

from typing import Protocol

from hgpt_ai_os.content_brain.content_dna import IMAGE_DNA


class ImageTopic(Protocol):
    topic: str
    domain: str
    subject: str
    problem: str
    objects: tuple[str, ...]
    risks: tuple[str, ...]
    causes: tuple[str, ...]
    actions: tuple[str, ...]
    signs: tuple[str, ...]


def render_image_prompt(topic: ImageTopic) -> str:
    dna = IMAGE_DNA
    if _is_saw(topic.topic):
        return _render_saw_image_prompt(topic, dna)
    return "\n".join(
        [
            dna.prompt_1_heading,
            dna.prompt_1_role,
            (
                f"Professional industrial photography, vertical 4:5 frame. Show {topic.topic} at the exact moment "
                f"the first warning sign appears: {topic.signs[0]}. A Vietnamese field engineer in full PPE pauses the work, "
                f"keeps a safe distance from {topic.objects[0]}, and frames the evidence with a gauge, checklist, and camera. "
                "The image must feel like real factory documentation, emotional but disciplined, sharp metal texture, readable body language, no staged office look."
            ),
            "",
            dna.prompt_2_heading,
            dna.prompt_2_role,
            (
                f"Professional engineering infographic for {topic.topic}, clean industrial layout, dark factory background with technical overlay panels. "
                f"Show four fixed blocks: visible signs ({_join(topic.signs[:3])}), cause chain ({_join(topic.causes[:3])}), "
                f"inspection points ({_join(topic.objects[:4])}), and practical prevention ({_join(topic.actions[:4])}). "
                "Use precise line icons, measurement callouts, warning color accents, steel texture, controlled spacing, and no fake brand marks."
            ),
            "",
            dna.prompt_3_heading,
            dna.prompt_3_role,
            (
                f"Professional Facebook thumbnail, 16:9 industrial documentary style. Foreground: engineer holding a measurement tool beside {topic.objects[0]}. "
                f"Background: steel workshop, controlled work zone, visible clue of {topic.signs[0]}, strong depth, high contrast, realistic PPE. "
                "Leave clean negative space for a short overlay, serious practical mood, urgent but not sensational."
            ),
            "",
            dna.overlay_heading,
            f"{_overlay(topic.topic)}",
        ]
    )


def _join(values: tuple[str, ...]) -> str:
    return ", ".join(values)


def _render_saw_image_prompt(topic: ImageTopic, dna) -> str:
    return "\n".join(
        [
            dna.prompt_1_heading,
            dna.prompt_1_role,
            (
                "Professional industrial photography prompt for Gemini image generation. Real steel fabrication workshop, SAW welding on a large H-beam, "
                "macro close-up of a weld seam with visible porosity on the surface, welding arc glowing under granular flux, controlled sparks, smoke haze, "
                "inspector using UT equipment beside the welded beam, realistic PPE, cinematic orange welding light mixed with steel-blue factory light, "
                "photorealistic engineering documentary style, HDR, volumetric lighting, high-detail steel texture, sharp focus, premium industrial atmosphere. "
                "No cartoon, no illustration, no fake text, no office scene, no generic maintenance checklist."
            ),
            "",
            dna.overlay_heading,
            "🚨 ĐƯỜNG HÀN SAW BỊ RỖ KHÍ",
            "“Một lỗi nhỏ – Hậu quả rất lớn”",
            "",
            dna.prompt_2_heading,
            dna.prompt_2_role,
            (
                "Professional engineering infographic prompt. Show a cutaway cross-section of a SAW weld on structural steel with internal gas pores clearly visible inside the weld metal. "
                "Use clean educational technical presentation, metallic texture, subtle blue-gray background, precise arrows pointing to porosity, small concise Vietnamese labels only, "
                "high clarity, high-detail steel material, no paragraph-sized text inside the generated image, no clutter, no cartoon, no decorative unrelated icons."
            ),
            "",
            dna.prompt_3_heading,
            dna.prompt_3_role,
            (
                "Professional Facebook thumbnail prompt. Extreme close-up of a SAW weld bead with obvious porosity, red warning symbol, industrial steel workshop in the background, "
                "controlled sparks and welding-orange glow, high contrast, sharp photorealistic engineering photography, clean negative space for a short headline, serious urgent mood, "
                "no sensational disaster, no cartoon, no fake brand, no distorted text."
            ),
            "",
            dna.overlay_heading,
            "❌ ĐỪNG ĐỂ RỖ KHÍ PHÁ HỎNG CẢ CÔNG TRÌNH!",
        ]
    )


def _overlay(topic: str) -> str:
    clean = " ".join((topic or "Technical issue").split())
    if len(clean) <= 34:
        return f"STOP & CHECK: {clean.upper()}"
    return f"STOP & CHECK: {clean[:31].upper()}..."


def _is_saw(topic: str) -> bool:
    return "saw" in _ascii(topic) and "ro khi" in _ascii(topic)


def _ascii(value: str) -> str:
    import re
    import unicodedata

    decomposed = unicodedata.normalize("NFD", (value or "").lower())
    no_marks = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    no_marks = no_marks.replace("đ", "d")
    return re.sub(r"[^a-z0-9]+", " ", no_marks).strip()
