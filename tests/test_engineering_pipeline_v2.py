import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hgpt_ai_os.ai.gemini_client import AIProviderError, AIResponse
from hgpt_ai_os.engineering_pipeline import (
    EngineeringGenerationPipeline,
    analyze_topic_intent,
)
from hgpt_ai_os.topic_engine import TopicIntelligenceEngine


ACCEPTANCE_TOPICS = (
    "Vòng bi động cơ bị kêu",
    "Động cơ 3 pha bị nóng",
    "Bơm thủy lực bị mất áp",
    "Máy cắt laser không ra khí",
    "Đường hàn SAW bị rỗ khí",
    "Bảo trì tự quản",
    "TPM",
    "5S trong xưởng",
    "Máy cán tôn bị khóa MHI",
    "Đầu tư dây chuyền hàn dầm 3 trong 1",
)

AI_SUCCESS_TOPICS = (
    "Vòng bi động cơ bị kêu",
    "Động cơ 3 pha bị nóng",
    "Bơm thủy lực bị mất áp",
)


def record_payload(topic: str) -> str:
    return json.dumps(
        {
            "title": f"Xử lý {topic}",
            "topic": topic,
            "problem": f"Sự cố cần phân tích bằng dữ liệu hiện trường: {topic}",
            "domain": "Bảo trì công nghiệp",
            "equipment": ["động cơ điện", "bơm thủy lực", "cụm truyền động"],
            "component": ["ổ bi", "cuộn dây stator", "khớp nối", "van an toàn"],
            "symptoms": [
                "tiếng kêu tăng theo tốc độ quay",
                "nhiệt vỏ máy tăng so với nền vận hành",
                "rung tại gối đỡ hoặc thân máy",
                "dòng điện hoặc áp suất dao động khi có tải",
            ],
            "failure_symptom": [
                "tiếng kêu tăng theo tốc độ quay",
                "nhiệt vỏ máy tăng so với nền vận hành",
                "rung tại gối đỡ hoặc thân máy",
                "dòng điện hoặc áp suất dao động khi có tải",
            ],
            "operating_context": "Thiết bị đang phục vụ sản xuất liên tục; cần ghi tải, tốc độ, nhiệt độ và lịch bảo trì trước khi tháo.",
            "working_principle": "Cụm quay phải giữ đồng tâm, bôi trơn đúng và tải ổn định; sai lệch cơ khí hoặc điện làm tăng ma sát, nhiệt và rung.",
            "failure_mechanisms": [
                "ma sát tăng tại ổ bi hoặc bề mặt làm việc làm nhiệt và rung tăng theo tốc độ",
                "lệch tâm khớp nối tạo tải hướng kính bất thường lên cụm quay",
                "điều kiện tải hoặc nguồn cấp không ổn định làm thiết bị làm việc ngoài vùng thiết kế",
            ],
            "root_causes": [
                "Hạng 1 - nguyên nhân gốc thứ nhất từ hồ sơ kỹ thuật. Vì sao xảy ra: điều kiện vận hành tạo tải bất thường. Cơ chế vật lý: ma sát hoặc quá tải làm tăng nhiệt và rung. Kiểm tra: cô lập thiết bị, quan sát dấu hiệu, đo thông số liên quan. Đo kiểm: Không đủ dữ liệu để kết luận. Cần đo thông số vận hành thực tế. Dụng cụ: thiết bị đo chuyên dụng, phiếu kiểm, ảnh hiện trường. Logic quyết định: chỉ sửa khi bằng chứng đo khớp triệu chứng. Sửa chữa: xử lý đúng nguyên nhân đã xác nhận. Xác nhận: chạy thử có kiểm soát và đo lại cùng phương pháp. Tiêu chí nhận: triệu chứng không tái diễn trong điều kiện thử đã ghi nhận.",
                "Hạng 2 - nguyên nhân gốc thứ hai từ hồ sơ kỹ thuật. Vì sao xảy ra: sai lệch lắp đặt hoặc bảo trì làm cụm chi tiết làm việc ngoài điều kiện thiết kế. Cơ chế vật lý: lệch tâm, lỏng ghép hoặc bôi trơn kém tạo mòn tăng tốc. Kiểm tra: kiểm tra cơ khí, lịch sử bảo trì và dấu vết tháo lắp. Đo kiểm: Không đủ dữ liệu để kết luận. Cần đo độ lệch, độ rơ hoặc thông số liên quan. Dụng cụ: đồng hồ so, thước căn, dụng cụ đo chuyên dụng. Logic quyết định: nếu sai lệch vượt tiêu chí OEM thì hiệu chỉnh trước khi thay phụ tùng. Sửa chữa: căn chỉnh, siết lại, thay chi tiết đã hỏng. Xác nhận: đo lại sau lắp và chạy thử. Tiêu chí nhận: thông số trở về tiêu chí OEM hoặc tiêu chí nội bộ đã phê duyệt.",
                "Hạng 3 - nguyên nhân gốc thứ ba từ hồ sơ kỹ thuật. Vì sao xảy ra: môi trường hoặc quy trình vận hành tạo nhiễm bẩn, quá tải hoặc chu kỳ dừng chạy bất lợi. Cơ chế vật lý: bụi, nhiệt, ẩm hoặc tải sốc làm suy giảm bề mặt làm việc. Kiểm tra: kiểm tra môi trường, thao tác vận hành và nhật ký lỗi. Đo kiểm: Không đủ dữ liệu để kết luận. Cần đo điều kiện môi trường và tải thực tế. Dụng cụ: camera nhiệt, ampe kìm, bộ ghi dữ liệu hoặc thiết bị đo chuyên dụng. Logic quyết định: nếu lỗi chỉ xuất hiện theo ca, tải hoặc môi trường thì sửa điều kiện tạo lỗi. Sửa chữa: loại bỏ tác nhân môi trường hoặc điều chỉnh quy trình vận hành. Xác nhận: theo dõi sau sửa trong chu kỳ vận hành thật. Tiêu chí nhận: không có triệu chứng lặp lại và dữ liệu theo dõi ổn định.",
            ],
            "evidence_required": ["ảnh điểm lỗi trước sửa", "log tải theo ca", "lịch bảo trì gần nhất"],
            "inspection": [
                "LOTO nguồn điện, nguồn áp và xác nhận thiết bị dừng an toàn",
                "ghi triệu chứng theo tốc độ, tải và thời điểm phát sinh",
                "kiểm nhiệt, rung, dòng điện hoặc áp suất tại các điểm chuẩn",
                "kiểm bôi trơn, độ rơ, đồng tâm, dấu mòn và dấu quá nhiệt",
                "đối chiếu lịch bảo trì, phụ tùng đã thay và cảnh báo vận hành",
            ],
            "inspection_procedure": [
                "LOTO nguồn điện, nguồn áp và xác nhận thiết bị dừng an toàn",
                "ghi triệu chứng theo tốc độ, tải và thời điểm phát sinh",
                "kiểm nhiệt, rung, dòng điện hoặc áp suất tại các điểm chuẩn",
                "kiểm bôi trơn, độ rơ, đồng tâm, dấu mòn và dấu quá nhiệt",
                "đối chiếu lịch bảo trì, phụ tùng đã thay và cảnh báo vận hành",
            ],
            "measurements": ["nhiệt độ vỏ máy", "rung mm/s RMS", "dòng điện từng pha", "áp suất làm việc hoặc tải vận hành"],
            "tools_required": ["camera nhiệt", "máy đo rung", "ampe kìm", "đồng hồ so", "phiếu LOTO"],
            "decision_logic": [
                "nếu nhiệt và rung cùng tăng theo tốc độ thì ưu tiên kiểm cụm quay và bôi trơn",
                "nếu dòng hoặc áp dao động theo tải thì kiểm nguồn cấp, tải và phần điều khiển",
                "nếu số đo chưa đủ thì chưa thay phụ tùng hàng loạt",
            ],
            "repair": ["cô lập thiết bị", "vệ sinh điểm kiểm", "căn chỉnh hoặc thay chi tiết đã xác nhận hỏng", "chạy thử có tải"],
            "repair_procedure": ["cô lập thiết bị", "vệ sinh điểm kiểm", "căn chỉnh hoặc thay chi tiết đã xác nhận hỏng", "chạy thử có tải"],
            "verification": ["đo lại nhiệt độ sau chạy thử", "đo lại rung hoặc áp suất bằng cùng điểm đo", "ghi nhận không còn tiếng kêu/rung bất thường"],
            "acceptance_criteria": ["thiết bị chạy ổn định dưới tải sản xuất", "không còn cảnh báo an toàn", "số đo sau sửa phù hợp tiêu chí OEM hoặc tiêu chí nội bộ đã phê duyệt"],
            "prevention": ["bổ sung điểm đo vào PM", "lưu trend nhiệt-rung-dòng", "kiểm phụ tùng thay thế theo mã kỹ thuật"],
            "preventive_maintenance": ["bổ sung điểm đo vào PM", "lưu trend nhiệt-rung-dòng", "kiểm phụ tùng thay thế theo mã kỹ thuật"],
            "lessons_learned": ["khóa nguyên nhân bằng số đo trước khi thay phụ tùng", "ghi baseline sau sửa để ca sau so sánh", "liên kết lỗi với điều kiện tải thực tế"],
            "common_mistakes": ["bỏ qua dữ liệu đo trước sửa", "thay phụ tùng khi chưa kiểm đồng tâm", "chạy thử không tải rồi bàn giao ngay"],
            "safety_controls": ["LOTO nguồn điện", "xả áp trước tháo đường ống", "barricade khu vực chạy thử"],
            "kaizen": ["chuẩn hóa phản ứng sự cố"],
            "digital_factory_recommendations": ["lưu ảnh trước và sau sửa"],
            "applicable_standards": [],
            "missing_information": [],
            "confidence": 0.91,
            "source_keys": ["AI_PROVIDER"],
        },
        ensure_ascii=False,
    )


