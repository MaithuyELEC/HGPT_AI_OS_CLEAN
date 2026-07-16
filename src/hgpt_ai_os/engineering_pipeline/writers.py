from __future__ import annotations

import ast
import json
import re
import unicodedata
from collections.abc import Iterable

from .record import EngineeringRecord


_FIELD_LABELS = {
    "cause": "Nguyên nhân",
    "category": "Nhóm lỗi",
    "symptoms": "Dấu hiệu",
    "failure_symptom": "Dấu hiệu",
    "mechanism": "Cơ chế hư hỏng",
    "physical_mechanism": "Cơ chế hư hỏng",
    "inspection": "Cách kiểm tra",
    "inspection_method": "Cách kiểm tra",
    "measurements": "Đo kiểm",
    "measurement": "Đo kiểm",
    "tools": "Dụng cụ",
    "instruments": "Dụng cụ",
    "expected_values": "Giá trị đối chiếu",
    "decision_logic": "Logic quyết định",
    "repair": "Cách xử lý",
    "repair_procedure": "Cách xử lý",
    "verification": "Xác nhận sau sửa",
    "acceptance": "Tiêu chí bàn giao",
    "acceptance_criteria": "Tiêu chí bàn giao",
    "prevention": "Phòng ngừa",
    "preventive_maintenance": "Phòng ngừa",
}

_INTERNAL_KEYS = {
    "failure_modes",
    "root_causes",
    "recommended_actions",
    "inspection_steps",
    "preventive_actions",
    "safety_notes",
    "tools_required",
    "source_keys",
    "confidence",
}

_ALLOWED_ENGLISH_TERMS = {
    "ISO",
    "IEC",
    "AWS",
    "API",
    "LOTO",
    "NDT",
    "VFD",
    "OEM",
    "QA",
    "QC",
    "CMMS",
    "SCADA",
}

_ENGLISH_LEAKAGE_TERMS = {
    "provider",
    "prompt",
    "json",
    "dict",
    "list",
    "repr",
    "generic",
    "management",
    "marketing",
    "facebook",
    "tiktok",
    "hashtag",
    "blog",
    "chatgpt",
}

_GENERIC_FIELD_FALLBACKS = {
    "domain": "Bảo trì kỹ thuật",
    "title": "Hồ sơ xử lý sự cố kỹ thuật",
    "problem": "Sự cố cần được xác nhận bằng dữ liệu hiện trường trước khi kết luận.",
    "equipment": "thiết bị/khu vực theo hồ sơ kỹ thuật",
    "subsystem": "cụm chức năng cần kiểm tra",
    "component": "chi tiết liên quan cần xác nhận",
    "failure_symptom": "triệu chứng bất thường cần ghi nhận tại hiện trường",
    "operating_context": "bối cảnh vận hành cần được mô tả bằng dữ liệu hiện trường.",
    "working_principle": "nguyên lý làm việc cần được đối chiếu với tài liệu kỹ thuật.",
    "failure_mechanisms": "cơ chế hư hỏng cần được xác nhận bằng kiểm tra và đo kiểm.",
    "root_causes": "nguyên nhân gốc cần được khoanh vùng bằng bằng chứng đo kiểm.",
    "evidence_required": "bằng chứng hiện trường trước và sau sửa",
    "inspection_procedure": "kiểm tra hiện trường theo phiếu kiểm đã phê duyệt",
    "measurements": "thông số đo cần ghi lại trước và sau sửa",
    "tools_required": "dụng cụ đo kiểm phù hợp với thiết bị",
    "decision_logic": "nếu dữ liệu đo chưa đủ thì chưa kết luận nguyên nhân.",
    "repair_procedure": "thực hiện sửa chữa theo kết quả kiểm tra và hướng dẫn kỹ thuật.",
    "verification": "xác nhận sau sửa bằng cùng phương pháp đo kiểm ban đầu.",
    "acceptance_criteria": "chỉ bàn giao khi có đủ bằng chứng đạt yêu cầu.",
    "lessons_learned": "chuyển sự cố thành điểm kiểm soát trong bảo trì định kỳ.",
    "common_mistakes": "không kết luận khi thiếu dữ liệu đo kiểm.",
    "preventive_maintenance": "cập nhật kế hoạch bảo trì dựa trên bằng chứng lỗi.",
    "safety_controls": "cô lập năng lượng và kiểm soát an toàn trước khi thao tác.",
    "kaizen": "chuẩn hóa điểm đo và biểu mẫu ghi nhận cho lần kiểm tra sau.",
    "digital_factory_recommendations": "lưu dữ liệu đo, ảnh hiện trường và kết luận vào hệ thống quản lý bảo trì.",
    "applicable_standards": "chỉ sử dụng tiêu chuẩn đã được xác nhận.",
    "missing_information": "Không đủ dữ liệu để kết luận. Cần đo và bổ sung bằng chứng hiện trường.",
}

