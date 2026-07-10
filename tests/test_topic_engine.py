from __future__ import annotations

import unittest
from difflib import SequenceMatcher

from hgpt_ai_os.content.generator import ContentGenerator
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
    "Root Cause:",
)


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
            for section in (
                "Vấn đề hiện trường",
                "Dấu hiệu cần kiểm tra",
                "Phân tích kỹ thuật",
                "Nguyên nhân khả năng cao",
                "Hành động khắc phục",
                "Phòng ngừa tái diễn",
                "Bài học quản lý",
            ):
                self.assertIn(section, body)
            self.assert_no_forbidden_patterns(body)

        for body in seo:
            for section in (
                "Triệu chứng thường gặp",
                "Cơ chế kỹ thuật",
                "Nguyên nhân cần ưu tiên xác minh",
                "Cách kiểm tra tại xưởng",
                "Biện pháp khắc phục",
                "Kiểm soát phòng ngừa",
                "Kết luận",
            ):
                self.assertIn(section, body)
            self.assert_no_forbidden_patterns(body)

        saw_checklist = checklists[0]
        for item in ("sấy thuốc hàn", "kiểm tra dây hàn", "làm sạch mép hàn", "kiểm tra dầu/rỉ/ẩm", "dòng hàn", "điện áp", "tốc độ chạy", "chiều sâu lớp thuốc", "stickout", "VT/UT", "WPS"):
            self.assertIn(item, saw_checklist)

        maintenance_checklist = checklists[1]
        for item in ("chổi than", "bạc đạn", "rotor/stator", "công tắc", "dây nguồn", "bụi mài", "quá tải", "rung/ồn/nhiệt", "lịch bảo trì", "hướng dẫn vận hành"):
            self.assertIn(item, maintenance_checklist)

        self.assertLess(_max_similarity(facebook), 0.72)
        self.assertLess(_max_similarity(seo), 0.72)
        self.assertLess(_max_similarity(checklists), 0.78)

    def test_quality_acceptance_for_saw_porosity_facebook(self):
        body = TopicIntelligenceEngine().generate("Đường hàn SAW bị rỗ khí", "facebook")

        for expected in ("SAW", "rỗ khí", "thuốc hàn", "VT", "UT", "WPS"):
            self.assertIn(expected, body)
        self.assertTrue("dòng hàn" in body or "điện áp" in body)
        self.assert_no_forbidden_patterns(body)

    def test_quality_acceptance_for_power_tool_facebook(self):
        body = TopicIntelligenceEngine().generate("Máy mài cầm tay hỏng liên tục", "facebook")

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

        self.assertGreater(len(saw_facebook), 1200)
        self.assertGreater(len(grinder_facebook), 1200)
        for expected in ("SAW", "rỗ khí", "thuốc hàn", "sấy thuốc", "bề mặt thép", "dòng hàn", "điện áp", "tốc độ chạy", "WPS", "VT/UT", "sửa hàn"):
            self.assertIn(expected, saw_facebook)
        for expected in ("máy mài cầm tay", "chổi than", "bạc đạn", "rotor/stator", "bụi mài", "quá tải", "công tắc/dây nguồn", "rung/ồn/nhiệt", "bảo trì định kỳ", "công nhân"):
            self.assertIn(expected, grinder_facebook)

        for expected in ("Mở đầu", "Khơi tò mò", "Nỗi đau", "Thông tin", "Cú twist", "Kêu gọi hành động"):
            self.assertIn(expected, tiktok)
        for forbidden in ("Mốc 0-3 giây", "Góc máy", "Lời thoại", "Phụ đề", "Chuyển cảnh"):
            self.assertNotIn(forbidden, tiktok)
        self.assertIn("Góc máy", image_prompt)
        self.assertIn("Ánh sáng", image_prompt)
        self.assertIn("Chi tiết cần tránh", image_prompt)
        self.assertIn("thời lượng 30-45 giây", video_prompt)
        self.assertIn("Góc máy", video_prompt)
        self.assertIn("Lời thoại", video_prompt)
        self.assertIn("Phụ đề", video_prompt)
        self.assertIn("9:16", video_prompt)
        self.assertIn("Âm thanh", video_prompt)
        self.assertIn("Kết thúc", video_prompt)
        self.assertGreater(len(seo), 2500)
        for expected in ("Tần suất", "Người chịu trách nhiệm", "Hành động khi không đạt"):
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
        for expected in ("thời lượng 30-45 giây", "9:16", "Góc máy", "ống kính", "Ánh sáng", "Lời thoại", "Phụ đề", "Âm thanh", "Kết thúc", "Chi tiết cần tránh", "SAW", "thuốc hàn", "WPS", "VT/UT"):
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
        self.assertLess(SequenceMatcher(None, saw_facebook, laser_facebook).ratio(), 0.58)

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


def _max_similarity(values: list[str]) -> float:
    scores = []
    for left_index, left in enumerate(values):
        for right in values[left_index + 1 :]:
            scores.append(SequenceMatcher(None, left, right).ratio())
    return max(scores)


if __name__ == "__main__":
    unittest.main()
