from __future__ import annotations

import unittest
from difflib import SequenceMatcher

from hgpt_ai_os.content.generator import ContentGenerator
from hgpt_ai_os.topic_engine import TopicIntelligenceEngine
from hgpt_ai_os.topic_engine.topic_parser import TopicParser


class TopicEngineTests(unittest.TestCase):
    def test_topic_parser_supports_vietnamese_keywords_and_phrases(self):
        parsed = TopicParser().parse("Lỗi rỗ khí mối hàn SAW do flux ẩm")

        self.assertIn("rỗ", parsed.tokens)
        self.assertIn("khí", parsed.tokens)
        self.assertIn("saw", parsed.tokens)
        self.assertIn("rỗ khí mối", parsed.keywords)
        self.assertNotIn("do", parsed.keywords)

    def test_topic_engine_extracts_entities_intent_and_context(self):
        engine = TopicIntelligenceEngine()
        reasoning = engine.reason(
            "SAW porosity do wet flux",
            "Flux must be dry before submerged arc welding.",
        )

        self.assertEqual(reasoning.intent.intent, "Problem")
        self.assertIn("SAW", reasoning.entities.get("Process"))
        self.assertIn("Porosity", reasoning.entities.get("Defect"))
        self.assertIn("Flux", reasoning.entities.get("Material"))
        self.assertTrue(reasoning.knowledge_facts)
        self.assertIn("wet flux", " ".join(reasoning.problem.root_cause_candidates).lower())
        self.assertTrue(reasoning.problem.immediate_cause)
        self.assertTrue(reasoning.problem.hidden_cause)
        self.assertTrue(reasoning.problem.root_cause)
        self.assertTrue(reasoning.possible_mechanisms)
        self.assertTrue(reasoning.corrective_actions)
        self.assertTrue(reasoning.preventive_actions)

    def test_topic_engine_extracts_vietnamese_multiword_engineering_entities(self):
        reasoning = TopicIntelligenceEngine().reason("Máy mài cầm tay hỏng liên tục")

        self.assertIn("angle grinder", reasoning.entities.get("Tool"))
        self.assertIn("continuous breakdown", reasoning.entities.get("Failure"))
        self.assertIn("Grinding", reasoning.entities.get("Process"))

    def test_offline_writers_produce_distinct_topic_specific_bodies(self):
        engine = TopicIntelligenceEngine()
        topics = (
            "Đường hàn SAW bị rỗ khí",
            "Máy mài cầm tay hỏng liên tục",
            "5S khu vực máy cắt Laser",
            "Lỗi bong tróc sơn",
        )

        facebook = [engine.generate(topic, "facebook") for topic in topics]
        seo = [engine.generate(topic, "seo") for topic in topics]
        checklists = [engine.generate(topic, "checklist") for topic in topics]

        for body in facebook:
            for section in (
                "Hook:",
                "Pain Point:",
                "Symptoms:",
                "Engineering Analysis:",
                "Root Cause:",
                "Corrective Action:",
                "Preventive Action:",
                "Lesson Learned:",
                "CTA:",
            ):
                self.assertIn(section, body)

        for body in seo:
            for section in (
                "Introduction",
                "Technical Analysis",
                "Root Cause",
                "Engineering Solution",
                "Preventive Maintenance",
                "Conclusion",
            ):
                self.assertIn(section, body)

        saw_checklist = checklists[0]
        for item in ("Flux", "Wire", "Voltage", "Current", "Travel Speed", "Stickout", "Plate Cleanliness", "Flux Depth", "Repair", "Inspection"):
            self.assertIn(item, saw_checklist)

        maintenance_checklist = checklists[1]
        for item in ("Bearing", "Motor", "Lubrication", "Alignment", "Vibration", "Temperature", "Fastener", "Noise"):
            self.assertIn(item, maintenance_checklist)

        self.assertLess(_max_similarity(facebook), 0.72)
        self.assertLess(_max_similarity(seo), 0.72)
        self.assertLess(_max_similarity(checklists), 0.78)

    def test_generator_builtin_path_uses_offline_topic_engine(self):
        generator = ContentGenerator(ai=None)
        generator.free_desktop_mode = True
        content = generator.generate_facebook(
            "Động cơ máy nén khí quá nhiệt",
            "Motor temperature and current must be recorded during inspection.",
        )

        lowered = content.lower()
        self.assertIn("động cơ", lowered)
        self.assertIn("quá nhiệt", lowered)
        self.assertIn("bằng chứng", lowered)
        self.assertNotIn("retrieved context", lowered)
        self.assertNotIn("reference notes", lowered)


def _max_similarity(values: list[str]) -> float:
    scores = []
    for left_index, left in enumerate(values):
        for right in values[left_index + 1 :]:
            scores.append(SequenceMatcher(None, left, right).ratio())
    return max(scores)


if __name__ == "__main__":
    unittest.main()