_GENERIC_TERM_REPLACEMENTS = (
    ("AI provider", "nguồn dữ liệu kỹ thuật"),
    ("AI Provider", "nguồn dữ liệu kỹ thuật"),
    ("provider", "nguồn dữ liệu"),
    ("Maintenance", "Bảo trì"),
    ("maintenance", "bảo trì"),
    ("Checklist", "Phiếu kiểm"),
    ("checklist", "phiếu kiểm"),
    ("OEM manual", "tài liệu hãng sản xuất"),
    ("OEM", "hãng sản xuất"),
    ("QA/QC", "kiểm soát chất lượng"),
    ("CMMS", "hệ thống quản lý bảo trì"),
    ("SCADA", "hệ thống giám sát điều khiển"),
    ("Digital Factory", "Nhà máy số"),
    ("digital factory", "nhà máy số"),
    ("measured in", "đơn vị"),
    ("post-repair", "sau sửa"),
)


def render_all(record: EngineeringRecord) -> dict[str, str]:
    rendered = _RenderedRecord(record)
    return {
        "facebook.docx": render_facebook(rendered),
        "tiktok.docx": render_tiktok(rendered),
        "image_prompt.docx": render_image_prompt(rendered),
        "video_prompt.docx": render_video_prompt(rendered),
        "seo.docx": render_seo(rendered),
        "hashtags.docx": render_hashtags(rendered),
        "approval_checklist.docx": render_checklist(rendered),
    }


def render_facebook(record: "_RenderedRecord") -> str:
    return _render_knowledge_reference(record, "Hồ sơ kỹ thuật hiện trường", "dùng cho tổ bảo trì, QA/QC và ca sản xuất")


def render_tiktok(record: "_RenderedRecord") -> str:
    return _render_knowledge_reference(record, "Bài học kỹ thuật đầu ca", "dùng để huấn luyện nhanh trước khi thao tác")


