from __future__ import annotations

from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call
from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import playbook_for_reasoning, sanitize_user_output


def _image_details(key: str) -> tuple[str, str, str, str]:
    if key == "COMPRESSOR_LOW_PRESSURE":
        return (
            "máy nén khí công nghiệp, đồng hồ áp, lọc gió, lọc tách dầu, van và đường ống khí có điểm rò được đánh dấu",
            "phòng máy nén khí trong nhà xưởng, ánh sáng rõ, có bình chứa, đường ống góp khí và khu vực cô lập an toàn",
            "kỹ thuật viên mặc PPE dùng đồng hồ áp và thiết bị dò rò kiểm tra cụm máy nén",
            "máy nén khí, đồng hồ áp, ống khí, điểm rò, lọc, van, PPE, biển LOTO, phòng máy",
        )
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
    if key == "WIRE_ROPE_FAILURE":
        return (
            "cầu trục dừng an toàn, cáp tải bị đứt sợi, puly, tang cuốn, móc cẩu và thước đo cáp",
            "xưởng cơ khí có khu vực nâng hạ được rào chắn, tải đã hạ xuống giá đỡ và treo thẻ LOTO",
            "kỹ sư bảo trì kiểm tra cáp bằng thước đo, đánh dấu sợi đứt và ghi ảnh hiện trường",
            "cầu trục, cáp tải, sợi cáp đứt, puly, tang cuốn, móc cẩu, thước đo, PPE, rào chắn",
        )
    if key == "SHOT_BLAST_IMPELLER_FAILURE":
        return (
            "máy phun bi tự động mở nắp kiểm tra, bánh văng bi, cánh đẩy gãy, lồng định hướng, tấm lót và hạt bi",
            "khu xử lý bề mặt trong xưởng thép, buồng phun đã LOTO, khay hạt bi và dụng cụ đo rung đặt bên cạnh",
            "kỹ thuật viên mặc PPE soi cánh gãy, kiểm tra bolt và chụp ảnh dạng phân bố phun",
            "bánh văng bi, cánh đẩy, lồng định hướng, tấm lót, hạt bi, dụng cụ đo rung, PPE, buồng phun",
        )
    if key == "GEARBOX_FAILURE":
        return (
            "động cơ giảm tốc, hộp giảm tốc, khớp nối, mức dầu, súng đo nhiệt và thiết bị đo rung",
            "dây chuyền cơ khí đang dừng kiểm tra, có che chắn mở an toàn và bảng ghi thông số vận hành",
            "kỹ thuật viên đo nhiệt motor và gearbox, kiểm tra dầu và đồng tâm khớp nối",
            "motor, hộp giảm tốc, dầu, khớp nối, đo nhiệt, đo rung, PPE, bệ máy",
        )
    if key == "VFD_OVERCURRENT":
        return (
            "tủ điện biến tần đang báo OC, màn hình VFD, cáp motor, ampe kìm, megger và nhãn tham số motor",
            "phòng điện công nghiệp sạch, có rào chắn điện, PPE hồ quang và sơ đồ đấu nối trên cửa tủ",
            "kỹ sư điện kiểm tra fault log, dòng motor và cáp sau khi cô lập nguồn an toàn",
            "biến tần, lỗi OC, tủ điện, cáp motor, ampe kìm, megger, PPE, sơ đồ đấu nối",
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
        trace_call("Image Prompt Writer", self, selected_topic=reasoning.topic, writer_selected=plan.channel, writer_class=self.__class__.__name__)
        playbook = playbook_for_reasoning(reasoning)
        trace_call("Selected playbook", self, selected_topic=reasoning.topic, selected_playbook=playbook.key, writer_selected=plan.channel, writer_class=self.__class__.__name__)
        subject, context, action, must_have = _image_details(playbook.key)
        visual_details = ", ".join(dict.fromkeys((*playbook.checklist_items[:6], *playbook.safety_risks[:2])))
        return sanitize_user_output("\n".join(
            [
                "Prompt Gemini tạo ảnh",
                f"Chủ thể: {subject}",
                f"Bối cảnh: {context}",
                f"Hành động: {action}",
                "Trang phục: bảo hộ lao động đúng xưởng, găng tay, kính, giày an toàn, dáng đứng tập trung vào thao tác thật",
                "Ánh sáng: ánh sáng xưởng tự nhiên, rõ chi tiết kim loại, thấy texture bề mặt, không tối, không cháy sáng",
                "Góc máy: ngang tầm mắt kết hợp cận cảnh chi tiết lỗi và thao tác kiểm tra, có chiều sâu foreground-middle-background",
                "Ống kính: 35mm cho bối cảnh, 85mm hoặc macro cho chi tiết kỹ thuật",
                "Màu sắc: chân thực, thép và dụng cụ đúng màu, tương phản vừa phải, không dùng màu hoạt hình",
                f"Chi tiết cần có: {must_have}",
                f"Chi tiết hiện trường: {visual_details}",
                "Chuyển động: bụi kim loại nhẹ, giấy checklist hơi rung, kỹ thuật viên đang đặt dụng cụ đo, máy ở trạng thái an toàn",
                "Bố cục: điểm lỗi, tay thao tác và thiết bị chính cùng nằm trong một câu chuyện thị giác rõ ràng",
                "Chi tiết cần tránh: chữ phủ vô nghĩa, tay méo, thiết bị phi thực tế, tư thế mất an toàn, cảnh quá sạch như showroom",
                "Phong cách chất lượng: ảnh tư liệu công nghiệp sắc nét, thực tế, có chiều sâu, không CGI rẻ tiền",
                "Tỷ lệ khung hình: 4:5 hoặc 16:9",
            ]
        ))


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, ImagePromptWriter)
