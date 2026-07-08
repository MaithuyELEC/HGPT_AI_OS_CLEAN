from __future__ import annotations

from hgpt_ai_os.content.generator import ContentGenerator
from hgpt_ai_os.topic_engine import TopicIntelligenceEngine
from hgpt_ai_os.topic_engine.topic_parser import TopicParser


def test_topic_parser_supports_vietnamese_keywords_and_phrases():
    parsed = TopicParser().parse("Lỗi rỗ khí mối hàn SAW do flux ẩm")

    assert "rỗ" in parsed.tokens
    assert "khí" in parsed.tokens
    assert "saw" in parsed.tokens
    assert "rỗ khí mối" in parsed.keywords
    assert "do" not in parsed.keywords


def test_topic_engine_extracts_entities_intent_and_context():
    engine = TopicIntelligenceEngine()
    reasoning = engine.reason(
        "SAW porosity do wet flux",
        "Flux must be dry before submerged arc welding.",
    )

    assert reasoning.intent.intent == "Problem"
    assert "SAW" in reasoning.entities.get("Process")
    assert "Porosity" in reasoning.entities.get("Defect")
    assert "Flux" in reasoning.entities.get("Material")
    assert reasoning.knowledge_facts
    assert "wet flux" in " ".join(reasoning.problem.root_cause_candidates).lower()


def test_generator_builtin_path_uses_offline_topic_engine():
    generator = ContentGenerator(ai=None)
    generator.free_desktop_mode = True
    content = generator.generate_facebook(
        "Động cơ máy nén khí quá nhiệt",
        "Motor temperature and current must be recorded during inspection.",
    )

    lowered = content.lower()
    assert "động cơ" in lowered
    assert "quá nhiệt" in lowered
    assert "bằng chứng" in lowered
    assert "retrieved context" not in lowered
    assert "reference notes" not in lowered