def render_image_prompt(record: "_RenderedRecord") -> str:
    equipment = ", ".join(record.equipment[:4]) or record.domain
    components = ", ".join(record.component[:5]) or "cụm chi tiết liên quan"
    symptoms = ", ".join(record.failure_symptom[:4]) or record.problem
    measurements = ", ".join(record.measurements[:4]) or "thông số đo tại hiện trường"
    tools = ", ".join(record.tools_required[:6]) or "dụng cụ đo, phiếu kiểm, nhãn khóa an toàn"
    inspection = ", ".join(record.inspection_procedure[:4]) or "kiểm tra trực quan và đo kiểm theo phiếu kiểm"
    repair = ", ".join(record.repair_procedure[:3]) or "xử lý nguyên nhân, kiểm tra lại và bàn giao có kiểm soát"
    safety = ", ".join(record.safety_controls[:4]) or "cô lập năng lượng, rào chắn và PPE đầy đủ"
    missing = ", ".join(record.missing_information[:3]) or "không bịa số đo, nhãn, giá trị hoặc tiêu chuẩn khi hồ sơ chưa cung cấp"
    return "\n".join(
        [
            "## Prompt hình ảnh kỹ thuật",
            "",
            f"Mục tiêu hình ảnh: tạo ảnh tài liệu công nghiệp cho chủ đề {record.topic}, giúp kỹ sư HGPT Steel nhìn đúng đối tượng, bằng chứng kỹ thuật, thao tác kiểm tra và trạng thái an toàn; ảnh không được biến chủ đề này thành thiết bị hoặc lỗi khác.",
            f"Chủ thể chính: kỹ sư bảo trì hoặc QA/QC đang xử lý {record.main_entity or record.topic}; nét mặt tập trung, thao tác tự nhiên, ghi nhận bằng chứng thay vì tạo dáng quảng cáo.",
            f"Thiết bị/cấu kiện chính: {equipment}; thể hiện rõ {components}, đúng bối cảnh nhà máy kết cấu thép, không thay bằng máy dân dụng hoặc thiết bị không liên quan.",
            f"Hiện tượng kỹ thuật cần thể hiện: {symptoms}; nếu hiện tượng chưa đo được thì thể hiện hành động kiểm chứng thay vì bịa số đo.",
            f"Hành động kiểm tra hoặc sửa chữa: {inspection}; sau đó thể hiện logic {repair} ở mức trực quan, có kiểm soát hiện trường.",
            f"Dụng cụ đo kiểm: {tools}; mặt đồng hồ hoặc màn hình chỉ được gợi ý trạng thái đo, không hiển thị giá trị cụ thể khi hồ sơ chưa cung cấp.",
            "PPE: mũ bảo hộ, kính bảo hộ, găng tay đúng thao tác, giày an toàn, áo phản quang hoặc đồng phục xưởng; PPE phải khớp rủi ro điện, thủy lực, khí nén, hàn, cắt, nhiệt hoặc nâng hạ nếu có.",
            "Bối cảnh nhà xưởng kết cấu thép: nền bê tông có vạch phân luồng, bảng 5S, tủ dụng cụ, tủ điện, pallet vật tư, dầm thép, khu vực hàn/cắt/sơn hoặc bảo trì đúng ngữ cảnh.",
            "Tiền cảnh: điểm bất thường, dụng cụ đo, phiếu kiểm hoặc tag LOTO nằm rõ trong khung; không để chữ hoặc tay che mất bằng chứng kỹ thuật.",
            "Trung cảnh: 1-2 kỹ thuật viên Việt Nam thao tác đúng quy trình, một người đo hoặc quan sát, một người ghi nhận hồ sơ, khoảng cách an toàn được giữ rõ.",
            "Hậu cảnh: dây chuyền hoặc khu vực sản xuất kết cấu thép đang được kiểm soát, có biển cảnh báo, kệ dụng cụ và hồ sơ hiện trường nhưng không lấn át chủ thể.",
            "Góc máy: góc 3/4 ngang tầm ngực, có thêm insert macro cho chi tiết kỹ thuật; bố cục phải cho thấy quan hệ giữa người, thiết bị, dụng cụ đo và vùng nguy hiểm.",
            "Tiêu cự: góc tài liệu công nghiệp cho cảnh chính, macro cho chi tiết; độ sâu trường ảnh vừa phải để thiết bị chính rõ nhưng vẫn đọc được bối cảnh nhà máy.",
            "Bố cục: rule of thirds, nhiều lớp tiền cảnh - trung cảnh - hậu cảnh, đường nhìn đi từ tay kỹ thuật viên tới điểm kiểm tra; ảnh phải dùng được cho bài kỹ thuật, không giống ảnh stock chung chung.",
            "Ánh sáng: ánh sáng nhà xưởng chân thực, có thể bổ sung đèn kiểm tra cầm tay, highlight mềm trên kim loại, không tối, không cháy sáng, không dùng neon hoặc ánh sáng sân khấu.",
            "Chất liệu bề mặt: thép sơn công nghiệp, kim loại xước nhẹ, cao su, dây cáp, ống dầu/khí, bụi kim loại hoặc dầu mỡ đúng mức; texture PPE và giấy checklist rõ.",
            f"Dấu hiệu kỹ thuật nhìn thấy: {measurements}; nếu cần giá trị thì ghi chú {missing}.",
            f"Yêu cầu an toàn: {safety}; thể hiện LOTO, rào chắn, biển cảnh báo, khoảng cách an toàn và trạng thái máy/cấu kiện đã được kiểm soát.",
            "Đồng phục HGPT Steel: logo nhỏ, sạch, chuyên nghiệp trên mũ, áo hoặc clipboard; chữ ít, rõ, không che chi tiết kỹ thuật.",
            "Phong cách ảnh: photorealistic industrial documentary, cảm giác ảnh hiện trường thật trong nhà máy kết cấu thép, sắc nét ở bằng chứng kỹ thuật.",
            "Nội dung loại trừ cho prompt: chữ sai tiếng Việt, chữ méo, số đo bịa, tiêu chuẩn giả, màn hình vô nghĩa, thiết bị sai ngành, thao tác mất an toàn, thiếu PPE, bypass liên động, tay thừa, mặt biến dạng, watermark, logo lạ, cảnh showroom quá sạch, hoạt hình, CGI, blur, overexposed, underexposed, nội dung trái với chủ đề.",
            f"Đây là gì? {record.topic} trong bối cảnh {equipment}.",
            f"Vì sao xảy ra? {_first(record.root_causes, 'cần khóa nguyên nhân bằng bằng chứng đo kiểm')}",
            f"Cần bằng chứng gì trước khi kết luận? {', '.join(record.evidence_required[:3]) or 'ảnh hiện trường, số đo và hồ sơ kỹ thuật liên quan'}.",
        ]
    )


