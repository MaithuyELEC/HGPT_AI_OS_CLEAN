from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import playbook_for_reasoning


def _image_details(key: str) -> tuple[str, str, str, str]:
    if key == "SAW_POROSITY":
        return (
            "dây chuyền hàn SAW, xe hàn, lớp thuốc hàn, đường hàn có rỗ khí, mũ hàn và đầu dò UT",
            "xưởng kết cấu thép có dầm thép lớn, khu kiểm tra VT/UT và vật tư hàn được che ẩm",
            "kỹ sư QA/QC cùng thợ hàn kiểm tra đường hàn, đối chiếu WPS và đánh dấu vùng sửa",
            "lớp thuốc, thuốc hàn, đường hàn, xe hàn, rỗ khí, mũ hàn, bảo hộ, xưởng kết cấu thép",
        )
    if key == "POWER_TOOL_BREAKDOWN":
        return (
            "bàn bảo trì có máy mài cầm tay, chổi than, bạc đạn, bụi mài, rotor/stator và đồng hồ đo",
            "xưởng thép với bảng dụng cụ 5S, khu sửa dụng cụ điện và biển an toàn",
            "kỹ thuật viên mặc bảo hộ tháo kiểm tra máy mài, vệ sinh bụi và ghi nhãn tình trạng",
            "bàn bảo trì, máy mài, chổi than, bạc đạn, bụi, rotor/stator, kỹ thuật viên, bảo hộ, bảng dụng cụ 5S, xưởng thép",
        )
    if key == "LASER_5S":
        return (
            "bàn cắt laser, phôi thép, chi tiết thành phẩm có nhãn, thùng phế và bảng dụng cụ",
            "khu máy cắt laser sạch, có vạch sàn, luồng vật tư một chiều và dòng chảy 5S rõ ràng",
            "tổ sản xuất phân loại phôi, dán nhãn thành phẩm và dọn phế cuối ca",
            "bàn cắt laser, phôi, chi tiết thành phẩm có nhãn, thùng phế, bảng dụng cụ, vạch sàn, dòng chảy 5S",
        )
    if key == "PAINT_PEELING":
        return (
            "cấu kiện thép có vùng sơn bong, mẫu nhám bề mặt, máy đo DFT và dụng cụ kiểm tra bám dính",
            "khu phun bi/sơn có ánh sáng rõ, bề mặt thép đã khoanh vùng lỗi và hồ sơ kiểm tra",
            "người kiểm tra đo DFT, soi nhám bề mặt và đánh dấu vùng cần xử lý lại",
            "cấu kiện thép, sơn bong, nhám bề mặt, máy đo DFT, người kiểm tra, khu phun bi/sơn",
        )
    return (
        "khu vực sản xuất liên quan, thiết bị chính, dấu hiệu lỗi và dụng cụ kiểm tra",
        "xưởng thật, có công nhân, kỹ sư và hồ sơ nghiệm thu",
        "đội sản xuất kiểm tra nguyên nhân và thực hiện hành động khắc phục",
        "thiết bị, dấu hiệu lỗi, kiểm tra, bảo hộ, hồ sơ nghiệm thu",
    )


class ImagePromptWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        playbook = playbook_for_reasoning(reasoning)
        subject, context, action, must_have = _image_details(playbook.key)
        return "\n".join(
            [
                "Prompt Gemini tạo ảnh",
                f"Chủ thể: {subject}",
                f"Bối cảnh: {context}",
                f"Hành động: {action}",
                "Trang phục: bảo hộ lao động đúng xưởng, găng tay, kính, giày an toàn, không tạo dáng quảng cáo",
                "Ánh sáng: ánh sáng xưởng tự nhiên, rõ chi tiết kim loại, không tối, không cháy sáng",
                "Góc máy: ngang tầm mắt kết hợp cận cảnh chi tiết lỗi và thao tác kiểm tra",
                "Ống kính: 35mm cho bối cảnh, 85mm cho chi tiết kỹ thuật",
                "Màu sắc: chân thực, thép và dụng cụ đúng màu, không dùng màu hoạt hình",
                f"Chi tiết cần có: {must_have}",
                "Chi tiết cần tránh: chữ sai tiếng Việt, tay méo, thiết bị phi thực tế, biểu đồ giả, tư thế mất an toàn",
                "Phong cách chất lượng: ảnh tư liệu công nghiệp sắc nét, thực tế, có chiều sâu",
                "Tỷ lệ khung hình: 4:5 hoặc 16:9",
            ]
        )
