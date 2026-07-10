from __future__ import annotations

import re

from hgpt_ai_os.content.factory.builder_factory import BuilderFactory


def _build_all(topic: str) -> dict[str, str]:
    return {
        key: BuilderFactory.create(key).build(topic)
        for key in (
            "facebook",
            "tiktok",
            "video",
            "image",
            "seo",
            "hashtags",
            "approval",
        )
    }


def _joined(outputs: dict[str, str]) -> str:
    return "\n".join(outputs.values()).lower()


def test_5s_topic_generates_workshop_specific_content_without_unrelated_defects():
    outputs = _build_all("5S trong xưởng sản xuất kết cấu thép")
    body = _joined(outputs)

    assert "5s" in body
    assert "xưởng" in body
    assert "kết cấu thép" in body
    assert "an toàn" in body or "năng suất" in body
    assert "vật tư" in body
    assert "phôi thép" in body
    assert "rỗ khí" not in body
    assert "động cơ quá nhiệt" not in body


def test_mig_porosity_topic_generates_welding_content_without_5s_generic_content():
    outputs = _build_all("Lỗi rỗ khí mối hàn MIG")
    body = _joined(outputs)

    assert "rỗ khí" in body
    assert "mối hàn" in body
    assert "nguyên nhân" in body
    assert "mig" in body
    assert "5s" not in body
    assert "5s trong xưởng" not in body
    assert "shadow board" not in body


def test_compressor_motor_overheat_topic_generates_maintenance_content():
    outputs = _build_all("Động cơ máy nén khí quá nhiệt")
    body = _joined(outputs)

    assert "động cơ" in body
    assert "quá nhiệt" in body
    assert "bảo trì" in body
    assert "máy nén khí" in body
    assert "fit-up" not in body


def test_facebook_has_required_topic_aware_sections():
    content = BuilderFactory.create("facebook").build("5S trong xưởng sản xuất kết cấu thép")

    for section in (
        "Hook:",
        "Vấn đề:",
        "Dấu hiệu nhận biết:",
        "Nguyên nhân gốc:",
        "Giải pháp:",
        "Điều học được:",
        "Hành động:",
        "Hashtags:",
    ):
        assert section in content


def test_each_output_type_uses_a_distinct_topic_specific_body():
    topic_a = "5S trong xưởng sản xuất kết cấu thép"
    topic_b = "Động cơ máy nén khí quá nhiệt"

    for key in ("facebook", "tiktok", "video", "image", "seo", "hashtags", "approval"):
        first = BuilderFactory.create(key).build(topic_a)
        second = BuilderFactory.create(key).build(topic_b)

        assert first != second
        assert topic_a in first or "5S" in first
        if key == "hashtags":
            assert "#DongCo" in second
        else:
            assert topic_b in second or "động cơ" in second.lower()


def test_static_hashtags_are_kept_with_topic_specific_hashtags():
    content = BuilderFactory.create("hashtags").build("5S trong xưởng sản xuất kết cấu thép")

    for tag in (
        "#MaithuyELEC",
        "#LucidAuto",
        "#KetCauThep",
        "#KienThucXuong",
        "#NhaMaySo",
        "#5S",
        "#Kaizen",
    ):
        assert tag in content


def test_release_output_contracts_are_independent_without_sentence_reuse():
    topics = (
        "Nuôi ong lấy mật",
        "Cách mở quán cà phê",
        "Bảo trì cầu trục trong nhà máy",
    )
    channels = ("facebook", "tiktok", "video", "image", "seo")

    for topic in topics:
        outputs = {key: BuilderFactory.create(key).build(topic) for key in channels}

        assert outputs["facebook"] != outputs["tiktok"]
        assert outputs["tiktok"] != outputs["video"]
        assert outputs["video"] != outputs["seo"]
        assert outputs["seo"] != outputs["facebook"]
        assert all(outputs["image"] != body for key, body in outputs.items() if key != "image")

        for label in (
            "Title:",
            "Hook:",
            "Pain:",
            "Story:",
            "Knowledge:",
            "Practical actions:",
            "Question:",
            "CTA:",
            "Hashtags:",
        ):
            assert label in outputs["facebook"]
        assert "Người đọc" not in outputs["facebook"]
        assert "Chủ đề thuộc" not in outputs["facebook"]

        for label in ("Hook", "Curiosity", "Pain", "Truth", "One practical tip", "CTA"):
            assert label in outputs["tiktok"]
        assert 120 <= len(outputs["tiktok"].split()) <= 220
        for forbidden in ("Scene", "Camera", "Storyboard", "Lighting", "Cảnh", "Góc máy"):
            assert forbidden not in outputs["tiktok"]

        image_lines = [line.strip() for line in outputs["image"].splitlines() if line.strip()]
        assert [line.split(":", 1)[0] for line in image_lines] == [
            "Chủ thể",
            "Bối cảnh",
            "Hành động",
            "Trang phục",
            "Ánh sáng",
            "Góc máy",
            "Ống kính",
            "Màu sắc",
            "Chi tiết cần có",
            "Chi tiết cần tránh",
            "Phong cách",
            "Tỷ lệ",
        ]

        for label in (
            "Tiêu đề:",
            "Mở đầu:",
            "Cảnh 1:",
            "Cảnh 2:",
            "Cảnh 3:",
            "Góc máy:",
            "Ánh sáng:",
            "Lời thoại:",
            "Phụ đề:",
            "Âm thanh:",
            "Kết thúc:",
            "CTA:",
        ):
            assert label in outputs["video"]

        for label in ("Title:", "Meta:", "Keywords:", "Outline:", "FAQ:", "Conclusion:"):
            assert label in outputs["seo"]

        seen_sentences: dict[str, str] = {}
        for channel, body in outputs.items():
            for sentence in _sentences(body):
                owner = seen_sentences.setdefault(sentence, channel)
                assert owner == channel, f"sentence reused by {owner} and {channel}: {sentence}"


def _sentences(body: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", body)
    parts = re.split(r"(?<=[.!?])\s+|\n+", normalized)
    sentences = []
    for part in parts:
        sentence = part.strip(" -")
        if len(sentence.split()) >= 6:
            sentences.append(sentence.lower())
    return sentences