def render_video_prompt(record: "_RenderedRecord") -> str:
    equipment = ", ".join(record.equipment[:4]) or record.domain
    symptoms = ", ".join(record.failure_symptom[:4]) or record.problem
    inspection = ", ".join(record.inspection_procedure[:4]) or "kiểm tra trực quan và đo kiểm tại hiện trường"
    measurements = ", ".join(record.measurements[:4]) or "thông số đo trước và sau sửa"
    tools = ", ".join(record.tools_required[:5]) or "dụng cụ đo, phiếu kiểm và nhãn khóa an toàn"
    repair = ", ".join(record.repair_procedure[:4]) or "sửa đúng nguyên nhân và kiểm tra lại"
    verification = ", ".join(record.verification[:4]) or "xác nhận lại bằng cùng phương pháp phát hiện lỗi"
    safety = ", ".join(record.safety_controls[:4]) or "cô lập năng lượng, rào chắn và PPE đầy đủ"
    return "\n".join(
        [
            "## Prompt video kỹ thuật",
            "",
            f"Mục tiêu video: video tài liệu công nghiệp cho {record.topic}, cho thấy đúng chủ thể {record.main_entity or equipment}, bằng chứng kỹ thuật, hành động an toàn và kết quả kiểm chứng; không biến thành slideshow hoặc quảng cáo.",
            "Thời lượng: đúng 10 giây.",
            "Nhân vật: 1 người vận hành và 1 kỹ sư bảo trì/QA/QC Việt Nam, thao tác tự nhiên, không nhìn camera, ưu tiên ghi bằng chứng hơn diễn xuất.",
            "PPE continuity: mũ, kính, găng, giày an toàn, áo phản quang hoặc đồng phục xưởng phải xuất hiện liên tục; PPE thay đổi theo rủi ro điện, thủy lực, khí nén, hàn, cắt, nhiệt hoặc nâng hạ.",
            f"Thiết bị/cấu kiện: {equipment}; quay đúng {record.main_entity or record.topic}, chi tiết {', '.join(record.component[:4]) or 'liên quan đến chủ đề'}, không dùng thiết bị khác ngành.",
            f"0-2 giây: Hook - cận cảnh {symptoms} hoặc điểm cần kiểm chứng; người vận hành dừng thao tác, chỉ vị trí bất thường, âm thanh xưởng giảm nhẹ để người xem chú ý.",
            f"2-5 giây: Evidence/diagnosis - kỹ sư cô lập khu vực, dùng {tools} để thực hiện {inspection}; camera thấy phiếu kiểm, tag LOTO hoặc dụng cụ đo nhưng không bịa số đo.",
            f"5-8 giây: Correct action - thực hiện {repair}; thao tác ngắn, đúng trình tự, không bypass liên động, không đặt tay vào vùng kẹp/cắt/nóng/đang có năng lượng.",
            f"8-10 giây: Result/closing - xác nhận {verification}; quay hồ sơ ghi nhận và khu vực được trả lại trạng thái an toàn có kiểm soát.",
            "Camera movement: handheld ổn định kiểu documentary, push-in nhanh vào chi tiết lỗi, macro insert cho dụng cụ đo, over-the-shoulder khi đọc checklist, pull-back cuối để thấy khu vực an toàn.",
            f"Equipment movement: chỉ cho chuyển động nếu đã an toàn; nếu cần chạy thử thì thể hiện trạng thái kiểm soát và khoảng cách an toàn theo {safety}.",
            "Worker actions: dừng, báo lỗi, LOTO/rào chắn, đo kiểm, ghi ảnh hiện trường, sửa đúng nguyên nhân đã xác nhận, ký hoặc tích phiếu nghiệm thu.",
            f"Voice-over: 'Với {record.topic}, đừng sửa theo cảm tính. Khóa an toàn, đo đúng điểm, xử lý đúng nguyên nhân và nghiệm thu bằng dữ liệu.'",
            "On-screen text: 'Dừng - Đo - Xử lý - Xác nhận' xuất hiện nhỏ, rõ, không che thiết bị; không hiển thị thông số khi chưa có nguồn.",
            "Ambient sound: tiếng xưởng nhẹ, tiếng dụng cụ kim loại, tiếng bíp đồng hồ đo, tiếng giấy checklist; nhạc nền thấp, nghiêm túc.",
            "Chuyển cảnh: cắt theo hành động thật ở mốc 2 giây, 5 giây, 8 giây; không dùng glitch, neon, hiệu ứng slideshow hoặc khung tĩnh kéo dài.",
            "Ánh sáng: ánh sáng nhà xưởng overhead, có thể thêm đèn kiểm tra cầm tay; màu tự nhiên, không tối, không cháy sáng.",
            "Lời kêu gọi cuối: chữ cuối nhỏ 'Lưu để dùng trong họp đầu ca' và giọng đọc kết thúc 'Có bằng chứng rồi mới bàn giao.'",
            "Nội dung loại trừ cho prompt: slideshow, ảnh tĩnh ghép lại, video dài hơn 10 giây, thiếu PPE, thao tác mất an toàn, bypass liên động, số đo bịa, tiêu chuẩn giả, thiết bị sai ngành, chữ méo, tiếng Việt sai, logo lạ, watermark, CGI rẻ, hoạt hình, camera rung mạnh, motion blur quá mức, cảnh tối, neon, quảng cáo lố.",
            f"Đây là gì? {record.topic} trong bối cảnh {equipment}.",
            f"Vì sao xảy ra? {_first(record.root_causes, 'cần khóa nguyên nhân bằng bằng chứng đo kiểm')}",
            f"Cần bằng chứng gì trước khi kết luận? {', '.join(record.evidence_required[:3]) or 'ảnh hiện trường, số đo và hồ sơ kỹ thuật liên quan'}.",
        ]
    )


