from __future__ import annotations

import re

from hgpt_ai_os.content.export.docx_exporter import DocxExporter
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
        "Hook",
        "Real shop scenario",
        "Root cause analysis",
        "Practical solution",
        "Lesson learned",
        "Call To Action",
    ):
        assert section in content


def test_general_facebook_uses_domain_writer_sections_not_template_sections():
    content = BuilderFactory.create("facebook").build("Mai")

    for section in (
        "Mở bài",
        "Bối cảnh",
        "Điều cần hiểu",
        "Cách làm",
        "Sai lầm thường gặp",
        "Kết lại",
        "Lời mời",
    ):
        assert section in content

    for label in (
        "Introduction",
        "Main knowledge",
        "Step-by-step actions",
        "Practical advice",
        "Conclusion",
    ):
        assert label not in content


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
        "#LucidAIStudio",
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

        expected_general = topic != "Bảo trì cầu trục trong nhà máy"
        if expected_general:
            for label in (
                "Mở bài",
                "Bối cảnh",
                "Điều cần hiểu",
                "Cách làm",
                "Sai lầm thường gặp",
                "Kết lại",
                "Lời mời",
            ):
                assert label in outputs["facebook"]
            for label in (
                "Introduction",
                "Main knowledge",
                "Step-by-step actions",
                "Practical advice",
                "Conclusion",
            ):
                assert label not in outputs["facebook"]
        else:
            for label in (
                "Hook",
                "Real shop scenario",
                "Root cause analysis",
                "Practical solution",
                "Lesson learned",
                "Call To Action",
            ):
                assert label in outputs["facebook"]
            for label in (
                "Introduction",
                "Main knowledge",
                "Step-by-step actions",
                "Practical advice",
                "Common mistakes",
                "Conclusion",
            ):
                assert label not in outputs["facebook"]
        assert "Người đọc" not in outputs["facebook"]
        assert "Chủ đề thuộc" not in outputs["facebook"]

        expected_tiktok_labels = (
            ("Mở đầu", "Gây chú ý", "Nội dung chính", "Điểm nhớ", "Kết thúc")
            if expected_general
            else ("Mở đầu", "Khơi mở kiến thức", "Điểm cần tránh", "Cách làm đúng", "Gợi ý áp dụng", "Kết thúc")
        )
        for label in expected_tiktok_labels:
            assert label in outputs["tiktok"]
        for forbidden in ("Hook", "Curiosity", "Pain", "Truth", "One practical tip", "CTA"):
            assert forbidden not in outputs["tiktok"]
        assert 120 <= len(outputs["tiktok"].split()) <= 220
        for forbidden in ("Scene", "Camera", "Storyboard", "Lighting", "Cảnh", "Góc máy"):
            assert forbidden not in outputs["tiktok"]

        image_lines = [line.strip() for line in outputs["image"].splitlines() if line.strip()]
        if expected_general:
            image_labels = [line.split(" - ", 1)[0] for line in image_lines]
            assert image_labels[0].startswith("Prompt Gemini tạo ảnh:")
            assert image_labels[1:] == [
                "Chủ thể",
                "Bối cảnh",
                "Hành động",
                "Bố cục",
                "Ánh sáng",
                "Góc quay",
                "Ống kính",
                "Chất liệu",
                "Màu sắc",
                "Cảm xúc",
                "Chi tiết cần tránh",
                "Tỷ lệ khung hình",
                "Chất lượng",
            ]
            for label in ("Prompt Veo tạo video", "Cảnh một -", "Cảnh hai -", "Cảnh ba -", "Lời thoại -", "Kết thúc -"):
                assert label in outputs["video"]
        else:
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
                "Cảnh 1 - Hook:",
                "Cảnh 2 - Failure:",
                "Cảnh 3 - Diagnosis:",
                "Cảnh 4 - Repair:",
                "Cảnh 5 - Result:",
                "Góc máy:",
                "Ánh sáng:",
                "Phụ đề:",
                "Âm thanh:",
                "Kết thúc:",
                "Kêu gọi hành động:",
            ):
                assert label in outputs["video"]

        seo_labels = (
            ("Tiêu đề SEO:", "Mô tả tìm kiếm:", "Từ khóa chính", "Dàn ý bài viết", "Câu hỏi thường gặp")
            if expected_general
            else ("H1:", "Introduction", "H2:", "FAQ", "Summary")
        )
        for label in seo_labels:
            assert label in outputs["seo"]

        seen_sentences: dict[str, str] = {}
        for channel, body in outputs.items():
            for sentence in _sentences(body):
                owner = seen_sentences.setdefault(sentence, channel)
                assert owner == channel, f"sentence reused by {owner} and {channel}: {sentence}"


def test_general_topics_export_all_outputs_without_legacy_template_labels():
    exporter = DocxExporter()
    topics = ("Mai", "Japanese N5", "Coffee", "Husky", "Cooking", "Travel", "Finance")
    channels = ("facebook", "tiktok", "seo", "image", "video", "hashtags", "approval")
    forbidden = (
        "Introduction",
        "Main knowledge",
        "Step-by-step actions",
        "Practical advice",
        "Common mistakes",
        "Conclusion",
        "Hook:",
        "Story:",
        "Pain:",
        "Truth:",
        "CTA:",
        "Curiosity:",
        "Practical actions:",
    )

    for topic in topics:
        outputs = {key: BuilderFactory.create(key).build(topic) for key in channels}
        assert set(outputs) == set(channels)

        for channel, body in outputs.items():
            exporter.validate_content(body)
            for label in forbidden:
                assert label not in body, f"{topic} {channel} leaked {label}"


def _sentences(body: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", body)
    parts = re.split(r"(?<=[.!?])\s+|\n+", normalized)
    sentences = []
    for part in parts:
        sentence = part.strip(" -")
        if len(sentence.split()) >= 6:
            sentences.append(sentence.lower())
    return sentences
