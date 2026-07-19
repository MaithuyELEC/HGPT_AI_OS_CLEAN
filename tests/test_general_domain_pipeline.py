from __future__ import annotations

import unittest

from hgpt_ai_os.content.export.docx_exporter import DocxExporter
from hgpt_ai_os.content.factory.builder_factory import BuilderFactory
from hgpt_ai_os.content.factory.general_domain import GeneralDomainRouter
from hgpt_ai_os.content.factory.topic_aware import TopicClassifier


class GeneralDomainPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.exporter = DocxExporter()
        self.general_topics = (
            "Cách chăm sóc mai",
            "Giảm cân",
            "Cách mở quán cafe",
            "Học tiếng Nhật N5",
            "Husky",
            "Nấu bò kho",
            "Dạy con học",
            "Quản lý tài chính cá nhân",
            "Trồng rau sạch",
            "Du lịch Đà Lạt",
        )
        self.mechanical_topics = (
            "Cáp cẩu trục bị đứt",
            "Rỗ khí SAW",
            "PLC Fault",
            "VFD Overcurrent",
            "Motor Burnout",
            "Hydraulic Leak",
            "Gearbox Failure",
            "Bearing Failure",
        )
        self.channels = ("facebook", "tiktok", "seo", "image", "video", "hashtags", "approval")
    def test_general_acceptance_topics_return_supported_content(self) -> None:
        router = GeneralDomainRouter()

        for topic in self.general_topics:
            with self.subTest(topic=topic):
                outputs = {
                    channel: BuilderFactory.create(channel).build(topic)
                    for channel in self.channels
                }
                for channel, body in outputs.items():
                    self.exporter.validate_content(body)
                    if channel == "hashtags":
                        self.assertIn("#LucidAIStudio", body)
                    else:
                        self.assertIn(topic.split()[0], body)
                self.assertTrue(router.can_handle(topic) or TopicClassifier().is_out_of_scope(topic))
                self.assertIn("Prompt Gemini tạo ảnh", outputs["image"])
                self.assertIn("Prompt Veo tạo video", outputs["video"])
                self.assertNotEqual(outputs["facebook"], outputs["image"])
                self.assertNotEqual(outputs["facebook"], outputs["video"])

    def test_general_channels_do_not_emit_general_life_or_legacy_template_artifacts(self) -> None:
        forbidden = (
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
            "Practical actions:",
            "ngoài phạm vi",
            "Engineering Scope",
        )

        for topic in self.general_topics:
            for channel in self.channels:
                with self.subTest(topic=topic, channel=channel):
                    body = BuilderFactory.create(channel).build(topic)
                    self.exporter.validate_content(body)
                    for label in forbidden:
                        self.assertNotIn(label, body)

    def test_general_prompt_outputs_are_channel_specific(self) -> None:
        image = BuilderFactory.create("image").build("Cách chăm sóc mai")
        video = BuilderFactory.create("video").build("Du lịch Đà Lạt")

        for field in (
            "Prompt Gemini tạo ảnh",
            "Chủ thể -",
            "Bối cảnh -",
            "Hành động -",
            "Chi tiết cần tránh -",
        ):
            self.assertIn(field, image)

        for field in ("Prompt Veo tạo video", "Mở đầu -", "Cảnh một -", "Cảnh hai -", "Kết thúc -"):
            self.assertIn(field, video)

    def test_mechanical_acceptance_topics_do_not_use_general_builder(self) -> None:
        classifier = TopicClassifier()
        router = GeneralDomainRouter()

        for topic in self.mechanical_topics:
            with self.subTest(topic=topic):
                self.assertFalse(router.can_handle(topic))
                self.assertFalse(classifier.uses_general_builder(topic))


if __name__ == "__main__":
    unittest.main()