def render_seo(record: "_RenderedRecord") -> str:
    slug = _slug(record.topic)
    return "\n".join(
        [
            f"## Mục lục tra cứu kỹ thuật: {record.topic}",
            "",
            f"Mã tra cứu: {slug}",
            f"Mục đích: giúp kỹ sư sau này tìm lại định nghĩa, cơ chế, bằng chứng, đo kiểm, sửa chữa, xác nhận và phòng ngừa cho {record.topic}.",
            "",
            "### Từ khóa tra cứu",
            *_bullets(
                (
                    record.topic,
                    record.domain,
                    *record.failure_symptom[:3],
                    *record.equipment[:2],
                ),
                8,
            ),
            "",
            "### Cấu trúc hồ sơ kiến thức",
            "- Định nghĩa và phạm vi áp dụng",
            "- Nguyên lý làm việc hoặc cơ chế quá trình",
            "- Hiện tượng, cơ chế lỗi và nguyên nhân gốc",
            "- Bằng chứng cần thu thập trước khi kết luận",
            "- Quy trình kiểm tra, đo kiểm, dụng cụ và logic chẩn đoán",
            "- Sửa chữa, xác nhận sau sửa, tiêu chí bàn giao và phòng ngừa tái diễn",
            "- Tiêu chuẩn áp dụng, dữ liệu còn thiếu và giả định bị cấm",
            "",
            "### Trích yếu kỹ thuật",
            *_knowledge_question_lines(record),
        ]
    )


