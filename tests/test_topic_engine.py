from __future__ import annotations

import json
import unittest
from difflib import SequenceMatcher
from pathlib import Path

from hgpt_ai_os.content.generator import ContentGenerator
from hgpt_ai_os.content.factory.builder_factory import BuilderFactory
from hgpt_ai_os.topic_engine.failure_intelligence import (
    FailureIntelligenceLibrary,
    REQUIRED_FAILURE_FIELDS,
)
from hgpt_ai_os.topic_engine.engineering_knowledge_library import (
    EngineeringKnowledgeLibrary,
    KNOWLEDGE_CONTRACT_FIELDS,
)
from hgpt_ai_os.topic_engine import TopicIntelligenceEngine
from hgpt_ai_os.topic_engine.writers.channel_writer import match_playbook
from hgpt_ai_os.topic_engine.topic_parser import TopicParser


FORBIDDEN_OUTPUT_PATTERNS = (
    "Problem:",
    "Evidence:",
    "Most probable cause:",
    "Recommended verification:",
    "can trigger",
    "Immediate trigger:",
    "Hidden layer:",
)

ENGINEERING_V2_SECTIONS = (
    "Mô tả sự cố",
    "Nguyên lý kỹ thuật",
    "Cơ chế hư hỏng",
    "Dạng hư hỏng",
    "Phân tích nguyên nhân gốc",
    "Phân tích 5 Vì sao",
    "Quy trình kiểm tra",
    "Dụng cụ cần chuẩn bị",
    "Đo kiểm",
    "Tiêu chí nghiệm thu",
    "Tiêu chuẩn áp dụng",
    "Quy trình sửa chữa",
    "Xác minh sau sửa",
    "Bảo trì phòng ngừa",
    "Bài học kinh nghiệm",
    "Sai lầm thường gặp",
    "Kaizen",
    "Hành động quản lý",
    "Đề xuất Digital Factory",
)

ROOT_CAUSE_FIELDS = (
    "Dấu hiệu nhận biết:",
    "Phương pháp kiểm tra:",
    "Đo kiểm:",
    "Dụng cụ:",
    "Tiêu chí kết luận:",
    "Hành động khắc phục:",
    "Phòng ngừa tái diễn:",
)

RAW_FAILURE_INTELLIGENCE_PHRASES = (
    "broken wires count and location",
    "rope diameter measurement",
    "sheave groove condition",
    "drum groove",
    "release inspection",
    "load test according to",
    "no-load functional test",
    "working load limit",
    "anchor point",
    "alignment",
    "wear",
    "lubrication",
    "corrosion",
    "fatigue",
)

FAILURE_LIBRARY_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "hgpt_ai_os"
    / "topic_engine"
    / "failure_intelligence_library.json"
)


