from __future__ import annotations

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
            assert "#Motor" in second or "#Dong" in second
        else:
            assert topic_b in second or "động cơ" in second.lower()


def test_static_hashtags_are_kept_with_topic_specific_hashtags():
    content = BuilderFactory.create("hashtags").build("5S trong xưởng sản xuất kết cấu thép")

    for tag in (
        "#MaithuyELEC",
        "#LucidAuto",
        "#HGPTSteel",
        "#SteelKnowledgeBase",
        "#DigitalFactory",
        "#5S",
        "#Kaizen",
    ):
        assert tag in content