def render_checklist(record: "_RenderedRecord") -> str:
    return "\n".join(
        [
            "## Phiếu kiểm phê duyệt kỹ thuật",
            "",
            "### Thông tin đầu vào",
            f"- Chủ đề: {record.topic}",
            f"- Lĩnh vực: {record.domain}",
            f"- Thiết bị/khu vực: {', '.join(record.equipment) or 'cần xác nhận thêm'}",
            "",
            "### Kiểm tra bắt buộc",
            *_checkboxes(record.inspection_procedure, 8),
            "",
            "### Đo kiểm và bằng chứng",
            *_checkboxes(record.measurements, 6),
            *_checkboxes(record.evidence_required, 4),
            "",
            "### Quyết định sửa chữa",
            *_checkboxes(record.decision_logic, 5),
            *_checkboxes(record.repair_procedure, 6),
            "",
            "### Xác nhận sau sửa",
            *_checkboxes(record.verification, 6),
            *_checkboxes(record.acceptance_criteria, 5),
            "",
            "### Không được quên",
            *_checkboxes(record.common_mistakes, 4),
            *_checkboxes(record.safety_controls, 4),
            "",
            "### Phụ lục tri thức bắt buộc",
            *_knowledge_question_lines(record),
        ]
    )


def render_hashtags(record: "_RenderedRecord") -> str:
    tags = tuple(
        dict.fromkeys(
            (
                "LucidAuto",
                "HGPTSteelKnowledgeBase",
                record.topic,
                record.domain,
                record.topic_type,
                record.main_entity,
                *record.equipment[:3],
                *record.component[:3],
                *record.applicable_standards[:3],
            )
        )
    )
    return "\n".join(
        [
            "## Thẻ phân loại kiến thức",
            "",
            *_bullets(tuple(tag for tag in tags if tag), 16),
            "",
            "### Phụ lục tri thức bắt buộc",
            *_knowledge_question_lines(record),
        ]
    )