class TopicEngineTests(unittest.TestCase):
    def test_failure_intelligence_library_profiles_have_required_fields(self):
        library = FailureIntelligenceLibrary()

        for key in (
            "WIRE_ROPE_FAILURE",
            "MOTOR_BURNOUT",
            "VFD_OVERCURRENT",
            "PLC_FAULT",
            "SAW_POROSITY",
            "HYDRAULIC_LEAK",
            "BEARING_FAILURE",
            "GEARBOX_FAILURE",
        ):
            with self.subTest(key=key):
                profile = library.get(key)
                self.assertIsNotNone(profile)
                context = profile.as_context()
                for field in REQUIRED_FAILURE_FIELDS:
                    self.assertTrue(context[field], field)

    def test_release_v1_failure_library_is_expanded_for_engineering_platform(self):
        library = FailureIntelligenceLibrary()
        required_profiles = (
            "WELD_SLAG_INCLUSION",
            "WELD_LACK_OF_FUSION",
            "WELD_LACK_OF_PENETRATION",
            "WELD_UNDERCUT",
            "WELD_OVERLAP",
            "WELD_CRACK",
            "WELD_ARC_BLOW",
            "WELD_BURN_THROUGH",
            "WELD_DISTORTION",
            "WELD_SPATTER",
            "WELD_UNDERFILL",
            "WELD_EXCESS_REINFORCEMENT",
            "PUMP_CAVITATION",
            "COMPRESSOR_OVERHEAT",
            "ANCHOR_BOLT_MISLOCATION",
        )

        self.assertGreaterEqual(len(library.profiles), 23)
        for key in required_profiles:
            with self.subTest(key=key):
                profile = library.get(key)
                self.assertIsNotNone(profile)
                context = profile.as_context()
                for field in (
                    "failure_mechanism",
                    "measurements",
                    "engineering_calculation",
                    "engineering_notes",
                    "common_mistakes",
                    "lessons_learned",
                    "standards",
                ):
                    self.assertTrue(context[field], field)

    def test_release_v1_general_life_topics_return_engineering_scope_notice(self):
        for topic in ("Cách chăm sóc mai", "Cách nấu phở", "Thuế GTGT", "Travel checklist"):
            with self.subTest(topic=topic):
                body = BuilderFactory.create("facebook").build(topic)
                self.assertIn("Engineering AI Platform", body)
                self.assertIn("ngoài phạm vi", body)
                for forbidden in ("tưới", "công thức", "ngân sách du lịch", "ETF"):
                    self.assertNotIn(forbidden, body)

    def test_failure_intelligence_library_items_are_bilingual(self):
        data = json.loads(FAILURE_LIBRARY_PATH.read_text(encoding="utf-8"))
        bilingual_fields = ("failure_mode", *REQUIRED_FAILURE_FIELDS)

        for profile in data["profiles"]:
            with self.subTest(profile=profile["key"]):
                for field in bilingual_fields:
                    value = profile[field]
                    values = value if isinstance(value, list) else (value,)
                    for item in values:
                        self.assertIsInstance(item, dict, field)
                        self.assertTrue(item.get("id"), item)
                        self.assertTrue(item.get("vi"), item)
                        self.assertTrue(item.get("en"), item)

    def test_failure_intelligence_library_selects_vi_by_default_and_en_for_future_locale(self):
        vi_context = FailureIntelligenceLibrary().get("WIRE_ROPE_FAILURE").as_context()
        en_context = FailureIntelligenceLibrary(locale="en").get("WIRE_ROPE_FAILURE").as_context()

        self.assertIn("kiểm tra số lượng và vị trí sợi cáp bị đứt", vi_context["inspection_points"])
        self.assertIn("broken wires count and location", en_context["inspection_points"])

    def test_final_topic_context_acceptance_cases(self):
        engine = TopicIntelligenceEngine()
        cases = {
            "Cáp cẩu trục bị đứt": {
                "domain": "Industrial Maintenance",
                "intent": "Troubleshooting",
                "equipment": ("Crane",),
                "components": ("Wire Rope",),
                "failures": ("Broken",),
                "severity": "Critical",
                "playbook_key": "WIRE_ROPE_FAILURE",
                "query": "Crane Wire Rope Broken Troubleshooting",
            },
            "Động cơ bị cháy": {
                "equipment": ("Motor",),
                "failures": ("Burned",),
                "severity": "High",
                "query": "Motor Burned Troubleshooting",
            },
            "Biến tần báo OC": {
                "equipment": ("VFD",),
                "failures": ("Over Current",),
                "severity": "High",
                "query": "VFD Over Current Troubleshooting",
            },
            "PLC Siemens SF": {
                "equipment": ("PLC", "Siemens PLC"),
                "failures": ("System Fault",),
                "severity": "High",
            },
            "Đường hàn SAW rỗ khí": {
                "components": ("Weld Seam",),
                "failures": ("Porosity",),
                "severity": "High",
                "playbook_key": "SAW_POROSITY",
            },
            "Nuôi chó Husky": {"domain": "Out of Scope", "intent": "Training"},
            "Học tiếng Nhật N5": {"domain": "Out of Scope", "intent": "Training"},
            "Thuế GTGT": {"domain": "Out of Scope"},
            "Blockchain Layer 2": {"domain": "Out of Scope"},
            "Cách chăm sóc mai": {"domain": "Out of Scope", "processes": ()},
        }

        for topic, expected in cases.items():
            with self.subTest(topic=topic):
                context = engine.analyze(topic)
                for field, value in expected.items():
                    if field == "query":
                        self.assertEqual(context.knowledge_query, value)
                    else:
                        self.assertEqual(getattr(context, field), value)
                self.assertGreater(context.confidence, 0.5)

    def test_crane_failure_routing_does_not_mutate_unknown_failure_to_noise(self):
        engine = TopicIntelligenceEngine()
        cases = {
            "Cầu trục 7.5T bị đứt": ("CRANE_GENERAL_FAILURE", "Crane Broken Troubleshooting"),
            "Cầu trục bị gãy": ("CRANE_GENERAL_FAILURE", "Crane Broken Troubleshooting"),
            "Cầu trục bị nứt": ("CRANE_GENERAL_FAILURE", "Crane Cracked Troubleshooting"),
            "Cầu trục rung": ("CRANE_NOISE", "Crane Vibration Troubleshooting"),
            "Cầu trục kêu": ("CRANE_NOISE", "Crane Noise Troubleshooting"),
            "Cáp cẩu trục bị đứt": ("WIRE_ROPE_FAILURE", "Crane Wire Rope Broken Troubleshooting"),
        }

        for topic, (playbook_key, query) in cases.items():
            with self.subTest(topic=topic):
                context = engine.analyze(topic)
                self.assertEqual(context.playbook_key, playbook_key)
                self.assertEqual(context.knowledge_query, query)

    def test_empty_context_playbook_uses_generic_reasoning_for_low_confidence_fuzzy_match(self):
        engine = TopicIntelligenceEngine()
        reasoning = engine.reason("Cầu trục 7.5T bị đứt")
        object.__setattr__(reasoning.topic_context, "playbook_key", "")

        playbook = match_playbook(reasoning.topic, reasoning)

        self.assertEqual(playbook.key, "GENERAL_ENGINEERING")
        self.assertEqual(playbook.aliases, ("Cầu trục 7.5T bị đứt",))

    def test_wire_rope_failure_merges_failure_intelligence_into_context(self):
        context = TopicIntelligenceEngine().analyze("Cáp cẩu trục bị đứt")
        merged = " ".join(
            (
                *context.standards,
                *context.failure_intelligence.get("symptoms", ()),
                *context.failure_intelligence.get("inspection_points", ()),
                *context.failure_intelligence.get("verification_steps", ()),
                *context.failure_intelligence.get("safety_notes", ()),
            )
        )

        for expected in (
            "ISO 4309",
            "sợi cáp",
            "đường kính cáp",
            "puly",
            "tang cuốn",
            "LOTO",
            "thử tải",
            "nghiệm thu",
        ):
            self.assertIn(expected, merged)
        self.assert_no_raw_failure_intelligence_phrases(merged)

    def test_wire_rope_failure_generated_channels_use_context_intelligence(self):
        engine = TopicIntelligenceEngine()
        for channel in ("facebook", "checklist", "approval", "video", "seo", "image", "tiktok"):
            with self.subTest(channel=channel):
                output = engine.generate("Cáp cẩu trục bị đứt", channel)
                if channel in {"facebook", "seo"}:
                    for expected in (
                        "ISO 4309",
                        "sợi cáp",
                        "đường kính cáp",
                        "puly",
                        "tang cuốn",
                        "LOTO",
                        "thử tải",
                        "nghiệm thu",
                    ):
                        self.assertIn(expected, output)
                if channel in {"checklist", "approval", "video", "image", "tiktok"}:
                    self.assertIn("Cáp cẩu trục bị đứt", output)
                    self.assertIn("cáp", output)
                self.assert_no_raw_failure_intelligence_phrases(output)

    def test_wire_rope_failure_output_uses_context_playbook_not_crane_noise(self):
        body = TopicIntelligenceEngine().generate("Cáp cẩu trục bị đứt", "facebook")

        self.assert_facebook_contract(body)
        for expected in (
            "dừng thiết bị",
            "LOTO",
            "cáp tải",
            "sợi cáp",
            "puly",
            "tang cuốn",
            "thay cáp",
            "thử tải",
        ):
            self.assertIn(expected, body)

        for forbidden in ("bánh xe", "ray", "hộp giảm tốc"):
            self.assertNotIn(forbidden, body)

    def test_knowledge_engine_v2_crane_wire_rope_facebook_acceptance(self):
        body = TopicIntelligenceEngine().generate("Cầu trục 7.5T bị đứt cáp", "facebook")

        self.assert_facebook_contract(body)
        for expected in (
            "Cầu trục 7.5T bị đứt cáp",
            "ISO 4309",
            "LOTO",
            "đường kính cáp",
            "puly",
            "tang cuốn",
            "thay cáp",
            "thử tải",
            "Maintenance Engineer",
            "QA/QC",
            "Workshop Manager",
            "CMMS",
            "Bài học rút ra",
        ):
            self.assertIn(expected, body)

        for forbidden in ("Hook:", "CTA:", "viral", "#", "bánh xe mòn lệch", "Chẩn đoán tiếng ồn"):
            self.assertNotIn(forbidden, body)

    def test_release_blocker_engineering_documents_are_chief_engineer_quality(self):
        cases = {
            "Cầu trục 7.5T bị đứt cáp": (
                "ISO 4309",
                "đường kính cáp",
                "puly",
                "tang cuốn",
                "quá tải",
                "thử tải",
            ),
            "Đường hàn SAW bị rỗ khí": (
                "SAW",
                "thuốc hàn",
                "WPS",
                "VT",
                "UT",
                "stickout",
                "hồ sơ sấy",
            ),
            "Phun bi tự động gãy cánh đẩy": (
                "blast wheel",
                "control cage",
                "liner",
                "separator",
                "profile",
                "rung",
            ),
            "Động cơ giảm tốc bị nóng": (
                "gearbox",
                "dầu",
                "breather",
                "đồng tâm",
                "nhiệt",
                "ISO 10816",
            ),
            "Máy nén khí áp thấp": (
                "áp outlet",
                "header",
                "leak",
                "pressure decay",
                "lọc tách dầu",
                "load-unload",
            ),
            "Biến tần báo OC": (
                "VFD",
                "DC bus",
                "accel",
                "megger",
                "fault",
                "parameter",
            ),
        }

        forbidden = (
            "Dấu hiệu bất thường",
            "dấu hiệu bất thường",
            "Cần kiểm tra",
            "cần kiểm tra",
            "Có thể",
            "có thể",
            "Trong nhiều trường hợp",
            "trong nhiều trường hợp",
            "Hook:",
            "CTA:",
            "viral",
        )

        engine = TopicIntelligenceEngine()
        for topic, expected_terms in cases.items():
            with self.subTest(topic=topic):
                body = engine.generate(topic, "facebook")
                self.assert_facebook_contract(body)
                for expected in expected_terms:
                    self.assertIn(expected, body)
                for phrase in forbidden:
                    self.assertNotIn(phrase, body)
                for expected_section in (
                    "Nguyên nhân cần ưu tiên",
                    "Trình tự kiểm tra thiết yếu",
                    "Nguyên tắc sửa đúng",
                    "Bài học rút ra",
                ):
                    self.assertIn(expected_section, body)

    def test_engineering_knowledge_library_v3_release_contract(self):
        library = EngineeringKnowledgeLibrary()
        required = (
            "WIRE_ROPE_FAILURE",
            "SAW_POROSITY",
            "SAW_UNDERCUT",
            "CONVEYOR_BELT_MISALIGNMENT",
            "SHOTBLAST_CONVEYOR",
            "AIR_COMPRESSOR_LOW_PRESSURE",
            "PAINT_PEELING",
        )

        for key in required:
            with self.subTest(key=key):
                playbook = library.get(key)
                self.assertIsNotNone(playbook)
                for field in KNOWLEDGE_CONTRACT_FIELDS:
                    self.assertTrue(getattr(playbook, field), field)
                self.assertGreaterEqual(len(playbook.root_causes), 3)
                self.assertGreaterEqual(len(playbook.related_standards), 2)
                self.assertGreaterEqual(len(playbook.measurements), 4)
                self.assertGreaterEqual(len(playbook.inspection_procedure), 4)
                self.assertGreaterEqual(len(playbook.repair_procedure_sop), 4)
                self.assertGreaterEqual(len(playbook.verification_after_repair), 4)
                self.assertGreaterEqual(len(playbook.preventive_maintenance), 4)

    def test_conveyor_belt_misalignment_routes_before_shotblast_and_uses_conveyor_knowledge(self):
        engine = TopicIntelligenceEngine()
        topic = "Băng tải buồng phun bi bị lệch"
        reasoning = engine.reason(topic)
        body = engine.generate(topic, "seo")
        lowered = body.lower()

        self.assertEqual(reasoning.topic_context.playbook_key, "CONVEYOR_BELT_MISALIGNMENT")
        self.assertEqual(match_playbook(topic, reasoning).key, "CONVEYOR_BELT_MISALIGNMENT")
        for expected in (
            "belt tracking",
            "head pulley",
            "tail pulley",
            "carrying roller",
            "return roller",
            "idler",
            "take-up",
            "belt splice",
            "belt tension",
            "bearing",
            "shaft runout",
            "scraper",
        ):
            self.assertIn(expected, lowered)
        for forbidden in (
            "blast wheel",
            "impeller",
            "control cage",
            "separator",
            "blade",
            "bucket elevator",
        ):
            self.assertNotIn(forbidden, lowered)

    def test_conveyor_knowledge_contains_required_tracking_concepts(self):
        raw = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "src"
                / "hgpt_ai_os"
                / "topic_engine"
                / "engineering_knowledge_playbooks.json"
            ).read_text(encoding="utf-8")
        )
        playbook = next(item for item in raw["playbooks"] if item["key"] == "CONVEYOR_BELT_MISALIGNMENT")
        serialized = json.dumps(playbook, ensure_ascii=False).lower()

        for concept in (
            "belt tracking",
            "head pulley",
            "tail pulley",
            "carrying roller",
            "return roller",
            "idler",
            "take-up",
            "belt splice",
            "belt tension",
            "roller alignment",
            "pulley alignment",
            "laser alignment",
            "bearing",
            "shaft runout",
            "frame alignment",
            "material build-up",
            "scraper",
        ):
            self.assertIn(concept, serialized)

    def test_final_release_existing_topics_keep_same_routing(self):
        engine = TopicIntelligenceEngine()
        cases = {
            "Cầu trục 7.5T bị đứt cáp": "WIRE_ROPE_FAILURE",
            "Máy nén khí áp thấp": "AIR_COMPRESSOR_LOW_PRESSURE",
            "Đường hàn SAW bị rỗ khí": "SAW_POROSITY",
            "Đường hàn SAW bị cháy cạnh": "SAW_UNDERCUT",
            "Bong tróc sơn": "PAINT_PEELING",
        }

        for topic, expected in cases.items():
            with self.subTest(topic=topic):
                reasoning = engine.reason(topic)
                self.assertEqual(match_playbook(topic, reasoning).key, expected)

    def test_engineering_writer_v3_generates_release_topics_from_structured_knowledge(self):
        cases = {
            "Cầu trục đứt cáp": ("WIRE_ROPE_FAILURE", "ISO 4309", "broken wire count", "sheave groove"),
            "Đường hàn SAW bị rỗ khí": ("SAW_POROSITY", "AWS D1.1", "hồ sơ sấy", "VT/UT"),
            "SAW undercut": ("SAW_UNDERCUT", "ISO 5817", "undercut depth", "stickout"),
            "Shotblast conveyor lỗi": ("SHOTBLAST_CONVEYOR", "ISO 8501-1", "surface profile", "vibration"),
            "Máy nén khí áp thấp": ("AIR_COMPRESSOR_LOW_PRESSURE", "ISO 8573", "pressure decay", "load-unload"),
            "Lỗi bong tróc sơn": ("PAINT_PEELING", "ISO 8503", "dew point", "adhesion"),
        }
        engine = TopicIntelligenceEngine()

        for topic, (key, standard, measurement, mechanism) in cases.items():
            with self.subTest(topic=topic):
                body = engine.generate(topic, "seo")
                self.assert_engineering_v2_document(body)
                self.assertIn(standard, body)
                self.assertIn(measurement, body)
                self.assertIn(mechanism, body)
                self.assertGreaterEqual(body.count("Nguyên nhân gốc:"), 3)
                self.assertNotIn("check carefully", body.lower())
                self.assertNotIn("do regular maintenance", body.lower())
                self.assertEqual(match_playbook(topic, engine.reason(topic)).key, key)

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

    def test_domain_playbook_matching_uses_vietnamese_engineering_topics(self):
        cases = {
            "Đường hàn SAW bị rỗ khí": "SAW_POROSITY",
            "Máy mài cầm tay hỏng liên tục": "POWER_TOOL_BREAKDOWN",
            "5S khu vực máy cắt Laser": "LASER_5S",
            "Lỗi bong tróc sơn": "PAINT_PEELING",
        }

        for topic, expected in cases.items():
            with self.subTest(topic=topic):
                self.assertEqual(match_playbook(topic).key, expected)

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
            self.assert_facebook_contract(body)
            self.assert_no_forbidden_patterns(body)

        for body in seo:
            self.assert_engineering_v2_document(body)
            self.assert_no_forbidden_patterns(body)

        for body in checklists:
            self.assert_checklist_contract(body)
            self.assert_no_forbidden_patterns(body)

        saw_checklist = checklists[0]
        for item in ("sấy hoặc thay thuốc hàn", "kiểm tra dây hàn", "làm sạch mép hàn", "dầu, rỉ hoặc ẩm", "dòng hàn", "điện áp", "tốc độ chạy", "chiều sâu lớp thuốc", "stickout", "VT", "UT", "WPS"):
            self.assertIn(item, saw_checklist)

        maintenance_checklist = checklists[1]
        for item in ("chổi than", "bạc đạn", "rotor/stator", "công tắc", "dây nguồn", "bụi mài", "quá tải", "rung/ồn/nhiệt", "lịch bảo trì", "hướng dẫn vận hành"):
            self.assertIn(item, maintenance_checklist)

        self.assertLess(_max_similarity(facebook), 0.72)
        self.assertLess(_max_similarity(seo), 0.72)
        self.assertLess(_max_similarity(checklists), 0.78)

    def test_quality_acceptance_for_saw_porosity_facebook(self):
        body = TopicIntelligenceEngine().generate("Đường hàn SAW bị rỗ khí", "facebook")

        self.assert_facebook_contract(body)
        for expected in ("SAW", "rỗ khí", "thuốc hàn", "VT", "UT", "WPS"):
            self.assertIn(expected, body)
        self.assertTrue("dòng hàn" in body or "điện áp" in body)
        self.assert_no_forbidden_patterns(body)

    def test_quality_acceptance_for_power_tool_facebook(self):
        body = TopicIntelligenceEngine().generate("Máy mài cầm tay hỏng liên tục", "facebook")

        self.assert_facebook_contract(body)
        for expected in ("máy mài", "chổi than", "bạc đạn", "bụi mài", "quá tải", "bảo trì"):
            self.assertIn(expected, body)
        self.assert_no_forbidden_patterns(body)

    def test_seo_and_prompt_writers_are_domain_specific(self):
        engine = TopicIntelligenceEngine()

        saw_seo = engine.generate("Đường hàn SAW bị rỗ khí", "seo")
        for expected in ("thuốc hàn ẩm", "bề mặt thép", "điện áp", "dòng hàn", "tốc độ chạy", "chiều sâu lớp thuốc", "VT", "UT", "WPS"):
            self.assertIn(expected, saw_seo)

        tool_seo = engine.generate("Máy mài cầm tay hỏng liên tục", "seo")
        for expected in ("chổi than", "bạc đạn", "rotor/stator", "bụi mài", "quá tải", "dây nguồn", "công tắc", "bảo trì định kỳ", "công nhân"):
            self.assertIn(expected, tool_seo)

        saw_image = engine.generate("Đường hàn SAW bị rỗ khí", "image")
        for expected in ("dây chuyền hàn SAW", "thuốc hàn", "đường hàn", "kiểm tra", "mũ hàn", "xưởng kết cấu thép"):
            self.assertIn(expected, saw_image)

        tool_video = engine.generate("Máy mài cầm tay hỏng liên tục", "video")
        for expected in ("máy mài", "chổi than", "bạc đạn", "bụi mài", "bảo hộ"):
            self.assertIn(expected, tool_video)

    def test_writer_final_quality_rescue_acceptance(self):
        engine = TopicIntelligenceEngine()

        saw_facebook = engine.generate("Đường hàn SAW bị rỗ khí", "facebook")
        grinder_facebook = engine.generate("Máy mài cầm tay hỏng liên tục", "facebook")
        tiktok = engine.generate("Đường hàn SAW bị rỗ khí", "tiktok")
        image_prompt = engine.generate("Máy mài cầm tay hỏng liên tục", "image")
        video_prompt = engine.generate("Đường hàn SAW bị rỗ khí", "video")
        seo = engine.generate("Đường hàn SAW bị rỗ khí", "seo")
        checklist = engine.generate("Máy mài cầm tay hỏng liên tục", "checklist")

        self.assert_facebook_contract(saw_facebook)
        self.assert_facebook_contract(grinder_facebook)
        for expected in ("SAW", "rỗ khí", "thuốc hàn", "sấy thuốc", "bề mặt thép", "dòng hàn", "điện áp", "tốc độ chạy", "WPS", "VT", "UT", "sửa hàn"):
            self.assertIn(expected, saw_facebook)
        for expected in ("máy mài cầm tay", "chổi than", "bạc đạn", "rotor/stator", "bụi mài", "quá tải", "công tắc/dây nguồn", "rung/ồn/nhiệt", "bảo trì định kỳ", "công nhân"):
            self.assertIn(expected, grinder_facebook)

        for expected in ("Mở đầu", "Lời thoại", "Cảnh 1", "Bài học kỹ thuật", "Kết thúc"):
            self.assertIn(expected, tiktok)
        self.assertGreaterEqual(len(tiktok.split()), 120)
        self.assertLessEqual(len(tiktok.split()), 220)
        for forbidden in ("Mốc 0-3 giây", "Góc máy", "Phụ đề", "Chuyển cảnh"):
            self.assertNotIn(forbidden, tiktok)
        self.assertIn("Góc máy", image_prompt)
        self.assertIn("Ánh sáng", image_prompt)
        self.assertIn("Chi tiết cần tránh", image_prompt)
        self.assertIn("Thời lượng: 45-60 giây", video_prompt)
        self.assertIn("Góc máy", video_prompt)
        self.assertIn("Lời thoại", video_prompt)
        self.assertIn("Phụ đề", video_prompt)
        self.assertIn("9:16", video_prompt)
        self.assertIn("Âm thanh", video_prompt)
        self.assertIn("Kết thúc", video_prompt)
        self.assertGreater(len(seo), 2500)
        self.assert_engineering_v2_document(seo)
        self.assert_checklist_contract(checklist)
        for expected in ("An toàn và cô lập năng lượng", "Đo kiểm", "Phòng ngừa tái diễn"):
            self.assertIn(expected, checklist)
        self.assertLess(SequenceMatcher(None, saw_facebook, grinder_facebook).ratio(), 0.65)

        for body in (saw_facebook, grinder_facebook, tiktok, image_prompt, video_prompt, seo, checklist):
            self.assert_no_forbidden_patterns(body)

    def test_rc2_prompt_and_facebook_quality_acceptance(self):
        engine = TopicIntelligenceEngine()

        saw_image = engine.generate("Đường hàn SAW bị rỗ khí", "image")
        for expected in ("Prompt Gemini tạo ảnh", "Bối cảnh", "Góc máy", "Ống kính", "Ánh sáng", "Chi tiết cần tránh", "Tỷ lệ khung hình", "dây chuyền hàn SAW", "lớp thuốc", "đường hàn", "xe hàn", "rỗ khí", "bảo hộ", "xưởng kết cấu thép"):
            self.assertIn(expected, saw_image)

        grinder_image = engine.generate("Máy mài cầm tay hỏng liên tục", "image")
        for expected in ("bàn bảo trì", "máy mài", "chổi than", "bạc đạn", "bụi", "rotor/stator", "kỹ thuật viên", "bảo hộ", "bảng dụng cụ 5S", "xưởng thép"):
            self.assertIn(expected, grinder_image)

        laser_image = engine.generate("5S khu vực máy cắt Laser", "image")
        for expected in ("bàn cắt laser", "phôi", "chi tiết thành phẩm có nhãn", "thùng phế", "bảng dụng cụ", "vạch sàn", "dòng chảy 5S"):
            self.assertIn(expected, laser_image)

        paint_image = engine.generate("Lỗi bong tróc sơn", "image")
        for expected in ("cấu kiện thép", "sơn bong", "nhám bề mặt", "máy đo DFT", "người kiểm tra", "khu phun bi/sơn"):
            self.assertIn(expected, paint_image)

        saw_video = engine.generate("Đường hàn SAW bị rỗ khí", "video")
        for expected in ("Thời lượng: 45-60 giây", "9:16", "Góc máy", "ống kính", "Ánh sáng", "Lời thoại", "Phụ đề", "Âm thanh", "Kết thúc", "Chi tiết cần tránh", "SAW", "thuốc hàn", "WPS", "VT/UT"):
            self.assertIn(expected, saw_video)

        saw_facebook = engine.generate("Đường hàn SAW bị rỗ khí", "facebook")
        laser_facebook = engine.generate("5S khu vực máy cắt Laser", "facebook")
        banned = (
            "Người có kinh nghiệm sẽ không vội kết luận",
            "Đây là điểm phải xử lý bằng dữ liệu hiện trường",
            "Nếu thiếu một mắt xích",
        )
        for body in (saw_facebook, laser_facebook):
            for phrase in banned:
                self.assertNotIn(phrase, body)
        self.assertLess(SequenceMatcher(None, saw_facebook, laser_facebook).ratio(), 0.62)

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

    def assert_no_forbidden_patterns(self, body: str) -> None:
        for pattern in FORBIDDEN_OUTPUT_PATTERNS:
            self.assertNotIn(pattern, body)

    def assert_no_raw_failure_intelligence_phrases(self, body: str) -> None:
        lowered = body.lower()
        for phrase in RAW_FAILURE_INTELLIGENCE_PHRASES:
            self.assertNotIn(phrase, lowered)

    def assert_engineering_v2_document(self, body: str) -> None:
        current_index = -1
        for section in ENGINEERING_V2_SECTIONS:
            index = body.find(f"\n{section}\n")
            self.assertGreater(index, current_index, section)
            current_index = index
        for field in ROOT_CAUSE_FIELDS:
            self.assertIn(field, body)
        self.assertIn("Nguyên nhân gốc:", body)
        self.assertIn("Tiêu chí nghiệm thu", body)
        self.assertIn("Tiêu chuẩn áp dụng", body)
        self.assertIn("Đề xuất Digital Factory", body)

    def assert_facebook_contract(self, body: str) -> None:
        self.assertGreaterEqual(len(body.split()), 700)
        self.assertLessEqual(len(body.split()), 1200)
        for section in (
            "Mô tả kỹ thuật ngắn",
            "Nguyên nhân cần ưu tiên",
            "Trình tự kiểm tra thiết yếu",
            "Bằng chứng phải có trước khi kết luận",
            "Nguyên tắc sửa đúng",
            "Bài học rút ra",
        ):
            self.assertIn(section, body)
        self.assertNotIn("Phân tích nguyên nhân gốc", body)
        self.assertNotIn("Đề xuất Digital Factory", body)

    def assert_checklist_contract(self, body: str) -> None:
        for section in (
            "1. An toàn và cô lập năng lượng",
            "2. Ghi nhận hiện trạng",
            "3. Kiểm tra cơ khí",
            "4. Kiểm tra điện/điều khiển",
            "5. Đo kiểm",
            "6. Khắc phục",
            "7. Kiểm tra sau sửa",
            "8. Nghiệm thu",
            "9. Phòng ngừa tái diễn",
        ):
            self.assertIn(section, body)
        checkbox_lines = [line for line in body.splitlines() if line.startswith("- [ ]")]
        self.assertGreaterEqual(len(checkbox_lines), 18)
        self.assertTrue(all(len(line.split()) <= 28 for line in checkbox_lines))
        self.assertNotIn("Phân tích nguyên nhân gốc", body)
        self.assertNotIn("Đề xuất Digital Factory", body)


def _max_similarity(values: list[str]) -> float:
    scores = []
    for left_index, left in enumerate(values):
        for right in values[left_index + 1 :]:
            scores.append(SequenceMatcher(None, left, right).ratio())
    return max(scores)


if __name__ == "__main__":
    unittest.main()
