from __future__ import annotations

import unittest

from hgpt_ai_os.topic_engine import TopicIntelligenceEngine


class UniversalContentIntelligenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = TopicIntelligenceEngine()

    def test_5s_steel_topic_routes_to_improvement_not_fault_diagnosis(self) -> None:
        context = self.engine.analyze("5S trong xưởng sản xuất kết cấu thép")

        self.assertEqual(context.domain_family, "LEAN_KAIZEN_5S_TPM")
        self.assertIn("STRUCTURAL_STEEL", context.secondary_domains)
        self.assertEqual(context.topic_intent, "IMPROVEMENT")
        self.assertEqual(context.topic_nature, "managerial")
        self.assertFalse(context.failures)
        self.assertGreaterEqual(dict(context.domain_scores)["LEAN_KAIZEN_5S_TPM"], 0.3)

    def test_bearing_noise_routes_to_maintenance_diagnosis_with_evidence_gaps(self) -> None:
        context = self.engine.analyze("Vòng bi động cơ bị kêu")

        self.assertEqual(context.domain_family, "EQUIPMENT_MAINTENANCE")
        self.assertIn("ELECTRICAL_MAINTENANCE", context.secondary_domains)
        self.assertIn(context.topic_intent, {"DIAGNOSE", "TROUBLESHOOT"})
        self.assertIn("user topic", context.available_evidence)
        self.assertIn("model/OEM details", context.missing_evidence)
        self.assertIn("site photos or measured evidence", context.missing_evidence)

    def test_general_life_topic_is_supported_by_universal_router(self) -> None:
        context = self.engine.analyze("Cách chăm sóc mai")

        self.assertEqual(context.domain_family, "GENERAL_LIFE")
        self.assertEqual(context.topic_nature, "general-life")
        self.assertEqual(context.topic_intent, "GENERAL_GUIDANCE")
        self.assertEqual(context.risk_level, "Low")


if __name__ == "__main__":
    unittest.main()