def _render_knowledge_reference(record: "_RenderedRecord", title: str, audience: str) -> str:
    return "\n".join(
        [
            f"## {title}: {record.topic}",
            "",
            f"Đối tượng sử dụng: {audience}. Hồ sơ này là tài liệu kỹ thuật dài hạn cho HGPT Steel, không phải nội dung marketing hoặc câu trả lời tạm thời.",
            "",
            *_knowledge_question_lines(record),
            "",
            "### Logic quyết định tại hiện trường",
            *_bullets(record.decision_logic, 6),
            "",
            "### Bài học lưu vào tri thức nhà máy",
            *_bullets(record.lessons_learned, 5),
            *_bullets(record.common_mistakes, 4),
            "",
            "### Khuyến nghị số hóa",
            *_bullets(record.digital_factory_recommendations, 5),
        ]
    )


def _knowledge_question_lines(record: "_RenderedRecord") -> list[str]:
    standards = record.applicable_standards or ("Chưa xác nhận tiêu chuẩn áp dụng; cần đối chiếu bản vẽ, ITP, WPS, OEM manual hoặc quy định hiện hành.",)
    unknowns = record.missing_information or ("Không đủ dữ liệu để kết luận. Cần đo và bổ sung bằng chứng hiện trường trước khi chốt nguyên nhân.",)
    evidence = record.evidence_required or ("Ảnh hiện trường, log vận hành, số đo trước/sau sửa và hồ sơ kỹ thuật liên quan.",)
    return [
        "### 1. Đây là gì?",
        f"- Chủ đề: {record.topic}",
        f"- Lĩnh vực: {record.domain}",
        f"- Thiết bị/quá trình: {', '.join(record.equipment) or record.main_entity or 'cần xác nhận từ hồ sơ kỹ thuật'}",
        "",
        "### 2. Vì sao xảy ra?",
        *_bullets(record.root_causes, 5),
        "",
        "### 3. Cơ chế hoạt động hoặc cơ chế lỗi",
        f"- Nguyên lý: {record.working_principle}",
        *_bullets(record.failure_mechanisms, 5),
        "",
        "### 4. Kiểm tra như thế nào?",
        *_bullets(record.inspection_procedure, 8),
        "",
        "### 5. Đo kiểm gì?",
        *_bullets(record.measurements, 8),
        *_bullets(record.tools_required, 6),
        "",
        "### 6. Chẩn đoán như thế nào?",
        *_bullets(record.decision_logic, 6),
        "",
        "### 7. Sửa chữa như thế nào?",
        *_bullets(record.repair_procedure, 8),
        "",
        "### 8. Xác nhận và nghiệm thu như thế nào?",
        *_bullets(record.verification, 6),
        *_bullets(record.acceptance_criteria, 6),
        "",
        "### 9. Ngăn tái diễn như thế nào?",
        *_bullets(record.preventive_maintenance, 6),
        *_bullets(record.kaizen, 4),
        "",
        "### 10. Tiêu chuẩn nào áp dụng?",
        *_bullets(standards, 6),
        "",
        "### 11. Thông tin nào còn thiếu?",
        *_bullets(unknowns, 6),
        "",
        "### 12. Cần bằng chứng gì trước khi kết luận?",
        *_bullets(evidence, 6),
        "",
        "### 13. Kiểm soát an toàn",
        *_bullets(record.safety_controls, 6),
    ]


def _bullets(values: tuple[str, ...], limit: int) -> list[str]:
    return [f"- {value}" for value in values[:limit] if value]


def _checkboxes(values: tuple[str, ...], limit: int) -> list[str]:
    return [f"- ☐ {value}" for value in values[:limit] if value]


def _first(values: tuple[str, ...], fallback: str) -> str:
    return values[0] if values else fallback


def _slug(value: str) -> str:
    words = re.findall(r"[a-z0-9]+", _ascii_words(value))
    return "-".join(words[:8]) or "engineering-record"


def _hashtag(value: str) -> str:
    words = re.findall(r"[a-z0-9]+", _ascii_words(value))
    if not words:
        return ""
    return "#" + "".join(word.capitalize() for word in words[:5])


def _ascii_words(value: str) -> str:
    value = value.replace("Đ", "D").replace("đ", "d")
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char)).lower()