class FakeAI:
    provider = None

    def __init__(self, response):
        self.response = response

    def generate(self, system_prompt, user_prompt):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        return self.response


class EngineeringPipelineV21Tests(unittest.TestCase):
    def test_topic_intent_classifies_supported_domain_and_topic_type(self):
        cases = {
            "Vòng bi động cơ bị kêu": ("MECHANICAL_MAINTENANCE", "FAULT_DIAGNOSIS"),
            "Động cơ 3 pha bị nóng": ("ELECTROMECHANICAL_MAINTENANCE", "FAULT_DIAGNOSIS"),
            "Bơm thủy lực bị mất áp": ("HYDRAULIC_PNEUMATIC", "FAULT_DIAGNOSIS"),
            "Cầu trục bị đứt cáp": ("CRANE_LIFTING", "SAFETY_RISK"),
            "Máy cắt laser không ra khí": ("PRODUCTION_EQUIPMENT", "FAULT_DIAGNOSIS"),
            "Đường hàn SAW bị rỗ khí": ("WELDING_ENGINEERING", "DEFECT_ANALYSIS"),
            "Sơn kết cấu thép bị bong tróc": ("STEEL_STRUCTURE_FABRICATION", "DEFECT_ANALYSIS"),
            "Sai kích thước dầm H sau hàn": ("STEEL_STRUCTURE_FABRICATION", "QA_QC_NONCONFORMITY"),
            "Bảo trì tự quản": ("TPM_LEAN_KAIZEN", "MANAGEMENT_METHOD"),
            "5S trong xưởng kết cấu thép": ("TPM_LEAN_KAIZEN", "MANAGEMENT_METHOD"),
            "Máy cán tôn bị khóa MHI": ("PRODUCTION_EQUIPMENT", "FAULT_DIAGNOSIS"),
            "Đầu tư dây chuyền hàn dầm 3 trong 1": ("PRODUCTION_EQUIPMENT", "INVESTMENT_EVALUATION"),
        }

        for topic, expected in cases.items():
            intent = analyze_topic_intent(topic)
            self.assertEqual((intent.primary_domain, intent.topic_type), expected)
            self.assertTrue(intent.request_id.startswith("req_"))
            self.assertTrue(intent.topic_fingerprint)

    def test_acceptance_topics_generate_seven_documents_only_when_ai_succeeds(self):
        topic_engine = TopicIntelligenceEngine()

        for topic in AI_SUCCESS_TOPICS:
            ai = FakeAI(
                AIResponse(
                    provider="Gemini",
                    model="gemini-test",
                    content=record_payload(topic),
                    metadata={"status_code": 200},
                )
            )
            pipeline = EngineeringGenerationPipeline(ai=ai)
            record, documents = pipeline.generate_documents(
                topic=topic,
                context="",
                knowledge_items=[],
                topic_context=topic_engine.analyze(topic),
            )

            self.assertTrue(pipeline.engineering_record_created)
            self.assertEqual(pipeline.engineering_record_source, "AI_PROVIDER")
            self.assertEqual(pipeline.http_status, "200")
            self.assertGreater(pipeline.ai_response_length, 0)
            self.assertEqual(record.title, f"Xử lý {topic}")
            self.assertTrue(record.primary_domain)
            self.assertTrue(record.topic_type)
            self.assertTrue(record.request_id)
            self.assertEqual(len(documents), 7)
            forbidden = (
                "Đây là gì",
                "Vì sao xảy ra",
                "Thông tin còn thiếu",
                "Cần bằng chứng",
                "Engineering Record",
                "EngineeringRecord",
                "Mục lục tra cứu",
                "Cấu trúc hồ sơ",
                "Trích yếu",
                "Đo kiểm",
                "Tiêu chuẩn",
                "Phụ lục tri thức bắt buộc",
            )
            transformed_channels = (
                "facebook.docx",
                "seo.docx",
                "image_prompt.docx",
                "video_prompt.docx",
            )
            for filename in transformed_channels:
                for label in forbidden:
                    self.assertNotIn(label, documents[filename], filename)
            self.assertIn("Hook", documents["facebook.docx"])
            self.assertIn("Real shop scenario", documents["facebook.docx"])
            self.assertIn("Root cause analysis", documents["facebook.docx"])
            self.assertIn("Practical solution", documents["facebook.docx"])
            self.assertIn("Lesson learned", documents["facebook.docx"])
            self.assertIn("Call To Action", documents["facebook.docx"])
            for label in (
                "H1:",
                "Introduction",
                "H2: Root Causes",
                "H2: Inspection",
                "H2: Repair",
                "H2: Acceptance",
                "H2: Prevention",
                "FAQ",
                "Summary",
            ):
                self.assertIn(label, documents["seo.docx"])
            self.assertTrue(documents["image_prompt.docx"].startswith("subject -"))
            for label in ("scene -", "camera -", "lighting -", "composition -", "materials -", "motion -", "negative prompt -"):
                self.assertIn(label, documents["image_prompt.docx"])
            for label in ("Opening Hook:", "Failure:", "Diagnosis:", "Repair:", "Verification:", "Ending:"):
                self.assertIn(label, documents["video_prompt.docx"])
            joined_documents = "\n".join(documents.values())
            self.assertIn("HGPT Steel", joined_documents)
            self.assertNotIn("marketing copy", joined_documents.lower())
            self.assertNotIn("Kịch bản video ngắn", joined_documents)
            self.assertNotIn("Tóm tắt tối ưu tìm kiếm", joined_documents)
            self.assertNotIn("draft_record", ai.user_prompt)
            self.assertIn("Chief Mechanical Engineer of HGPT Steel", ai.system_prompt)
            self.assertIn("Root causes must have at least 3 items", ai.user_prompt)
            self.assertIn("Không đủ dữ liệu để kết luận. Cần đo...", ai.user_prompt)
            self.assertIn("topic_intent", ai.user_prompt)
            self.assertIn("content_contract_for_topic_type", ai.user_prompt)

    def test_semantic_failure_returns_safe_limitation_record_and_seven_docs(self):
        topic = "Bảo trì tự quản"
        topic_engine = TopicIntelligenceEngine()
        ai = FakeAI(
            AIResponse(
                provider="Gemini",
                model="gemini-test",
                content=record_payload(topic),
                metadata={"status_code": 200},
            )
        )
        pipeline = EngineeringGenerationPipeline(ai=ai)

        record, documents = pipeline.generate_documents(
            topic=topic,
            context="",
            knowledge_items=[],
            topic_context=topic_engine.analyze(topic),
        )

        self.assertTrue(record.safe_failure)
        self.assertEqual(record.topic_type, "MANAGEMENT_METHOD")
        self.assertEqual(len(documents), 7)
        self.assertIn("Safe limitation record", pipeline.error)
        self.assertIn("Không đủ dữ liệu để kết luận", "\n".join(record.missing_information))

    def test_provider_failure_returns_safe_limitation_documents(self):
        topic_engine = TopicIntelligenceEngine()
        pipeline = EngineeringGenerationPipeline(
            ai=FakeAI(
                AIProviderError(
                    provider="Gemini",
                    model="gemini-test",
                    message="Gemini HTTP error 429.",
                    error_type="http_error",
                    metadata={"status_code": 429},
                )
            )
        )

        record, documents = pipeline.generate_documents(
            topic="Bơm thủy lực bị mất áp",
            context="",
            knowledge_items=[],
            topic_context=topic_engine.analyze("Bơm thủy lực bị mất áp"),
        )

        self.assertTrue(pipeline.engineering_record_created)
        self.assertTrue(record.safe_failure)
        self.assertEqual(pipeline.engineering_record_source, "SAFE_LIMITATION_RECORD")
        self.assertEqual(len(documents), 7)
        self.assertFalse(pipeline.docx_created)
        self.assertEqual(pipeline.http_status, "429")
        self.assertIn("Safe limitation record", pipeline.error)

    def test_production_failure_creates_zero_docx(self):
        import hgpt_ai_os.production as production

        with tempfile.TemporaryDirectory() as tmpdir:
            output_root = Path(tmpdir)
            with patch.object(production, "OUTPUT_ROOT", output_root), patch.object(
                production,
                "EngineeringGenerationPipeline",
                lambda: EngineeringGenerationPipeline(
                    ai=FakeAI(
                        AIProviderError(
                            provider="Gemini",
                            model="gemini-test",
                            message="Gemini request timed out.",
                            error_type="timeout",
                        )
                    )
                ),
            ):
                production.build_outputs(
                    1,
                    "Vòng bi động cơ bị kêu",
                    open_output_folder=False,
                )

            self.assertEqual(len(list(output_root.rglob("*.docx"))), 7)


if __name__ == "__main__":
    unittest.main()
