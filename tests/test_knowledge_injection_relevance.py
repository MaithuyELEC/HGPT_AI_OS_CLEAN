from __future__ import annotations

import unittest

from hgpt_ai_os.intelligence import KnowledgeSearch, TopicAnalyzer
from hgpt_ai_os.knowledge.retrieval_pipeline import KNOWLEDGE_THRESHOLD


def _ids_for(topic: str) -> list[str]:
    analysis = TopicAnalyzer().analyze(topic)
    return [
        result.item.id
        for result in KnowledgeSearch("knowledge").search(analysis, top_k=5)
    ]


def _scores_for(topic: str) -> list[float]:
    analysis = TopicAnalyzer().analyze(topic)
    return [
        result.score
        for result in KnowledgeSearch("knowledge").search(analysis, top_k=5)
    ]


class KnowledgeInjectionRelevanceTests(unittest.TestCase):
    def test_gardening_topic_does_not_inject_steel_knowledge(self):
        ids = _ids_for("Cách chăm sóc mai")

        self.assertEqual(ids, [])

    def test_cooking_topic_does_not_inject_qaqc(self):
        ids = _ids_for("Cách nấu phở")

        self.assertNotIn("QAQC_001", ids)
        self.assertFalse(any(knowledge_id.startswith("QAQC") for knowledge_id in ids))

    def test_pet_topic_does_not_inject_welding(self):
        ids = _ids_for("Nuôi chó Husky")

        self.assertNotIn("WELD_001", ids)
        self.assertEqual(ids, [])

    def test_aws_d11_topic_injects_relevant_knowledge(self):
        ids = _ids_for("AWS D1.1")
        scores = _scores_for("AWS D1.1")

        self.assertIn("QAQC_001", ids)
        self.assertTrue(all(score >= KNOWLEDGE_THRESHOLD for score in scores))

    def test_fitup_topic_injects_relevant_knowledge(self):
        ids = _ids_for("Lỗi Fit-up")
        scores = _scores_for("Lỗi Fit-up")

        self.assertIn("QAQC_001", ids)
        self.assertTrue(all(score >= KNOWLEDGE_THRESHOLD for score in scores))

    def test_tekla_structures_is_data_driven(self):
        ids = _ids_for("Tekla Structures")
        scores = _scores_for("Tekla Structures")

        self.assertTrue(all(score >= KNOWLEDGE_THRESHOLD for score in scores))
        self.assertIsInstance(ids, list)

    def test_future_topics_require_no_code_rules(self):
        topics = (
            "Blockchain",
            "Medicine",
            "Law",
            "Accounting",
            "Marketing",
            "Education",
            "AI",
            "Robotics",
            "Hydraulics",
            "PLC",
        )

        for topic in topics:
            with self.subTest(topic=topic):
                self.assertTrue(
                    all(score >= KNOWLEDGE_THRESHOLD for score in _scores_for(topic))
                )


if __name__ == "__main__":
    unittest.main()