def _generic_fallback(field: str) -> str:
    return _GENERIC_FIELD_FALLBACKS.get(field, "")


def _has_unapproved_english(text: str) -> bool:
    for word in re.findall(r"\b[A-Za-z]{3,}\b", text):
        normalized = word.upper()
        if normalized in _ALLOWED_ENGLISH_TERMS:
            continue
        if word.lower() in _ENGLISH_LEAKAGE_TERMS:
            return True
    return False


class _RenderedRecord:
    _FIELDS = EngineeringRecord.__dataclass_fields__

    def __init__(self, record: EngineeringRecord) -> None:
        self._record = record

    def __getattr__(self, name: str):
        value = getattr(self._record, name)
        if name not in self._FIELDS:
            return value
        if isinstance(value, tuple):
            items = _items(value, field=name)
            return items
        if isinstance(value, str):
            text = _clean_text(value)
            return _generic_fallback(name) if _has_unapproved_english(text) else text
        return value


def _items(values: Iterable[object], limit: int | None = None, field: str = "") -> tuple[str, ...]:
    items: list[str] = []
    for value in values:
        items.extend(_flatten_value(value, field=field))
        if limit is not None and len(items) >= limit:
            break
    return tuple(dict.fromkeys(item for item in items if item))[:limit]


def _flatten_value(value: object, field: str = "") -> list[str]:
    if value is None:
        return []
    parsed = _parse_structured_text(value) if isinstance(value, str) else value
    if parsed is None:
        return []
    if isinstance(parsed, dict):
        text = _render_mapping(parsed)
        return [text] if text else []
    if isinstance(parsed, (list, tuple, set)):
        items: list[str] = []
        for item in parsed:
            items.extend(_flatten_value(item, field=field))
        return items
    text = _clean_text(str(parsed))
    if _has_unapproved_english(text):
        fallback = _generic_fallback(field)
        return [fallback] if fallback else []
    return [text]


def _render_mapping(values: dict[object, object]) -> str:
    parts: list[str] = []
    for raw_key, raw_value in values.items():
        key = _clean_key(raw_key)
        if not key or key in _INTERNAL_KEYS:
            continue
        label = _FIELD_LABELS.get(key)
        if not label:
            continue
        value = "; ".join(_flatten_value(raw_value, field=key))
        if value:
            parts.append(f"{label}: {value}")
    return ". ".join(parts)


def _parse_structured_text(value: str) -> object:
    text = value.strip()
    if not text:
        return None
    if text[:1] not in "{[":
        return text
    for parser in (json.loads, ast.literal_eval):
        try:
            return parser(text)
        except (ValueError, SyntaxError, TypeError, json.JSONDecodeError):
            continue
    return text


def _clean_key(value: object) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", str(value).strip().lower()).strip("_")


def _clean_text(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    if text[:1] in "{[":
        parsed = _parse_structured_text(text)
        if parsed is not text:
            return "; ".join(_flatten_value(parsed))
    text = _strip_internal_key_prefix(text)
    for source, target in sorted(_GENERIC_TERM_REPLACEMENTS, key=lambda item: len(item[0]), reverse=True):
        text = re.sub(re.escape(source), target, text, flags=re.IGNORECASE)
    text = re.sub(r"\bif\b", "nếu", text, flags=re.IGNORECASE)
    text = re.sub(r"\bthen\b", "thì", text, flags=re.IGNORECASE)
    text = re.sub(r"(?m)^\s*\d+\.\s*", "", text)
    text = re.sub(r"\b(?:dict|list|repr|json\.dumps|str\s*\()\b", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" ;,.")


def _strip_internal_key_prefix(text: str) -> str:
    key_match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*(.+)$", text)
    if not key_match:
        return text
    key = _clean_key(key_match.group(1))
    if key in _INTERNAL_KEYS or key in _FIELD_LABELS:
        return key_match.group(2).strip()
    return text
