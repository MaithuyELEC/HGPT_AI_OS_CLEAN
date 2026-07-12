from __future__ import annotations

import unittest

from hgpt_ai_os.content.export.docx_exporter import DocxExporter


class DocxExporterValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.exporter = DocxExporter()

    def test_topic_context_engineering_terms_are_valid_docx_content(self):
        content = """
        Kiểm tra cáp cẩu trục theo ISO 4309 và hồ sơ thiết bị.
        Ghi nhận Evidence bằng ảnh hiện trường, đo Broken Wires và đường kính cáp.
        Xác nhận Sheave, Drum, Wire Feed, CTWD, Stick-out và Load Test sau sửa chữa.
        Thực hiện LOTO, Release Inspection, Megger, Autotune, Over Current và IGBT khi liên quan.
        Tham chiếu AWS D1.1 cho mối hàn kết cấu phụ trợ.
        """

        self.exporter.validate_content(content)

    def test_template_leakage_labels_are_rejected(self):
        forbidden_labels = (
            "Story",
            "Pain",
            "Truth",
            "Hook",
            "Curiosity",
            "Practical actions",
        )

        for label in forbidden_labels:
            with self.subTest(label=label):
                with self.assertRaisesRegex(ValueError, "forbidden English text"):
                    self.exporter.validate_content(f"{label}: leaked template text")

    def test_broken_vietnamese_validation_still_blocks_corruption(self):
        with self.assertRaisesRegex(ValueError, "broken Vietnamese text"):
            self.exporter.validate_content("Nội dung bị lỗi b ng ch ng trong DOCX.")


if __name__ == "__main__":
    unittest.main()
